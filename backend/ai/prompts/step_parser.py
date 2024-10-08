
import dotenv
import base64
from PIL import Image, ImageDraw, ImageFont
from typing import List

from io import BytesIO
from openai import OpenAI

dotenv.load_dotenv()

client = OpenAI()

system_prompt1 = """

# 역할
학생의 수학 문제 풀이를 분석하여야 한다.

# 문제
{problem}

## 스킬 목록
{skills}

## 정답

\\frac{dy}{dx}=-\\frac{2\\pi}{3}

# 지침
- 학생의 답안을 단계별로 분석하여라.
- 개별 풀이 단계, 해당하는 스킬, 위치, 텍스트를 기록하여라.
- 모든 단계를 분석한 후, 이를 XML 형식으로 변환하여라.

# 예시 출력

### 1단계
과정: 학생은 수열의 8번째 항과 9번째 항으로 공차를 구하고자 함.
스킬: Skill A
위치: B5, C5
식: 12 - 8 = 4

### 2단계
과정: 학생은 공차와 8번째 항을 이용하여 초항을 구하고자 함.
스킬: Skill E
위치: C7, C8, D7, D8, E7, E8
식: 8 - 4 * 7 = -20

### 3단계
과정: 학생은 초항과 공차를 이용하여 일반항을 구하고자 함.
스킬: Skill F
위치: A11, A12, B11, B12, C11, C12, D11, D12, E11, E12
식: a_n = -20 + 4 * (n - 1)

### 변환 단계
<output>
    <step>
        <process>학생은 수열의 8번째 항과 9번째 항으로 공차를 구하고자 함.</process>
        <skill>Skill A</skill>
        <left>B</left>
        <top>5</top>
        <right>C</right>
        <bottom>5</bottom>
        <equation>12 - 8 = 4</equation>
    </step>
    <step>
        <process>학생은 공차와 8번째 항을 이용하여 초항을 구하고자 함.</process>
        <skill>Skill E</skill>
        <left>C</left>
        <top>7</top>
        <right>E</right>
        <bottom>8</bottom>
        <equation>8 - 4 * 7 = -20</equation>
    </step>
    <step>
        <process>학생은 초항과 공차를 이용하여 일반항을 구하고자 함.</process>
        <skill>Skill F</skill>
        <left>A</left>
        <top>11</top>
        <right>E</right>
        <bottom>12</bottom>
        <equation>a_n = -20 + 4 * (n - 1)</equation>
    </step>
</output>
"""

grid_x_num = 10
grid_y_num = 15

def preprocess(image: Image, page_id: int) -> Image:
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
            text = f"{chr(ord('A') + ix)}{iy + 1 + grid_y_num * page_id}"
            font = ImageFont.load_default().font_variant(size=64)
            _, _, text_width, text_height = font.getbbox(text)
            x = (width - 2) * (ix + 0.5) // grid_x_num - text_width // 2
            y = (height - 2) * (iy + 0.5) // grid_y_num - text_height // 2
            draw.text((x, y), text, fill=(0, 0, 255, 96), font=font)

    image = Image.alpha_composite(image.convert("RGBA"), overlay)
    return image

def save_merged_image(images: List[Image], filename: str):
    width, height = images[0].size
    merged = Image.new("RGB", (width, len(images) * height))
    for i, image in enumerate(images):
        merged.paste(image, (0, i * height))
    merged.save(filename)


def parse(problem, images):

    # add grid
    images = [preprocess(image, i) for i, image in enumerate(images)]

    save_merged_image(images, "image.png")

    # convert to base64
    res = []
    for image in images:
        buffered = BytesIO()
        if image.mode == "RGBA":
            image = image.convert("RGB")
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        res.append(img_str)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt1.replace("{problem}", problem.text).replace("{skills}", problem.prompt),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{res[i]}",
                            "detail": "high",
                        },
                    }
                    for i in range(len(res))
                ],
            }
        ],
        max_tokens=2000,
    )
    print(response.choices[0].message.content)
    print(f"{len(res)} images - {(response.usage.prompt_tokens * 2.5 / 1000000 + response.usage.completion_tokens * 10 / 1000000) * 1348}원")

    # parse response xml
    data = response.choices[0].message.content
    data = data[data.find("<output>")+8:data.find("</output>")]
    
    import xml.etree.ElementTree as ET
    root = ET.fromstring(f"<output>{data}</output>")
    
    steps = []
    for step in root:
        steps.append({
            "process": step.find("process").text,
            "page": (int(step.find("top").text) - 1) // grid_y_num,
            "skill": step.find("skill").text,
            "left": (ord(step.find("left").text) - ord("A")) / grid_x_num,
            "top": (int(step.find("top").text) - 1) % grid_y_num / grid_y_num,
            "right": (ord(step.find("right").text) - ord("A") + 1) / grid_x_num,
            "bottom": ((int(step.find("bottom").text) - 1) % grid_y_num + 1) / grid_y_num,
            "equation": step.find("equation").text,
        })

    return steps
