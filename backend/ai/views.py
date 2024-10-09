
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

    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # # advices = asyncio.run(asyncio.gather(*[advisor.parse(problem, images, step) for step in steps]))
    # async def get_advice(step, idx):
    #     return await advisor.parse(problem, images, step, idx)
    # advices = loop.run_until_complete(asyncio.gather(*[get_advice(step, idx) for idx, step in enumerate(steps)]))

    # print(advices)

    loop.run_until_complete(advisor.parse(problem, images, steps[0], 0))

    # return JsonResponse([
    #     {
    #         "page_id": advice["page"],
    #         "left": advice["left"],
    #         "top": advice["top"],
    #         "right": advice["right"],
    #         "bottom": advice["bottom"],
    #         "text": advice["error"],
    #     }
    #     for advice in advices
    # ], safe=False)


