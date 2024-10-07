from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Problem
from .serializers import ProblemSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_problem(request):
    problem_id = request.query_params.get('id')

    if not problem_id:
        return Response({'error': 'Problem ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        problem = Problem.objects.get(id=problem_id)
    except Problem.DoesNotExist:
        return Response({'error': 'Problem not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProblemSerializer(problem)
    return Response(serializer.data)

