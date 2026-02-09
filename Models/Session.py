class Session:
    def __init__(self, context):
        self.context = context

    @property
    def is_authenticated(self):
        return self.context.user_data.get("authenticated", False)

    @property
    def token(self):
        return self.context.user_data.get("token")

    @property
    def refresh(self):
        return self.context.user_data.get("refresh")

    @property
    def worker(self):
        return self.context.user_data.get("worker")

    def logout(self):
        self.context.user_data.clear()
        self.context.user_data["authenticated"] = False
