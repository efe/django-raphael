from django.http import JsonResponse, Http404
from test_project.books.models import Book

def serialize_book(book):
    return {
        "id": book.id,
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "language": book.language,
        "page_count": book.page_count,
        "price": str(book.price),
        "in_stock": book.in_stock,
        "published_date": book.published_date.isoformat(),
        "created_at": book.created_at.isoformat(),
    }


async def retrieve_random_book_view_django_orm_async(request):
    """
    Async view that retrieves a single Book record by ID using Django ORM (objects.aget)
    and returns it as JSON.
    """
    try:
        book = await Book.objects.order_by("?").afirst()
    except Book.DoesNotExist:
        return JsonResponse({"detail": "Book not found"}, status=404)

    return JsonResponse(serialize_book(book))


async def retrieve_random_book_view_django_raphael_async(request):
    """
    Async view that retrieves a single Book record by ID using Django Raphael (aobject.get)
    and returns it as JSON.
    """
    try:
        book = await Book.aobjects.order_by("?").first()
    except Book.DoesNotExist:
        return JsonResponse({"detail": "Book not found"}, status=404)

    return JsonResponse(serialize_book(book))
