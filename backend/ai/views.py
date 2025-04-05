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
    








    initial_messages = [
        {
            "role": "system",
            "content": """
The following is a handwritten solution to a math problem.

Note: When using LaTeX, you MUST use $...$ to wrap math expressions.
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
                "text": """Convert student's handwritten solution to text. Your answer should be as equivalent as possible to the original text. Write the answer in LaTeX format. Wrap total response in <output>...</output> tag.
Extract student's answer and wrap it in <answer>...</answer> tag.

# IMPORTANT
- You must wrap latex expressions in $...$. ex) $a + b = c$

Example:
<output>
$a + b = c$
$a = \\frac{1}{2}$
$b = \\frac{1}{3}$
$c = \\frac{1 \\times 3 + 1 \\times 2}{2 \\times 3} = \\frac{5}{6}$
</output>
<answer>
$\\frac{5}{6}$
</answer>
"""
            }
        ])
        
        # Find the answer, and the solution
        answer = response.split("<answer>")[1].split("</answer>")[0]
        output = response.split("<output>")[1].split("</output>")[0]

        # Send request to the server
        import requests
        response = requests.post("http://localhost:7141/api/dee/cykim8811/submit.py", json={
            "problem": problem.text,
            "solution": output,
            "answer": answer,
        })

        if "content" not in response.text:
            raise Exception(response.text)

        data = json.loads(response.text)

        yield json.dumps({
            "page_id": 0,
            "left": 0.05,
            "top": 0.15,
            "right": 0.95,
            "bottom": 0.35,
            "user_input": output,
            "text": data["content"] if "content" in data else "error",
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