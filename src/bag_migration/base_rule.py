from typing import Any, Dict


class BaseRule:
    """Base class of migration rules

    The migration rule class is responsible for converting the input message.
    """

    def migrate(self, src_topic: str, in_msg: Any) -> Dict[str, Any]:
        raise NotImplementedError()

    @classmethod
    def version(cls) -> int:
        raise NotImplementedError()
