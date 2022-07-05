from django.core.paginator import Paginator


def get_page_obj(obj_list, posts_per_page_limit, request):
    paginator = Paginator(obj_list, posts_per_page_limit)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
