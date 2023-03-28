from django.conf import settings
from django.core.paginator import Paginator


def get_page(
        request,
        queryset,
        quantity: int = settings.POSTS_ON_PAGE
) -> Paginator:
    paginator = Paginator(queryset, quantity)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
