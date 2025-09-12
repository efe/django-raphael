import factory
import random
from decimal import Decimal
from faker import Faker

from .models import Book

fake = Faker()
random.seed(42)

class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    isbn = factory.Sequence(lambda n: f"978{str(n).zfill(10)}")
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=4).rstrip("."))
    author = factory.LazyFunction(fake.name)
    language = factory.LazyFunction(lambda: random.choice(
        ["English", "Spanish", "French", "German", "Italian", "Chinese", "Japanese", "Korean"]
    ))
    page_count = factory.LazyFunction(lambda: random.randint(80, 1200))
    price = factory.LazyFunction(lambda: Decimal(f"{random.uniform(3, 100):.2f}"))
    in_stock = factory.LazyFunction(lambda: random.choice([True, True, True, False]))
    published_date = factory.LazyFunction(lambda: fake.date_between(start_date="-70y", end_date="today"))
