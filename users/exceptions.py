class CooldownException(Exception):
    def __init__(self, seconds_remaining: int):
        self.seconds_remaining = seconds_remaining

class PendingSignupNotFoundException(Exception):
    pass

class UsernamePendingException(Exception):
    pass

class EmailPendingException(Exception):
    pass