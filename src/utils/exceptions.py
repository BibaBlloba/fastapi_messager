class CustomException(Exception):
    detail = 'Неожиданная ошибка'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(CustomException):
    detail = 'Объект не найден'


class ObjectExists(CustomException):
    detail = 'Объект уже существует'
