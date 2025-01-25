class DataIOErrorCodes:
    """Error codes for Data IO operations"""
    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SCHEMA_RETRIEVAL_FAILED = "SCHEMA_RETRIEVAL_FAILED"

class BaseError(Exception):
    """Base error class for the application"""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthError(Exception):
    """Custom exception for authentication errors"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ValidationError(BaseError):
    """Raised when request validation fails"""
    pass

class WebhookError(BaseError):
    """Raised when webhook processing fails"""
    pass

class DataIOError(Exception):
    """Custom exception for Data IO errors"""
    def __init__(self, code, message, status_code=400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message) 