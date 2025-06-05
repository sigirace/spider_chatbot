from abc import ABC, abstractmethod
from domain.chats.models.chat_info import ChatInfo
from domain.chats.models.identifiers import ChatId


class IChatInfoRepository(ABC):
    @abstractmethod
    async def find_by_id(self, chat_id: ChatId) -> ChatInfo | None:
        """
        chat_id 에 해당하는 doc 을 ChatInfo 객체에 로드하여 리턴한다.
        """
        raise NotImplementedError

    @abstractmethod
    async def is_chat_owner(self, chat_id: ChatId, owner_id: str) -> bool:
        """
        chat_id 의 소유 여부를 비교하여 리턴한다.
        """
        raise NotImplementedError

    @abstractmethod
    async def find_last_by_owner_id(
        self,
        owner_id: str,
        include_hidden: bool,
    ) -> ChatInfo | None:
        """
        대상 소유자의 마지막 ChatInfo 를 찾아 리턴한다
        """
        raise NotImplementedError

    @abstractmethod
    async def list_all_by_owner_id(self, owner_id: str) -> list[ChatInfo]:
        """
        특정 소유자의 ChatInfo 를 모두 찾아 리스트 형태로 리턴한다.
        없는 경우, 빈 리스트가 리턴될 것을 예상
        """
        raise NotImplementedError

    @abstractmethod
    async def list_sliced(
        self, owner_id: str, max_count: int, start_offset: int | None = None
    ) -> tuple[list[ChatInfo], int | None]:
        """
        ChatInfo 리스트의 슬라이싱(pagenation) 을 수행하는 함수.
        start_offset 으로부터 "뒤로" 최대 max_count 개의 ChatInfo 를 리턴. 첫(가장 오래된) ChatInfo의 offset 값은 1로 취급.

        input:
            max_count: int = 리턴받을 ChatInfo 의 최대 개수. 마지막에 도달하기 전까지는 항상 max_count 만큼 리턴됨을 기대 가능
            start_offset: int | None = ChatInfo 의 정렬 결과 커서에서 레코드 skip 을 수행하는 횟수를 계산하는 데 사용. 0 이하의 값이 입력되는 경우 빈 리스트를 출력. None 인 경우 가장 최근 ChatInfo 부터 리턴 대상이 됨

        output: tuple
            sliced_chat_info_list: list[ChatInfo] = 슬라이싱 된 ChatInfo 의 리스트
            next_start_offset: int | None = 프론트엔드가 다음 호출에 사용할 start_offset. 가장 오래된 ChatInfo 까지 도달했다면 0 대신 None 을 리턴
        """
        raise NotImplementedError

    @abstractmethod
    async def save(self, chat_info: ChatInfo) -> ChatId | None:
        """
        채팅 객체를 받아 저장을 수행한다.
        저장에 성공한 경우 그 ChatInfo 가 부여받은 id 를 반환한다. 실패한 경우 None 반환.
        """
        raise NotImplementedError

    @abstractmethod
    async def soft_delete(self, chat_id: ChatId) -> bool:
        """
        chat_id 에 해당하는 doc를 유저로부터 숨김 처리한다
        """
        raise NotImplementedError

    # @abstractmethod
    # def delete(self, chat_id: str) -> bool:
    #     """
    #     chat_id 에 해당하는 doc 을 실제로 지운다.
    #     """
    #     raise NotImplementedError
