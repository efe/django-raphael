from django.core.management.base import BaseCommand
from test_project.books.models import Book
from test_project.books.factories import BookFactory

class Command(BaseCommand):
    help = "Seed the database with a large number of Book records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--total",
            type=int,
            default=1_000_000,
            help="Number of books to create (default: 1,000,000)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10_000,
            help="Batch size for bulk insert (default: 10,000)",
        )

    def handle(self, *args, **options):
        total = options["total"]
        batch_size = options["batch_size"]

        self.stdout.write(self.style.NOTICE(f"📚 Creating {total:,} books..."))

        objs = []
        for i in range(1, total + 1):
            objs.append(BookFactory.build())
            if len(objs) >= batch_size:
                Book.objects.bulk_create(objs, batch_size=batch_size)
                objs.clear()
                if i % (batch_size * 5) == 0:
                    self.stdout.write(self.style.SUCCESS(f"✅ Inserted {i:,}/{total:,}"))

        if objs:
            Book.objects.bulk_create(objs, batch_size=batch_size)

        self.stdout.write(self.style.SUCCESS("🎉 Done seeding books!"))
