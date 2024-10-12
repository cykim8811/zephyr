from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from problem.models import Problem

from PIL import Image
import json
import time

from .prompts import step_parser, adviser



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

    steps = step_parser.parse(problem, images)

    def generate():
        advice = None
        for step in steps:
            advice = adviser.parse(problem, images, step)
            if advice is not None:
                yield json.dumps({
                    "page_id": advice["page_id"],
                    "left": advice["left"],
                    "top": advice["top"],
                    "right": advice["right"],
                    "bottom": advice["bottom"],
                    "text": advice["advice"],
                }) + "\n"
                print("=" * 100)
            else:
                yield json.dumps({
                    "page_id": step["page_id"],
                    "left": step["left"],
                    "top": step["top"],
                    "right": step["right"],
                    "bottom": step["bottom"],
                    "text": "No error found...",
                }) + "\n"
                print("=" * 100)
        time.sleep(1)
        yield "null\n"
    
    return StreamingHttpResponse(generate())
