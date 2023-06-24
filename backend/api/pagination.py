from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """Определение стандарта пагинации для вывода
    определенного количества рецептов на страницах
    рецептов и избранного.
    """
    page_size = 6
    page_size_query_param = 'limit'
