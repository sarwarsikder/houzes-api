from django.http import JsonResponse


def handler404(request, *args, **argv):
    response = JsonResponse({"status": False, "message": "Url not found", "data": None})
    response.status_code = 200
    return response


def handler500(request, *args, **argv):
    response = JsonResponse({"status": False, "message": "There was an error understanding the request.", "data": None})
    response.status_code = 200
    return response
