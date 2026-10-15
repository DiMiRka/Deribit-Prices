class PriceNotFoundError(Exception):
    def __init__(self, ticker: str) -> None:
        super().__init__(f"No prices stored for ticker {ticker!r}")
        self.ticker = ticker
