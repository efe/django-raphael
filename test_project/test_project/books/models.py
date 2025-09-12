from django.db import models

from test_project.books.mixin import RaphaelMixin


class Book(RaphaelMixin, models.Model):
    isbn = models.CharField(max_length=13, unique=True)

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    language = models.CharField(max_length=50, default="English")
    page_count = models.PositiveIntegerField()

    price = models.DecimalField(max_digits=6, decimal_places=2)
    in_stock = models.BooleanField(default=True)

    published_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author}"