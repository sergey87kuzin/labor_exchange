from abc import ABC, abstractmethod


class IService(ABC):
    """Базовый интерфейс для асинхронного сервиса бизнес-логики."""

    @abstractmethod
    async def create_object(self, *args, **kwargs):
        """Создать новый объект с заданными аргументами."""

        raise NotImplementedError

    @abstractmethod
    async def retrieve_object(self, *args, **kwargs):
        """Получить объект на основе заданных аргументов."""

        raise NotImplementedError

    @abstractmethod
    async def retrieve_many_objects(self, *args, **kwargs):
        """Получить несколько объектов на основе заданных аргументов."""

        raise NotImplementedError

    @abstractmethod
    async def update_object(self, *args, **kwargs):
        """Обновить существующий объект заданными аргументами."""

        raise NotImplementedError

    @abstractmethod
    async def delete_object(self, *args, **kwargs):
        """Удалить объект на основе заданных аргументов."""

        raise NotImplementedError
