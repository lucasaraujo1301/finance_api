from fastapi import status

from modules.core.expcetion import BaseException, Modules
from modules.core.i18n import _


class ServiceAccountException(BaseException):
    module = Modules.service_account


class ServiceAccountNotFound(ServiceAccountException):
    code = 1
    message = _("Service account not found.")
    status_code = status.HTTP_401_UNAUTHORIZED


class ApiKeyMissing(ServiceAccountException):
    code = 2
    message = _("API key missing from headers.")
    status_code = status.HTTP_401_UNAUTHORIZED


class ServiceAccountAlreadyExists(ServiceAccountException):
    code = 3
    message = _("Service account already exists.")
    status_code = status.HTTP_409_CONFLICT
