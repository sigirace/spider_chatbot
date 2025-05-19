from abc import ABC, abstractmethod

from users.domain.model.user import BaseUser, User


class IUserRepository(ABC):

    @abstractmethod
    def get_by_user_id(self, user_id: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, user: User) -> BaseUser:
        raise NotImplementedError
