from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination

class Pagination(PageNumberPagination):
    page_size = 10

paginator = Pagination()

def send_response(request, code, message, data):
 
    response = JsonResponse(data={'responseCode': code, 'responseMessage': message, 'responseData': data})
    response.status_code = 200
    return response

def send_response_validation(request, code, message):
 
    response = JsonResponse(data={'responseCode': code, 'responseMessage': message})
    response.status_code = 200
    return response

def paginatedData(paginator,data):

    returnData = {
        'count':paginator.page.paginator.count,
        'next_page':paginator.get_next_link(),
        'previous_page':paginator.get_previous_link(),
        'results':data
    }
    return returnData
