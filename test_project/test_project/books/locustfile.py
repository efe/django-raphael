import json
from pathlib import Path
from locust import FastHttpUser, task, between
import random

# Load pre-fetched IDs
BOOK_IDS = json.loads(Path("book_ids.json").read_text())

def pick_book_id():
    return random.choice(BOOK_IDS)

class DjangoORMAsyncUser(FastHttpUser):
    wait_time = between(0.05, 0.15)

    @task
    def get_django_async(self):
        book_id = pick_book_id()
        with self.client.get(
                f"/books/{book_id}/django-orm-async",
                name="GET /books/:id/django-orm-async",
                timeout=5,
                catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"{resp.status_code}: {resp.text[:200]}")

class DjangoRaphaelAsyncUser(FastHttpUser):
    wait_time = between(0.05, 0.15)

    @task
    def get_raphael_async(self):
        book_id = pick_book_id()
        with self.client.get(f"/books/{book_id}/django-raphael-async",
                             name="GET /books/:id/django-raphael-async",
                             timeout=5,
                             catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"{resp.status_code}: {resp.text[:200]}")