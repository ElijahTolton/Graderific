from locust import HttpUser, between, task

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.client.post("/login",
                json = {"username": "david",
                "password:": "david"})
        
    @task
    def top_level(self):
        self.client.get("/")

    @task
    def owner_info(self):
        self.client.get("/1/")