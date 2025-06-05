from abc import ABC, abstractmethod

from bson import ObjectId

from domain.users.models import UserCreate, User


class IUserRepository(ABC):

    @abstractmethod
    def get_by_user_id(self, user_id: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, user: UserCreate) -> None:
        raise NotImplementedError
