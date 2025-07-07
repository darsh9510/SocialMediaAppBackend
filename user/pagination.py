from rest_framework.pagination import PageNumberPagination

class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20

generalPaginator = Pagination()

def paginatedData(request, querySet, pageSize):

    paginator = Pagination()
    paginator.page_size = pageSize
    data = paginator.paginate_queryset(querySet,request)
    returnData = {
        'count':paginator.page.paginator.count,
        'next_page':paginator.get_next_link(),
        'previous_page':paginator.get_previous_link(),
        'results':data
    }
    return returnData