from fastapi import status

from modules.core.expcetion import BaseException, Modules


class UserExceptions(BaseException):
    module = Modules.user


class UserAlreadyExistException(UserExceptions):
    code = 1
    message = "User already exist."
    status_code = status.HTTP_409_CONFLICT
