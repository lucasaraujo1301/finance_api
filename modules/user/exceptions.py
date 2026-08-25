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


class InvalidCredentials(UserExceptions):
    code = 4
    message = "Invalid credentials."
    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidRefreshToken(UserExceptions):
    code = 5
    message = "Invalid refresh token."
    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidPasswordUpdateToken(UserExceptions):
    code = 6
    message = "Invalid password update token."
    status_code = status.HTTP_401_UNAUTHORIZED


class SuperuserRequired(UserExceptions):
    code = 7
    message = "Superuser access required."
    status_code = status.HTTP_403_FORBIDDEN
