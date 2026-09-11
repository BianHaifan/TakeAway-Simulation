from typing import Generic, TypeVar
from o2des.common import ActionSet
from o2des.core import Sandbox

T = TypeVar('T')

class Generator(Sandbox, Generic[T]):
    def __init__(
        self,
        id: str = "",
        seed: int = 0
    ):
        uid = id if id else self.__class__.__name__
        super().__init__(seed=seed, uid=uid)
        self.on_arrive = ActionSet(object)
        self.on_finish = self.on_arrive

    def arrive(self, entity: T) -> None:
        self.on_arrive(entity)