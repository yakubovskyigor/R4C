import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from customers.models import Customer
from orders.models import Order
from robots.models import Robot


@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            customer_id = data.get("customer_id", None)
            robot_serial = data.get("robot_serial", "")

            robot = Robot.objects.filter(serial=robot_serial).first()

            if robot:
                customer = Customer.objects.filter(id=customer_id).first()
                if not customer:
                    response_data = {
                        "error": "The customer with the specified id was not found",
                    }
                    return JsonResponse(response_data, status=404)

                # robot.is_available = False
                robot.save()

                order = Order.objects.create(customer=customer, robot_serial=robot_serial)

                response_data = {
                    "message": "The order has been successfully created!",
                    "order_id": order.id,
                }
                return JsonResponse(response_data)
            else:
                order = Order.objects.create(customer_id=customer_id, robot_serial=robot_serial)

                response_data = {
                    "message": 'Робот временно недоступен. Мы свяжемся с вами, когда он будет доступен.',
                    'order_id': order.id,
                }
                return JsonResponse(response_data)
        except Exception as e:
            response_data = {
                "error": str(e),
            }
            return JsonResponse(response_data, status=400)
    else:
        response_data = {"error": "Invalid request method"}
        return JsonResponse(response_data, status=405)
