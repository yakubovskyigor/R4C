import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Robot


@csrf_exempt
def robot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            model = data.get('model')
            version = data.get('version')
            created = data.get('created')

            if len(model) != 2 or len(version) != 2:
                return JsonResponse({'error': 'Invalid model or version length'}, status=400)

            serial = f"{model}-{version}"

            robot = Robot(serial=serial, model=model, version=version, created=created)
            robot.save()

            return JsonResponse({'message': 'Robot created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
