class AppError(Exception):
    def __init__(self, message='An error occurred.', status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}


class ValidationError(AppError):
    def __init__(self, message='Validation failed.', payload=None):
        super().__init__(message, status_code=400, payload=payload)


class UnauthorizedError(AppError):
    def __init__(self, message='Unauthorized access.', payload=None):
        super().__init__(message, status_code=403, payload=payload)


class AuthenticationError(AppError):
    def __init__(self, message='Authentication required.', payload=None):
        super().__init__(message, status_code=401, payload=payload)


class NotFoundError(AppError):
    def __init__(self, message='Resource not found.', payload=None):
        super().__init__(message, status_code=404, payload=payload)
