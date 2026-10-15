class DeribitError(Exception):
    pass


class DeribitNetworkError(DeribitError):
    pass


class DeribitResponseError(DeribitError):
    pass


class DeribitAPIError(DeribitError):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"Deribit API error {code}: {message}")
        self.code = code
        self.message = message
