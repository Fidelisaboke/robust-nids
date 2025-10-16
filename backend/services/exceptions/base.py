class ServiceException(Exception):
    """Base class for all service-layer exceptions."""

    def __init__(self, detail: str = 'A service error occurred.'):
        self.detail = detail
        super().__init__(detail)
