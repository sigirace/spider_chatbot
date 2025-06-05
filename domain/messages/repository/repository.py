from abc import ABC, abstractmethod

from domain.chats.models.identifiers import ChatId
from domain.messages.models.identifiers import MessageId
from domain.messages.models.message import BaseMessage


class IMessageRepository(ABC):
    @abstractmethod
    async def list_all_by_chat_id(self, chat_id: ChatId) -> list[BaseMessage]:
        """
        chat_id 에 해당하는 메시지들을 묶어 리스트 형식으로 리턴한다.
        idx가 있을 경우 해당 메세지만큼 slice를 수행한다.
        """
        raise NotImplementedError

    @abstractmethod
    async def count_by_chat_id(self, chat_id: ChatId) -> int:
        """
        chat_id 에 속하는 메시지들을 카운트하여 리턴한다
        """
        raise NotImplementedError

    @abstractmethod
    async def list_sliced(
        self,
        chat_id: ChatId,
        max_count: int,
        start_offset: int | None = None,
    ) -> tuple[list[BaseMessage], int | None]:
        """
        메시지 리스트의 슬라이싱(pagenation) 을 수행하는 함수.
        start_offset 으로부터 "뒤로" 최대 max_count 개의 메시지를 리턴. 채팅에서의 첫 메시지의 offset 값은 1로 취급.

        input:
            max_count: int = 리턴받을 메시지의 최대 개수. 마지막에 도달하기 전까지는 항상 max_count 만큼 리턴됨을 기대 가능
            start_offset: int | None = 메시지의 정렬 결과 커서에서 레코드 skip 을 수행하는 횟수를 계산하는 데 사용. 0 이하의 값이 입력되는 경우 빈 리스트를 출력. None 인 경우 가장 최근 메시지부터 리턴 대상이 됨

        output: tuple
            sliced_message_list: list[Message] = 슬라이싱 된 Message 의 리스트
            next_start_offset: int | None = 프론트엔드가 다음 호출에 사용할 start_offset. 메시지가 끝에 도달했다면 0 대신 None 을 리턴
        """
        raise NotImplementedError

    @abstractmethod
    async def insert(self, message: BaseMessage) -> MessageId:
        """
        메시지를 입력으로 받아 그 메시지를 컬렉션에 추가하는 프로시저.
        id의 부여를 DB에 일임하고자 하므로 DB에 저장한 뒤, 그 결과로써 부여받은 id 로 받아온다
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, message: BaseMessage) -> bool:
        """
        메시지를 입력받아 그 메시지를 업데이트하는 프로시저.
        DB에 저장한 뒤, 그 결과를 bool 값으로 받아온다. -> 당장 필요하진 않으나 약함. 이후 개선 필요
        """
        raise NotImplementedError
