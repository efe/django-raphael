from django.urls import path

from test_project.books import views

urlpatterns = [
    path("random-book/django-orm-async", views.retrieve_random_book_view_django_orm_async),
    path("random-book/django-raphael-async", views.retrieve_random_book_view_django_raphael_async),
    path("books/<int:book_id>/django-orm-async", views.retrieve_book_django_orm_async),
    path("books/<int:book_id>/django-raphael-async", views.retrieve_book_django_raphael_async),

]
