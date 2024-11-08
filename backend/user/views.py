from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Solution, Problem
from .serializers import SolutionSerializer
from django.contrib.auth import authenticate
from django.views.decorators.csrf import ensure_csrf_cookie

import json

@ensure_csrf_cookie
@api_view(['GET'])
def user_info(request):
    return Response('', status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_solution(request):
    user = request.user
    problem_id = request.data.get('problem_id')
    texts = request.data.get('texts')
    page_id = request.data.get('page_id')
    stroke = request.data.get('stroke')

    if problem_id is not None and texts is not None:
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response({'error': 'Problem not found'}, status=status.HTTP_404_NOT_FOUND)

        solution, created = Solution.objects.update_or_create(
            user=user,
            problem=problem,
            defaults={'texts': texts}
        )

        serializer = SolutionSerializer(solution)
        
        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)
    elif problem_id is not None and page_id is not None and stroke is not None:
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response({'error': 'Problem not found'}, status=status.HTTP_404_NOT_FOUND)

        current_solution = Solution.objects.filter(user=user, problem=problem).first()
        if current_solution:
            current_solution = json.loads(current_solution.texts)

        if not current_solution:
            current_solution = [{"strokes": []}]

        current_solution[page_id]["strokes"].append(json.loads(stroke))

        solution, created = Solution.objects.update_or_create(
            user=user,
            problem=problem,
            defaults={'texts': json.dumps(current_solution)}
        )

        serializer = SolutionSerializer(solution)

        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'problem_id and texts or page_id and stroke are required'}, status=status.HTTP_400_BAD_REQUEST)
            

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_solution(request):
    user = request.user
    problem_id = request.query_params.get('problem_id')

    if not problem_id:
        return Response({'error': 'problem_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        problem = Problem.objects.get(id=problem_id)
    except Problem.DoesNotExist:
        return Response({'error': 'Problem not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        solution = Solution.objects.get(user=user, problem=problem)
        serializer = SolutionSerializer(solution)
        return Response(serializer.data)
    except Solution.DoesNotExist:
        # Create empty solution
        solution = Solution.objects.create(user=user, problem=problem, texts='[{\"strokes\": []}]')
        serializer = SolutionSerializer(solution)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
from django.contrib.auth import login

@api_view(['POST'])
def minimal_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(request, email=email, password=password)
    
    print(f'User: {user}')

    if user is not None:
        login(request, user)
        return Response('', status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    