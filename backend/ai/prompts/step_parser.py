
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
{answer}

# 지침
- 학생의 답안을 단계별로 분석하여라. 학생의 풀이는 이미지로 주어지며, 수식, 그래프, 도식 등이 포함될 수 있다.
- 개별 풀이 단계, 해당하는 스킬, 위치, 텍스트를 기록하여라.
- 위치는, 해당 풀이 단계의 식 또는 그래프, 도식과 겹치는 모든 셀의 이름을 나열하여라. 이 때 순서는 상관없다.
- 분석이 완료된 후, 이를 XML 형식으로 변환하여라.
- LaTeX 형식을 사용할 때에는, $ 표시 사이에 수식을 넣어야 한다. 예를 들어, $y = x^2$는 y = x^2로 변환되어야 한다.
  이를 지키지 않을 경우, 오류처리되어 즉시 오답처리된다.
- 그래프의 경우, '해당 단계 내용' 부분에 그래프의 내용을 간략하게 작성하여라.
- 여러개의 스킬이 사용되는 경우, 각 스킬을 쉼표로 구분하여라.
- 만약 학생의 풀이가 Skill에 제시된 방향과 다르다면, '스킬'에는 '-'를 작성하고 최대한 학생의 풀이를 있는 그대로 기록하여라. 이 경우 학생의 의도를 추측하지 않는다.


# 예시 1
[서약]
- 이미지를 기반으로, 학생의 답안 분석을 시작합니다. Skill 등의 참고자료로 학생의 답안 이미지에 없는 내용을 추가, 변경하지 않도록 하겠습니다.
- 이를 어길 시, 이에 따른 모든 책임을 지도록 하겠습니다.

### 1단계
과정: 이미지에서, 학생은 수열의 8번째 항과 9번째 항으로 공차를 구함.
해당 단계 내용: $12 - 8 = 4$
스킬: Skill A
위치: B5, C5

### 2단계
과정: 이미지에서, 학생은 공차와 8번째 항을 이용하여 초항을 구함.
해당 단계 내용: $8 - 4 * 7 = -20$
스킬: Skill E
위치: C7, C8, D7, D8, E7, E8

### 3단계
과정: 이미지에서, 학생은 초항과 공차를 이용하여 일반항을 구함.
해당 단계 내용: $a_n = -20 + 4 * (n - 1)$
스킬: Skill F
위치: A11, A12, B11, B12, C11, C12, D11, D12, E11, E12

### XML 변환
<output>
    <step>
        <process>이미지에서, 학생은 수열의 8번째 항과 9번째 항으로 공차를 구함.</process>
        <formula>$12 - 8 = 4$</formula>
        <skill>Skill A</skill>
        <left>B</left>
        <top>5</top>
        <right>C</right>
        <bottom>5</bottom>
    </step>
    <step>
        <process>이미지에서, 학생은 공차와 8번째 항을 이용하여 초항을 구함.</process>
        <formula>$8 - 4 * 7 = -20$</formula>
        <skill>Skill E</skill>
        <left>C</left>
        <top>7</top>
        <right>E</right>
        <bottom>8</bottom>
    </step>
    <step>
        <process>이미지에서, 학생은 초항과 공차를 이용하여 일반항을 구함.</process>
        <formula>$a_n = -20 + 4 * (n - 1)$</formula>
        <skill>Skill F</skill>
        <left>A</left>
        <top>11</top>
        <right>E</right>
        <bottom>12</bottom>
    </step>
</output>

# 예시 2 (Skill에 제시된 방향과 다른 경우)
[서약] (예시 1과 동일)

### 1단계
과정: 이미지에서, 학생은 수열의 8번째 항과 9번째 항으로 바로 일반항을 구함.
해당 단계 내용: $a_n = 8 + 4(n-8)$
스킬: -
위치: B6, C6

