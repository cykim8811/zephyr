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

scale = 2
xcnt = 10
ycnt = 15
def build_screen(page_data: Dict[str, List[Dict[str, Union[str, List[Dict[int, int]]]]]]) -> str:
    # 이미지 생성
    img = Image.new('RGBA', (round(834 * scale), round(1179 * scale)), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 스트로크 그리기
    for stroke in page_data['strokes']:
        if stroke['type'] == 'pen':
            color = 'black'
            width = round(2 * scale)
        elif stroke['type'] == 'eraser':
            color = 'white'
            width = round(60 * scale)
        else:
            continue

        points = stroke['points']
        if len(points) > 1:
            for i in range(len(points) - 1):
                start = (round(points[i]['x'] * scale), round(points[i]['y'] * scale))
                end = (round(points[i+1]['x'] * scale), round(points[i+1]['y'] * scale))
                draw.line([start, end], fill=color, width=width)
    
    overlay = Image.new('RGBA', (round(834 * scale), round(1179 * scale)), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for i in range(xcnt+1):
        overlay_draw.line([(833 * scale / xcnt * i, 0), (833 * scale / xcnt * i, 1179 * scale)], fill='blue', width=round(1 * scale))
    for i in range(ycnt+1):
        overlay_draw.line([(0, 1179 * scale / ycnt * i), (833 * scale, 1179 * scale / ycnt * i)], fill='blue', width=round(1 * scale))

    for ix in range(xcnt):
        for iy in range(ycnt):
            iya = chr(ord('A') + iy)
            overlay_draw.text(
                (833 * scale / xcnt * ix + xcnt, 1179 * scale / ycnt * iy + 5),
                f"{iya}{ix}",
                fill='#0000FF33',
                font=ImageFont.load_default().font_variant(size=round(52 * scale))
            )
    
    img = Image.alpha_composite(img, overlay)

    # 이미지를 Base64로 인코딩
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return img_str


def save_base64_to_file(base64_string: str, file_path: str) -> None:
    """
    Base64로 인코딩된 이미지 문자열을 파일로 저장합니다.
    
    :param base64_string: Base64로 인코딩된 이미지 문자열
    :param file_path: 저장할 파일 경로 (예: 'image.png')
    """
    # Base64 문자열을 디코드하여 바이너리 데이터로 변환
    image_data = base64.b64decode(base64_string)
    
    # 바이너리 데이터를 파일로 저장
    with open(file_path, 'wb') as file:
        file.write(image_data)
    
    print(f"이미지가 {file_path}에 저장되었습니다.")

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
    ex) J7
- 오답이 발생한 부분과 겹치는 파란색 사각형을 모두 찾아내어 나열하시오.
    ex) C2, D2, C3, D3, C4, D4
    ex) F3
    ex) J5, J6, J7, J8, J9, J10
- 이를 토대로 left, right, top, bottom을 추출하시오.
    ex) left: 2, right: 4, top: C, bottom: D
    ex) left: 3, right: 3, top: F, bottom: F
    ex) left: 5, right: 10, top: J, bottom: J

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
    <left>3</left>
    <right>5</right>
    <top>G</top>
    <bottom>J</bottom>
    <advice>공차와 8번째 항이 있을 때, $a_1$을 구하려면 어떻게 해야 할까요?</advice>
</output>
"""


client = OpenAI()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_ai(request):
    problem_id = request.data.get('problem_id')

    if not problem_id:
        return HttpResponse("Problem ID is required", status=400)
    
    problem = Problem.objects.get(id=problem_id)
    user = request.user

    solution = Solution.objects.filter(user=user, problem=problem).first()

    if not solution:
        return HttpResponse("Solution not found", status=404)
    
    res = build_screen(json.loads(solution.texts)[0])

    save_base64_to_file(res, 'image.png')

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
                            "url": f"data:image/jpeg;base64,{res}",
                            "detail": "high",
                        },
                    },
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

    left = int(left)
    right = int(right) + 1
    top = ord(top) - ord('A')
    bottom = ord(bottom) - ord('A') + 1

    print({
        "page_id": 0,
        "left": left / 10,
        "right": right / 10,
        "top": top / 15,
        "bottom": bottom / 15,
        "text": advice,
    })
    
    return JsonResponse({
        "page_id": 0,
        "left": left / 10,
        "right": right / 10,
        "top": top / 15,
        "bottom": bottom / 15,
        "text": advice,
    })

