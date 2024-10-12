
from openai import OpenAI
import json
import base64
from io import BytesIO

import dotenv
dotenv.load_dotenv()

client = OpenAI()

system_prompt2 = """
# 역할
- 학생의 수학 문제 풀이의 해당 단계를 분석하여야 한다.
- 문제 풀이의 전체와 일부분이 이미지로 주어지며, 해당 단계에서 사용되는 스킬이 주어진다.
- 학생의 답안을 분석하여, 오류가 있는지 확인하고, 오류가 있다면 어떤 부분에서 오류가 발생하였는지 설명하여라.
- 오류가 있는 경우, 학생에게 조언을 제공하여라. 학생이 제대로 된 답을 제공할 수 있도록 하는 질문 형식이 권장된다.
  다만, 학생에게 직접 옳은 정답을 제공하는 것은 부정행위로 간주되어 즉시 오답처리된다.
- 모든 분석이 완료된 후, 이를 XML 형식으로 변환하여라.
- LaTeX 형식을 사용할 때에는, $ 표시 사이에 수식을 넣어야 한다. 예를 들어, $y = x^2$는 y = x^2로 변환되어야 한다.
  이를 지키지 않을 경우, 오류처리되어 즉시 오답처리된다.
- 문제의 풀이에는 지장이 없지만 문제의 조건을 빼먹은 경우, 조언에 "~라 하기 위해서는 어떤 조건이 필요할까요?"와 같은 질문을 사용하여라.

# 문제
{problem}

# 평가하여야 하는 단계
{step}

# 해당 단계의 스킬
{skills}

# 학생의 식
{student_formula}

# 예시
### 오류가 없을 경우
- 옳은 풀이
Skill C를 참고하여 봤을 때, 학생은 초항을 구하기 위하여 $a_1 = a_8 - 7d$를 사용하여야 한다.
고로 학생은 $a_1 = 20 - 7 * 4 = -8$이라 써야 한다.

- 학생의 풀이
학생은 초항을 구할 때, $a_1 = a_8 - 7d$를 사용하여 $a_1 = 20 - 7 * 4 = -8$을 구하였다.

- 평가
따라서, 학생은 초항을 올바르게 구하였다.

- XML 변환
<output></output>

### 오류가 있을 경우
- 옳은 풀이
- Skill C를 참고하여 봤을 때, 학생은 초항을 구하기 위하여 $a_1 = a_8 - 7d$를 사용하여야 한다.
고로 학생은 $a_1 = 20 - 7 * 4 = -8$이라 써야 한다.

- 학생의 풀이
학생은 초항을 구할 때, $a_1 = a_8 - 8d$를 사용하여 $a_1 = 20 - 8 * 4 = -12$을 구하였다.

- 평가
따라서, 학생은 초항을 구하는 과정에서 오류가 발생하였다.

- XML 변환
<output>
    <error>학생은 8번째 항과 공차를 이용하여 초항을 구하는 과정에서 오류가 발생하였다.</error>
    <advice>초항을 구할 때, 8번째 항에서 공차에 몇을 곱해서 빼야 초항을 구할 수 있을까요?</advice>
</output>

# 평가 단계 예시
- 따라서, 학생은 초항을 올바르게 구하였다.
- 따라서, 학생은 초항을 구하는 과정에서 오류가 발생하였다.
- 학생은 중간 단계를 생략하고 초항을 구하였다. 학생의 개념 이해에는 문제가 없는 것으로 보이므로, 정답처리하도록 하자.

# 주의사항
- 학생에게 직접 옳은 정답을 제공하는 것은 부정행위로 간주되어 즉시 오답처리된다.
- 학생에게 질문 형식으로 조언을 제공하여라.
- LaTeX 형식을 사용할 때에는, $ 표시 사이에 수식을 넣어야 한다. 이를 지키지 않을 경우, 오류처리되어 즉시 오답처리된다.
- "평가하여야 하는 단계"는 학생의 답안에서 특정 부분을 의미한다. 이 부분 만을 평가하도록 하고, 이 부분 외의 다른 부분을 평가하지 않도록 주의하여라.
  "평가하여야 하는 단계" 이외의 부분을 평가할 경우, 심각한 오류로 간주되어 즉시 오답처리된다.
- "옳은 풀이" 항목에서는, Skill에서 제시하는 범위 내에서만 평가하여야 한다.
"""

padding = 0.06
def parse(problem, images, step):
    print("adviser", step)
    page_id = step["page_id"]
    total_image = images[page_id]

    # crop image
    crop_left = max(0, step["left"] - padding)
    crop_top = max(0, step["top"] - padding * (total_image.width / total_image.height))
    crop_right = min(1, step["right"] + padding)
    crop_bottom = min(1, step["bottom"] + padding * (total_image.width / total_image.height))
    
    image = total_image.crop((
        crop_left * total_image.width,
        crop_top * total_image.height,
        crop_right * total_image.width,
        crop_bottom * total_image.height,
    ))

    # convert cropped to base64
    buffered = BytesIO()
    if image.mode == "RGBA":
        image = image.convert("RGB")
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # convert total image to base64
    buffered = BytesIO()
    if total_image.mode == "RGBA":
        total_image = total_image.convert("RGB")
    total_image.save(buffered, format="JPEG")
    total_img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    skills = ["- " + skill_text.strip() + "\n" + json.loads(problem.prompt)[skill_text.strip()] for skill_text in step["skill"].split(",") if skill_text.strip() in json.loads(problem.prompt)]

    total_prompt = system_prompt2.replace("{problem}", problem.text)\
                    .replace("{skills}", '\n\n'.join(skills))\
                    .replace("{step}", step["process"])\
                    .replace("{student_formula}", step["formula"])
    print("step:", step)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": total_prompt,
            },
            {
                "role": "user",
                "content": [
                    # {
                    #     "type": "image_url",
                    #     "image_url": {
                    #         "url": f"data:image/jpeg;base64,{img_str}",
                    #         "detail": "high",
                    #     },
                    # },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{total_img_str}",
                            "detail": "high",
                        },
                    }
                ],
            }
        ],
        max_tokens=1000,
        temperature=0.2,
    )

    # parse response xml
    data = response.choices[0].message.content
    print("\n\n[chatgpt result]\n" + data)
    data = data[data.find("<output>")+8:data.find("</output>")]

    import xml.etree.ElementTree as ET
    root = ET.fromstring(f"<output>{data}</output>")

    error = root.find("error")
    advice = root.find("advice")

    if error is None or advice is None:
        return None
    
    error = error.text
    advice = advice.text

    return {
        "page_id": page_id,
        "left": step["left"],
        "top": step["top"],
        "right": step["right"],
        "bottom": step["bottom"],
        "error": error,
        "advice": advice,
    }

