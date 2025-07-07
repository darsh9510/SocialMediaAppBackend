from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse
from notification.models import Notification

def send_response(request, code, message, data):
 
    response = JsonResponse(data={'responseCode': code, 'responseMessage': message, 'responseData': data})
    response.status_code = code
    return response

def send_response_validation(request, code, message):
 
    response = JsonResponse(data={'responseCode': code, 'responseMessage': message})
    response.status_code = code
    return response

class Pagination(PageNumberPagination):
    page_size = 5

paginator = Pagination()

def paginatedData(paginator,data):

    returnData = {
        'count':paginator.page.paginator.count,
        'next_page':paginator.get_next_link(),
        'previous_page':paginator.get_previous_link(),
        'results':data
    }
    return returnData

def send_notification(instance, instance_type, sender, reciever):
    Notification.objects.create(
        to_user = reciever,
        from_user = sender,
        detail = f'{instance_type}:{instance.id}'
    )
    return
