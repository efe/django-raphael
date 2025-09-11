# django-raphael

A low-effort, fully asynchronous ORM for Django applications, powered by [Tortoise ORM](https://tortoise.github.io/) under the hood. (draft)

## Why?

Django’s async ORM currently runs asynchronous calls in [a separate thread](https://docs.djangoproject.com/en/5.2/topics/async/), which introduces a performance difference compared to a fully asynchronous ORM. django-raphael provides a bridge between Django models and a fully async ORM like Tortoise ORM, enabling developers to use async database operations without redefining models and while maintaining synchronization.

## Usage

```python
# books/models.py

class Book(RaphaelMixin, models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
```

```python
# books/views.py

async def retrieve_book(request, id: int):
    book = await Book.objects.aget(id=id)
    return JsonResponse({
        "id": book.id,
        "title": book.title,
        "author": book.author,
    })

async def create_book(request):
    book = await Book.objects.acreate(
        title=request.body.get("title"),
        author=request.body.get("author"),
    )

    return JsonResponse({
        "id": book.id,
        "title": book.title,
        "author": book.author,
    }, status=201)
```

## "raphael?"

Tortoise ORM does its thing behind the scenes and it reminds me of the Ninja Turtles. [Raphael](https://en.wikipedia.org/wiki/Raphael_(Teenage_Mutant_Ninja_Turtles)), the hot-headed one, feels like the perfect spirit animal for async Python’s feel.