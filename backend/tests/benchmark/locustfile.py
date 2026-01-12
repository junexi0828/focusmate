
from locust import HttpUser, task, between

class FocusMateUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def health_check(self):
        self.client.get("/api/v1/system/health")

    @task(1)
    def echo_test(self):
        # Only tests simple endpoint without DB if available,
        # or minimal DB query
        self.client.get("/api/v1/system/health")
        # Note: Add specific DB-heavy endpoints here if needed for deeper stress testing
        # e.g. self.client.get("/api/v1/rooms/my-rooms") (requires auth)

    # To test auth routes, you would need to implement login logic in on_start
    # def on_start(self):
    #     response = self.client.post("/api/v1/auth/login", json={"..."})
    #     self.client.headers.update({"Authorization": f"Bearer {response.json()['access_token']}"})
