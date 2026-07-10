from fastapi import status

from modules.core.expcetion import BaseException, Modules


class UserExceptions(BaseException):
    module = Modules.user


class UserAlreadyExistException(UserExceptions):
    code = 1
    message = "User already exist."
    status_code = status.HTTP_409_CONFLICT


class UserNotFound(UserExceptions):
    code = 2
    message = "User not found."
    status_code = status.HTTP_401_UNAUTHORIZED


class ApiKeyMissing(UserExceptions):
    code = 3
    message = "ApiKey missing from headers"
    status_code = status.HTTP_401_UNAUTHORIZED
