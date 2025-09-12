from locust import HttpUser, task, between


class RandomBookUser(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(1, 3)

    # Optionally enlarge connection pool & timeouts (per request)
    @task
    def get_random_book(self):
        with self.client.get(
            "/random-book/django-orm-async",
            timeout=5,
            name="/random-book/django-orm-async",
            catch_response=True
        ) as r:
            if r.status_code != 200:
                r.failure(f"HTTP {r.status_code}")
            else:
                if "title" not in r.json():
                    r.failure("Missing 'title' field")
