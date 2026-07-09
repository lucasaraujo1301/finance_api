from enum import Enum

from fastapi import HTTPException, status


class Modules(Enum):
    system = 0
    user = 1


class BaseException(HTTPException):
    module: Modules | None = None
    code: int = 0
    message: str = "An unexpected error occurred."
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, *args, **kwargs):
        self.error_code = self._get_error_code()

        super().__init__(status_code=self.status_code, detail=self.message)

    def _get_error_code(self):
        return f"{self._get_module_code()}{self.code:03d}"
    
    def _get_module_code(self):
        if not isinstance(self.module, Modules):
            raise Exception("Wrong module configuration")

        return self.module.value


class SystemException(BaseException):
    module = Modules.system
    code = 1
