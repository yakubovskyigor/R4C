import json
import pandas as pd
import pytz
import xlsxwriter

from .models import Robot
from datetime import datetime, timedelta
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO


@csrf_exempt
def robot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            model = data.get("model")
            version = data.get("version")
            created = data.get("created")

            if len(model) != 2 or len(version) != 2:
                return JsonResponse(
                    {"error": "Invalid model or version length"}, status=400
                )

            serial = f"{model}-{version}"

            robot = Robot(serial=serial, model=model, version=version, created=created)
            robot.save()

            return JsonResponse({"message": "Robot created successfully"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


def generate_excel(request):
    end_date = datetime.now(pytz.utc)
    start_date = end_date - timedelta(days=end_date.weekday() + 7)

    unique_models = (
        Robot.objects.filter(created__gte=start_date, created__lte=end_date)
        .values("model")
        .distinct()
    )

    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)

    for model in unique_models:
        model_name = model["model"]
        model_data = (
            Robot.objects.filter(
                model=model["model"], created__gte=start_date, created__lte=end_date
            )
            .values("version")
            .annotate(count=Count("id"))
        )
        data = pd.DataFrame(list(model_data))

        worksheet = workbook.add_worksheet(model_name)

        worksheet.set_column("A:A", 15)
        worksheet.set_column("B:B", 15)
        worksheet.set_column("C:C", 25)

        worksheet.write("A1", "Модель")
        worksheet.write("B1", "Версия")
        worksheet.write("C1", "Количество за неделю")

        row = 1
        for item in data.itertuples():
            worksheet.write(row, 0, model_name)
            worksheet.write(row, 1, item.version)
            worksheet.write(row, 2, item.count)
            row += 1

    workbook.close()

    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=robots_weekly.xlsx"

    return response
