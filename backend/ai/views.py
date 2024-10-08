from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from openai import OpenAI
import json
import os

from problem.models import Problem
from user.models import Solution

from PIL import ImageFont

import base64
from io import BytesIO
from PIL import Image, ImageDraw
from typing import List, Dict, Union


def preprocess(image: Image, page_id: int) -> Image:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    width, height = image.size
    grid_x_num = 10
    grid_y_num = 15

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

system_prompt = """

# 역할
학생의 수학 문제 풀이를 분석하여야 한다.

# 문제
{problem}

## 스킬 목록
{skills}

## 정답

\\frac{dy}{dx}=-\\frac{2\\pi}{3}

# 지침
학생의 풀이를 다음과 같이 단계별로 분석한다.
### 1. 오류 검출
- 위 문제에 대한 학생의 풀이가 이미지로 주어진다. 학생의 풀이가 정답인지를 판별하고, 학생의 풀이가 오답이라면 학생의 풀이를 차례대로 검토하고 처음으로 잘못된 부분을 찾아내시오. 처음으로 잘못된 부분을 찾아내는 곳 까지만 출력하시오.
- "학생은 ~를 하려 하였습니다. Skill ~을 참고하여 보았을 때, ~해야 합니다. 학생은 ~라고 답하였습니다, 학생은 ~를 (적절하게/잘못) 구하였습니다. (O/X)"와 같은 형식으로 출력하시오.

### 2-1. (오류가 있을 시) 조언
- 해당 오류를 바탕으로 학생에게 어떻게 해결해야 하는지 조언을 해주시오(30자 이내). 이 때, 직접 해결 방법을 제시하는 것이 아닌, 해결 방법에 대한 질문을 제시하시오. 해결 방법을 직접 제시하는 것은 부정행위로 간주되며 즉시 신고됩니다.

### 2-2. 좌표
학생의 풀이에서 오답이 발생한 부분의 좌표를 입력하시오. 좌표는 다음과 같이 입력하시오.
- 학생이 작성한 오답을 작성하시오.
    ex) $a_n = a_{n-1} + 2$
- 오답이 발생한 위치를 대표하는 박스를 하나 찾아내시오.
    ex) C3
    ex) F3
    ex) H7
- 오답이 발생한 부분과 겹치는 파란색 사각형을 모두 찾아내어 나열하시오.
    ex) C2, D2, E2, C3, D3, E3
    ex) F3
    ex) F5, G5, H5, I5, J5
- 이를 토대로 left, right, top, bottom을 추출하시오.
    ex) left: C, right: E, top: 2, bottom: 3
    ex) left: F, right: F, top: 3, bottom: 3
    ex) left: F, right: J, top: 5, bottom: 5

### 3. 출력
- 위의 내용을 바탕으로 XML 형식으로 출력하시오. LaTeX 수식은 필히 $로 감싸서 작성하시오. 그렇지 않으면 오답처리됩니다.
- output 태그 안에 left, right, top, bottom, advice를 넣어서 출력하시오.

# 예시
### 1. 오류 검출
- 예시 1
...
5. 학생은 수열의 공차를 구하려 하였습니다. Skill L을 참고하여 보았을 때, 공차는 3이어야 합니다. 학생은 3이라 답하였습니다. 학생은 공차를 적절하게 구하였습니다. (O)
6. 학생은 초항을 구하려 하였습니다. Skill M을 참고하여 보았을 때, 초항은 2여야 합니다. 학생은 5이라 답하였습니다. 학생은 초항을 구하는 과정에서 실수를 하였습니다. (X)

- 예시 2
...
5. 학생은 수열의 공차를 구하려 하였습니다. Skill L을 참고하여 보았을 때, 공차는 3이어야 합니다. 학생은 3이라 답하였습니다. 학생은 공차를 적절하게 구하였습니다. (O)
6. 학생은 초항을 구하려 하였습니다. Skill M을 참고하여 보았을 때, 초항은 2여야 합니다. 학생은 2이라 답하였습니다. 학생은 초항을 적절하게 구하였습니다. (O)
7. 정답은 $a_1=6$입니다. 학생은 6이라 답하였습니다. 학생은 초항 $a_1$을 올바르게 구하였습니다. (O)

- 예시 3
1. 학생은 수열 식을 세우려 하였습니다. Skill -, 수열 식은 $a_n = a_{n-1} + 3$이어야 합니다. 학생은 $a_n = a_{n-1} + 2$이라 답하였습니다. 학생은 식을 잘못 세웠습니다. (X)

### 2-1. (오류가 있을 시) 조언
"공차와 8번째 항이 있을 때, $a_1$을 구하려면 어떻게 해야 할까요?"

<output>
    <left>C</left>
    <right>E</right>
    <top>2</top>
    <bottom>3</bottom>
    <advice>공차와 8번째 항이 있을 때, $a_1$을 구하려면 어떻게 해야 할까요?</advice>
</output>
"""


client = OpenAI()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_ai(request):
    problem_id = request.POST.get('problem_id')

    if not problem_id:
        return HttpResponse("problem_id is required", status=400)
    
    problem = Problem.objects.get(id=problem_id)
    
    # get images from request
    images = request.FILES.getlist('images')
    if not images:
        return HttpResponse("Images are required", status=400)

    # convert to pil
    images = [Image.open(image) for image in images]

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
                "content": system_prompt.replace("{problem}", problem.text).replace("{skills}", problem.prompt),
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
    )
    print(response.choices[0].message.content)
    print(f"{(response.usage.prompt_tokens * 2.5 / 1000000 + response.usage.completion_tokens * 10 / 1000000) * 1348}원")

    # parse response xml
    data = response.choices[0].message.content
    data = data[data.find("<output>")+8:data.find("</output>")]
    
    import xml.etree.ElementTree as ET
    root = ET.fromstring(f"<output>{data}</output>")
    left = root.find("left").text
    right = root.find("right").text
    top = root.find("top").text
    bottom = root.find("bottom").text
    advice = root.find("advice").text

    page_id = (int(top) - 1) // 15
    left = ord(left) - ord('A')
    right = ord(right) - ord('A') + 1
    top = (int(top) - 1) % 15
    bottom = (int(bottom) - 1) % 15 + 1

    return JsonResponse({
        "page_id": page_id,
        "left": left / 10,
        "right": right / 10,
        "top": top / 15,
        "bottom": bottom / 15,
        "text": advice,
    })

