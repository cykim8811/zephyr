from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from problem.models import Problem

from PIL import Image
import json
import time

from typing import List

from io import BytesIO
import base64

from PIL import Image, ImageDraw, ImageFont

from .prompts import step_parser, adviser

from openai import OpenAI
import dotenv

dotenv.load_dotenv()

client = OpenAI()

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

class OpenAISession:
    def __init__(self, model, messages, verbose=False, **config):
        self.model = model
        self.messages = messages
        self.default_config = {
            "model": "gpt-4o",
            "max_tokens": 1000,
            "temperature": 0.8,
            **config
        }
        self.verbose = verbose
    
    def ask(self, text, config={}):
        config = {**self.default_config, **config}
        if self.verbose: print("\n[User]\n", text)
        self.messages.append({ "role": "user", "content": text })
        response = client.chat.completions.create(
            messages=self.messages,
            **config
        ).choices[0].message.content
        self.messages.append({ "role": "assistant", "content": response })
        colorcode = "\033[92m"
        if self.verbose: print(colorcode + "\n[AI]\n" + response + "\033[0m")
        return response

    def request(self, inputs, config={}):
        config = {**self.default_config, **config}
        self.messages.append({ "role": "user", "content": inputs })
        if self.verbose: print("\n[User]\n", "(multiple inputs)")
        response = client.chat.completions.create(
            messages=self.messages,
            **config
        ).choices[0].message.content
        colorcode = "\033[92m"
        if self.verbose: print(colorcode + "\n[AI]\n" + response + "\033[0m")
        self.messages.append({ "role": "assistant", "content": response })
        return response
        

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

    images = [Image.open(image) for image in images]

    # add grid
    grid_images = [preprocess(image, i) for i, image in enumerate(images)]

    save_merged_image(grid_images, "image.png")

    # convert images to base64
    res = []
    for image in images:
        buffered = BytesIO()
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(buffered, format="JPEG")
        res.append(base64.b64encode(buffered.getvalue()).decode())
    
    grid_res = []
    for image in grid_images:
        buffered = BytesIO()
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(buffered, format="JPEG")
        grid_res.append(base64.b64encode(buffered.getvalue()).decode())
    
    initial_messages = [
        {
            "role": "system",
            "content": """
[단계 분석 방법]
관찰, 사용 가능한 스킬, 일치 여부, 평가, 위치 순으로 풀이를 분석합니다.
예시를 참고하여, 해당 단계의 풀이를 분석해주세요.

# 예시 1
사용 가능한 스킬:
[Skill C] $a_1 \\times a_2 = a_3$를 적용하면 $a_3 = 12$이다.
관찰: "$a_1 \\times a_2 = a_3$이다." 이라고 적혀있습니다.
일치 여부: 두 풀이는 정확하게 일치함.
평가: 따라서, 해당 단계에는 오류가 없습니다. [계속]
위치: <pos>C8</pos>

# 예시 2
사용 가능한 스킬:
[Skill D] $a_1 + a_2 = a_3$를 적용하면 $a_3 = 8$이다.
관찰: "$a_1 - a_2 = a_3$로 구할 수 있다."이라고 적혀있습니다.
일치 여부: 두 풀이에 차이가 존재함.
평가: 학생은 덧셈을 사용해야 하는데, 뺄셈을 사용하는 오류를 범했습니다. [오류]
위치: <pos>D3</pos>

# 예시 3
사용 가능한 스킬:
[Skill G] $a_n = a_1 + d * (n - 1)$를 적용하면 $t_n = 8 + 4 * (n - 1)$이다.
관찰: "고로 일반항은 $a_n = a_1 + 4 * n - 4$"이라고 적혀있습니다.
일치 여부: 두 풀이에 차이가 존재함.
평가: 학생은 $(n - 1)$을 전개한 형태를 활용하였으나, 이는 스킬의 식과 본질적으로 같으므로, 해당 단계에는 오류가 없습니다. [계속]
위치: <pos>E7</pos>

# 예시 4
사용 가능한 스킬:
[Skill A] $a_1 = p + r + a_3$를 적용하면 $a_1 = 3 + 3 + 4 = 10$이다.
관찰: "그러므로 초항은 $a_1 = 3 + 2 + 5 = 10$"이라고 적혀있습니다.
일치 여부: 두 풀이의 결과는 같으나 풀이 과정이 다름.
평가: 학생은 $r$과 $a_3$의 값을 잘못 구하였습니다. [오류]
위치: <pos>B5</pos>

# 예시 5
사용 가능한 스킬: 아직 사용된 스킬이 없습니다.
관찰: $a_1 = 3$이라고 적혀있습니다.
일치 여부: -
평가: 학생은 풀이에 스킬을 사용하지 않았습니다. [계속]
위치: <pos>C3</pos>

# 예시 6
사용 가능한 스킬:
[Skill E] $a_1^2 + 3\\cdot a_2 + 4 = 0$를 적용하면 $a_1^2 + 3\\cdot 8 + 4 = 0$이다.
[Skill F] $a_1^2 + 3\\cdot 8 + 4 = 0$를 계산하면 $a_1^2 = -28$이다.
관찰: "초항을 구하면$a_1 = 3\\cdot 8 + 4 = 0$ 이다"이라고 적혀있습니다.
일치 여부:
Skill E - 두 풀이는 정확하게 일치함.
Skill F - 학생은 Skill F를 사용하지 않음. (해당 스킬을 무시합니다)
평가: 학생은 [Skill E]를 올바르게 사용하였습니다. [계속]
위치: <pos>D9</pos>
"""
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{grid_res[i]}",
                        "detail": "high",
                    },
                }
                for i in range(len(res))
            ]
        }
    ]

    session = OpenAISession("gpt-4o", initial_messages, verbose=True, temperature=0.1)


    def generate():
        yield json.dumps({
            "page_id": 0,
            "left": 0.1,
            "top": 0.1,
            "right": 0.9,
            "bottom": 0.9,
            "text": "*N",
        }) + "\n"

        response = session.request([
            {
                "type": "text",
                "text": """
# 문제
{problem}
                        
# 참고 기술
{skills}
                        
주어진 Skill들을 활용하여, 이미지에 주어진 학생의 문제 풀이의 처음 단계를 분석해주세요. 마지막 줄에 태그를 추가해주세요.
만약 오류가 있다면 [오류]라고 표시해주시고, 만약 오류가 없고 마지막 단계라면 [종료]라고 표시해주세요. 다음 단계가 존재하면 [계속] 이라고 표시해주세요.
'스킬'은 문제의 참고 기술 중에서 사용된 것을 그대로 적어주세요.
'일치 여부'는 학생의 풀이와 스킬의 각 부분이 정확하게 일치하는지 여부를 확인해주세요.
'위치'는 학생의 풀이에서 오류와 겹치는 셀의 태그를 적어주세요.

주의: 계산 결과가 옳더라도, 풀이 과정이 모두 맞아야 정답처리 됩니다.
    """.replace("{skills}", 
                "\n".join([k + ": " + v for k, v in json.loads(problem.prompt).items()])
                )\
        .replace("{problem}", problem.text)
            }
        ] + [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{res[i]}",
                    "detail": "high",
                },
            }
            for i in range(len(res))
        ])
        

        import re
        position = re.search(r"<pos>(.*)</pos>", response).group(1)

        px = ord(position[0]) - ord('A')
        py = int(position[1:]) - 1

        page_id = py // grid_y_num

        py -= page_id * grid_y_num
        
        yield json.dumps({
            "page_id": page_id,
            "left": 0.05,
            "top": py / grid_y_num,
            "right": 0.95,
            "bottom": (py + 1) / grid_y_num,
            "text": "*G",
        }) + "\n"

        
        while "[오류]" not in response:
            response = session.request([
                {
                    "type": "text",
                    "text": "주어진 Skill들을 활용하여, 이미지에 주어진 학생의 문제 풀이의 다음 단계를 분석해주세요. 마지막 줄에 태그를 추가해주세요."
                }
            ] + [session.messages[-2]["content"].pop()]
            )
            import re
            position = re.search(r"<pos>(.*)</pos>", response).group(1)

            px = ord(position[0]) - ord('A')
            py = int(position[1:]) - 1

            page_id = py // grid_y_num

            py -= page_id * grid_y_num
            
            yield json.dumps({
                "page_id": page_id,
                "left": 0.05,
                "top": py / grid_y_num,
                "right": 0.95,
                "bottom": (py + 1) / grid_y_num,
                "text": "*G",
            }) + "\n"

            if "[종료]" in response: break

        if "[종료]" in response:
            yield json.dumps({
                "page_id": 0,
                "left": 0.05,
                "top": 0.05,
                "right": 0.95,
                "bottom": 0.95,
                "text": "*G",
            }) + "\n"
            time.sleep(3)
            yield "null\n"
            return

        response = session.ask("학생이 해당 오류를 고칠 수 있도록 조언해주세요. 학생이 스스로 고칠 수 있도록, 정답을 직접 제공하지 않도록 주의해주세요.")

        result = session.ask("""
해당 조언을 규칙에 맞게 고쳐주세요.

# 규칙
1. 모든 수식은 $ 기호 사이에 LaTeX로 작성한다.
ex) $a_1 \\times a_2 = a_3$, $\\frac{a_1}{a_2} = a_3$
2. 제시된 조언이 정답을 직접 제공하는 경우, 정답을 제거하고 오류를 바로잡아주는 방식으로 수정한다.
3. 2문장 이내의, 친절하게 학생을 도와주는 말투로 작성한다.
4. 완성된 조언은 <output>...</output> 태그로 감싼다.

# 예시
<output>이 수식에서 $a_1$과 $a_2$의 관계가 어떻게 되나요?</output>
""")

        advice = result[result.find("<output>")+8:result.find("</output>")]

        position = session.request([
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{grid_res[i]}",
                    "detail": "high",
                },
            }
            for i in range(len(res))
        ] + [
            {
                "type": "text",
                "text": "이미지에 격자를 겹쳐 제공합니다. 해당 오류의 공식을 다시 말하고, 해당 오류의 가장 왼쪽 위의 셀과 오른쪽 아래의 셀을 XML 형태로 제시해주세요."
                + "ex)"
                + "공식: $a_1 \\times a_2 = a_3$"
                + "<lt>C8</lt><rb>D12</rb>"
            }
        ])

        # parse lt and rb
        import re
        lt = re.search(r"<lt>(.*)</lt>", position).group(1)
        rb = re.search(r"<rb>(.*)</rb>", position).group(1)

        left = ord(lt[0]) - ord('A')
        top = int(lt[1:]) - 1
        right = ord(rb[0]) - ord('A') + 1
        bottom = int(rb[1:])

        page_id = top // grid_y_num

        top -= page_id * grid_y_num
        bottom -= page_id * grid_y_num
        

        yield json.dumps({
            "page_id": page_id,
            "left": 0.05,
            "top": top / (grid_y_num),
            "right": 0.95,
            "bottom": bottom / (grid_y_num),
            "text": advice,
        }) + "\n"

    return StreamingHttpResponse(generate(), content_type="text/event-stream")


    # yield json.dumps({
    #     "page_id": step["page_id"],
    #     "left": step["left"],
    #     "top": step["top"],
    #     "right": step["right"],
    #     "bottom": step["bottom"],
    #     "text": "*G",
    # }) + "\n"