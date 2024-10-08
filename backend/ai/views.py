from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

import json
import os

from problem.models import Problem
from user.models import Solution

from PIL import ImageFont

import base64
from io import BytesIO
from PIL import Image, ImageDraw
from typing import List, Dict, Union

from .prompts import step_parser



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

    print(steps)

    return HttpResponse("OK", status=200)