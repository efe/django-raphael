from django.urls import path

from test_project.books.views import retrieve_random_book_view_django_orm_async, retrieve_random_book_view_django_raphael_async

urlpatterns = [
    path("random-book/django-orm-async", retrieve_random_book_view_django_orm_async),
    path("random-book/django-raphael-async", retrieve_random_book_view_django_raphael_async),
]
