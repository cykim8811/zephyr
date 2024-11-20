from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.core.files.storage import default_storage
import hashlib

@csrf_protect
def save_images(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    problem_id = request.POST.get('problem_id')
    if not problem_id:
        return JsonResponse({'error': 'Problem ID is required'}, status=400)

    images = request.FILES.getlist('images')
    if not images:
        return JsonResponse({'error': 'No images provided'}, status=400)

    saved_paths = []
    for i, image in enumerate(images):
        # Create hash from image content and timestamp
        content_hash = hashlib.md5(image.read()).hexdigest()
        image.seek(0)  # Reset file pointer after reading
        
        path = f'dataset/problems/{problem_id}/{content_hash}.png'

        if default_storage.exists(path):
            saved_paths.append(path)
            continue

        saved_path = default_storage.save(path, image)
        saved_paths.append(saved_path)

    return JsonResponse({'message': 'Images saved successfully', 'paths': saved_paths})