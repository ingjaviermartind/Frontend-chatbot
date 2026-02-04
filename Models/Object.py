from abc import abstractmethod, ABC

class BaseObject(ABC):
    def __init__(self, ID : int | None):
        self._id = ID

    @property
    def ID(self) -> int | None:
        return self._id

    @abstractmethod
    def to_payload(self) -> dict:
        pass
#
# EOF
#