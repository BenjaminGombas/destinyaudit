class BungieAPIException(Exception):
    def __init__(self, message, error_code=None, response=None):
        self.message = message
        self.error_code = error_code
        self.response = response
        super().__init__(self.message)


class BungieRateLimitException(BungieAPIException):
    pass


class BungieMaintenanceException(BungieAPIException):
    pass
