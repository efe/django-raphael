from tortoise import fields
from tortoise.models import Model


class TortoiseBook(Model):
    id = fields.IntField(pk=True)
    isbn = fields.CharField(max_length=13, unique=True)

    title = fields.CharField(max_length=255)
    author = fields.CharField(max_length=255)
    language = fields.CharField(max_length=50, default="English")
    page_count = fields.IntField()

    price = fields.DecimalField(max_digits=6, decimal_places=2)
    in_stock = fields.BooleanField(default=True)

    published_date = fields.DateField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "books_book"

    def __str__(self):
        return f"{self.title} by {self.author}"
