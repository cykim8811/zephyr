
import base64
from PIL import Image, ImageDraw, ImageFont
import math
from io import BytesIO
from openai import AsyncOpenAI
import dotenv
import json

dotenv.load_dotenv()

client = AsyncOpenAI()

padding = 0.1

def preprocess2(image: Image, total_width) -> Image:
    grid_x_num = 10
    grid_y_num = math.ceil(image.height / image.width * grid_x_num)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    width, height = image.size

    for i in range(grid_x_num + 1):
        x = (width - 2) * i // grid_x_num
        draw.line([(x, 0), (x, height)], fill=(0, 0, 255, 255), width=2)

    for i in range(grid_y_num + 1):
        y = (height - 2) * i // grid_y_num
        draw.line([(0, y), (width, y)], fill=(0, 0, 255, 255), width=2)

    for ix in range(grid_x_num):
        for iy in range(grid_y_num):
            text = f"{chr(ord('A') + ix)}{iy + 1}"
            font = ImageFont.load_default().font_variant(size=round(64 * image.width / total_width))
            _, _, text_width, text_height = font.getbbox(text)
            x = (width - 2) * (ix + 0.5) // grid_x_num - text_width // 2
            y = (height - 2) * (iy + 0.5) // grid_y_num - text_height // 2
            draw.text((x, y), text, fill=(0, 0, 255, 96), font=font)

    return Image.alpha_composite(image, overlay)


system_prompt2 = """
# 역할
문제 풀이의 위치와, 오류 여부를 분석하여야 한다.

# 문제
{problem}

# 단계
{process}

# 사용된 스킬
{skill}

# 텍스트 추정 (정확도 낮음)
{estimate}

# 지침
- 답안의 위치를 찾아내고, 스킬을 기반으로 해당 풀이가 올바른지 판단하여라.
- 해당 식과 겹치는 모든 박스의 라벨을 기록하여라. 순서는 상관없다.
ex) D5, C5, D4, G5, E5, F4, G4, E4, H5
ex) A5, C5, B5
ex) G6, H4, G5, F5, G4, H6, F4
ex) F6, E5, F7, F5, E6
- 위치, 텍스트, 옳은 풀이, 오류를 기록하여라.
- 모든 단계를 분석한 후, 이를 XML 형식으로 변환하여라.

# 예시 출력

- (올바른 풀이일 경우)
텍스트: 12 - 8 = 4
해당 텍스트 위치: C3, B3, B4, F3, C4, D3, E3, E4, D4, F4
옳은 풀이: 12 - 8 = 4
오류: 없음
포맷:
<output>
    <left>B</left>
    <top>3</top>
    <right>F</right>
    <bottom>4</bottom>
    <text>12 - 8 = 4</text>
    <error>없음</error>
</output>


- (잘못된 풀이일 경우)
텍스트: 8 - 4 * 8 = -24
해당 텍스트 위치: D5, C6, E6, D7, C7, D6, C5, E5, E7
옳은 풀이: 8 - 4 * 7 = -20
오류: 초항을 잘못 계산함
포맷:
<output>
    <left>C</left>
    <top>5</top>
    <right>E</right>
    <bottom>7</bottom>
    <text>8 - 4 * 7 = -20</text>
    <error>초항을 잘못 계산함</error>
</output>

"""

from asgiref.sync import sync_to_async

async def parse(problem, images, step):
    # cut images[step["page"]] by step["left"], step["top"], step["right"], step["bottom"]
    # step["~"] is in (0, 1)
    total_left = max(step["left"] - padding, 0)
    total_top = max(step["top"] - padding * (images[step["page"]].height / images[step["page"]].width), 0)
    total_right = min(step["right"] + padding, 1)
    total_bottom = min(step["bottom"] + padding * (images[step["page"]].height / images[step["page"]].width), 1)

    cut_image = images[step["page"]].crop((
        images[step["page"]].width * total_left,
        images[step["page"]].height * total_top,
        images[step["page"]].width * total_right,
        images[step["page"]].height * total_bottom,
    ))


    # add grid
    cut_image = preprocess2(cut_image, images[step["page"]].width)

    import random
    cut_image.save(f"temp/{random.randint(10000, 100000 - 1)}.png")

    # convert to base64
    buffered = BytesIO()
    if cut_image.mode == "RGBA":
        cut_image = cut_image.convert("RGB")
    cut_image.save(buffered, format="JPEG")
    res = base64.b64encode(buffered.getvalue()).decode("utf-8")

    problem_skills = json.loads(problem.prompt)
    used_skills = "\n\n".join([skill for skill in problem_skills if skill in [t.strip() for t in step["skill"].split(",")]])

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt2.replace("{problem}", problem.text).replace("{process}", step["process"]).replace("{skill}", used_skills).replace("{estimate}", step["equation"]),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{res}",
                            "detail": "high",
                        },
                    }
                ],
            }
        ],
        max_tokens=1000,
    )

    print(response.choices[0].message.content)

    # parse response xml
    data = response.choices[0].message.content
    data = data[data.find("<output>")+8:data.find("</output>")]
    import xml.etree.ElementTree as ET
    root = ET.fromstring(f"<output>{data}</output>")

    left = root.find("left").text
    top = root.find("top").text
    right = root.find("right").text
    bottom = root.find("bottom").text

    left = ord(left) - ord("A")
    top = int(top) - 1
    right = ord(right) - ord("A") + 1
    bottom = int(bottom)

    grid_x_num = 10
    grid_y_num = math.ceil(images[step["page"]].height / images[step["page"]].width * grid_x_num)

    left = left / grid_x_num
    top = top / grid_y_num
    right = right / grid_x_num
    bottom = bottom / grid_y_num

    print("step", step["left"], step["top"], step["right"], step["bottom"])
    print("inner", left, top, right, bottom)
    print("total", total_left, total_top, total_right, total_bottom)

    left = total_left + left * (total_right - total_left)
    top = total_top + top * (total_right - total_left)
    right = total_left + right * (total_right - total_left)
    bottom = total_top + bottom * (total_right - total_left)

    print("final", left, top, right, bottom)

    return {
        "page": step["page"],
        "left": left,
        "top": top,
        "right": right,
        "bottom": bottom,
        "text": root.find("text").text,
        "error": root.find("error").text,
    }
    

