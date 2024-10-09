
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

from PIL import Image
import cv2
import numpy as np

def get_boxes(image: Image):
    """
    이미지에서 수식을 감지하고 바운딩 박스를 그린 후, 박스 좌표를 리턴하는 함수.
    """
    # PIL 이미지를 OpenCV 이미지로 변환
    cv_image = np.array(image.convert('L'))  # Grayscale로 변환

    # 이진화 처리
    _, binary_image = cv2.threshold(cv_image, 150, 255, cv2.THRESH_BINARY_INV)

    # 가로 방향으로 더 합치고 세로 방향은 더 엄격하게 커널 설정
    kernel = np.ones((15, 60), np.uint8)  # 세로 방향은 작게, 가로 방향은 크게
    dilated_image = cv2.dilate(binary_image, kernel, iterations=1)

    # 외곽선 찾기
    contours, _ = cv2.findContours(dilated_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 바운딩 박스 좌표들을 저장할 리스트
    bounding_boxes = []

    # 바운딩 박스 추출
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        bounding_boxes.append((x, y, x + w, y + h))  # 좌표를 (x1, y1, x2, y2) 형태로 저장

    return bounding_boxes

def preprocess2(image: Image, total_width) -> Image:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # get boxes
    boxes = get_boxes(image)

    # draw boxes
    for ind, box in enumerate(boxes):
        left, top, right, bottom = box
        draw.rectangle([left, top, right, bottom], outline=(0, 0, 255, 255), width=2)

        text = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[ind]
        font = ImageFont.load_default().font_variant(size=96)
        _, _, text_width, text_height = font.getbbox(text)

        x = (left + right) / 2 - text_width / 2
        y = (top + bottom) / 2 - text_height / 2
        draw.text((x, y), text, fill=(0, 0, 255, 96), font=font)

    return Image.alpha_composite(image, overlay), boxes


system_prompt2 = """
# Role
You are required to analyze the location of the problem solving.

# Problem
{problem}

# Step to detect
{process}

# Used skills
{skill}

# Estimated text (low accuracy)
{estimate}

# Instruction
- The goal is to extract the text of the target step from among the surrounding texts.
- The target text is marked with a blue box and labeled with an alphabet or number.
- List the alphabet or number of all boxes corresponding to the target text.
- The order of the list does not matter.

# Example
- (2,)
- (4, 3, 7)
- (F,)
- (6, 5)
- (A, 1, 6, D)
"""

async def parse(problem, images, step, idx):
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
    cut_image, boxes = preprocess2(cut_image, images[step["page"]].width)

    cut_image.save(f"temp/{idx}.png")

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

    # # parse response xml
    # data = response.choices[0].message.content
    # data = data[data.find("<output>")+8:data.find("</output>")]
    # import xml.etree.ElementTree as ET
    # root = ET.fromstring(f"<output>{data}</output>")

    # left = root.find("left").text
    # top = root.find("top").text
    # right = root.find("right").text
    # bottom = root.find("bottom").text

    # left = ord(left) - ord("A")
    # top = int(top) - 1
    # right = ord(right) - ord("A") + 1
    # bottom = int(bottom)

    # grid_x_num = 10
    # grid_y_num = math.ceil(images[step["page"]].height / images[step["page"]].width * grid_x_num)

    # left = left / grid_x_num
    # top = top / grid_y_num
    # right = right / grid_x_num
    # bottom = bottom / grid_y_num

    # print("step", step["left"], step["top"], step["right"], step["bottom"])
    # print("inner", left, top, right, bottom)
    # print("total", total_left, total_top, total_right, total_bottom)

    # left = total_left + left * (total_right - total_left)
    # top = total_top + top * (total_right - total_left)
    # right = total_left + right * (total_right - total_left)
    # bottom = total_top + bottom * (total_right - total_left)

    # print("final", left, top, right, bottom)

    # return {
    #     "page": step["page"],
    #     "left": left,
    #     "top": top,
    #     "right": right,
    #     "bottom": bottom,
    #     "text": root.find("text").text,
    #     "error": root.find("error").text,
    # }
    