### XML 변환
<output>
    <step>
        <process>이미지에서, 학생은 수열의 8번째 항과 9번째 항으로 바로 일반항을 구함.</process>
        <formula>$a_n = 8 + 4(n-8)$</formula>
        <skill>-</skill>
        <left>B</left>
        <top>6</top>
        <right>C</right>
        <bottom>6</bottom>
    </step>
</output>

# 예시 3 (특이 케이스 - 빈 화면)
[서약] (예시 1과 동일)

### XML 변환
<output></output>

# 예시 4 (특이 케이스 - 장난의 의도. 그림그리기 / 잡담 등. 문제 풀이의 의도가 조금이라도 있으면 예시 1을 사용)
[서약] (예시 1과 동일)

### XML 변환
<output>Joking</output>
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
                "content": system_prompt1.replace("{problem}", problem.text).replace("{skills}", problem.prompt).replace("{answer}", problem.answer),
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
        temperature=0.6,
    )
    print(response.choices[0].message.content)
    print(f"{(response.usage.prompt_tokens * 2.5 / 1000000 + response.usage.completion_tokens * 10 / 1000000) * 1348}원")

    # parse response xml
    data = response.choices[0].message.content
    data = data[data.find("<output>")+8:data.find("</output>")]

    if data == "Joking":
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """
# 역할
- 학생의 수학 문제 풀이를 돕는 교수자 AI이다.
- 학생과 간단한 재미있는 대화를 나누어라. 교수자 AI로서 권위를 지키며 느낌표 사용 등의 가벼운 말투를 자제하여라.
- 수학 문제 풀이로 돌아가도록 학생을 격려하여도 좋다. 학생이 힘들어하는 상황일 수 있으니, 감정적인 지원을 제공하여라.
  다만, 쉬어도 좋다는 말은 지양하여라.
- 위치는, 해당 풀이 단계의 식 또는 그래프, 도식과 겹치는 모든 셀의 이름을 나열하여라. 이 때 순서는 상관없다.
- 분석이 완료된 후, 이를 XML 형식으로 변환하여라.

# 예시
분석: 학생은 예쁜 꽃 그림을 그렸다.
대화: 예쁜 꽃 그림이네요! 꽃은 수학 문제와 어떤 관련이 있을까요?
위치: A1, A2, B2
형식:
<output>
    <step>
        <chat>예쁜 꽃 그림이네요! 꽃은 수학 문제와 어떤 관련이 있을까요?</chat>
        <left>A</left>
        <top>1</top>
        <right>B</right>
        <bottom>2</bottom>
    </step>
</output>
"""
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
            max_tokens=500,
            temperature=0.8,
        )
        print(response.choices[0].message.content)
        print(f"{(response.usage.prompt_tokens * 2.5 / 1000000 + response.usage.completion_tokens * 10 / 1000000) * 1348}원")

        # parse response xml
        data = response.choices[0].message.content
        print(data)
        data = data[data.find("<output>")+8:data.find("</output>")]
    
    import xml.etree.ElementTree as ET
    root = ET.fromstring(f"<output>{data}</output>")
    
    steps = []
    for step in root:
        left = step.find("left").text
        right = step.find("right").text
        top = step.find("top").text
        bottom = step.find("bottom").text

        chat = step.find("chat")

        page_id = (int(top) - 1) // grid_y_num

        left = (ord(left) - ord('A')) / grid_x_num
        right = (ord(right) - ord('A') + 1) / grid_x_num
        top = ((int(top) - 1) % grid_y_num) / grid_y_num
        bottom = (((int(bottom) - 1) % grid_y_num) + 1) / grid_y_num


        steps.append({
            "process": step.find("process").text if step.find("process") is not None else "",
            "formula": step.find("formula").text if step.find("formula") is not None else "",
            "chat": chat.text if chat is not None else None,
            "skill": step.find("skill").text if step.find("skill") is not None else "",
            "page_id": page_id,
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom,
        })

    return steps