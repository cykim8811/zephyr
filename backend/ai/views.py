
from django.http import HttpResponse, JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from problem.models import Problem

from PIL import Image


from .prompts import step_parser, advisor



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

    advisor.parse(problem, images, steps[1])

    return JsonResponse({
        "page_id": steps[0]["page"],
        "left": steps[0]["left"],
        "top": steps[0]["top"],
        "right": steps[0]["right"],
        "bottom": steps[0]["bottom"],
        "text": steps[0]["equation"]
    })


