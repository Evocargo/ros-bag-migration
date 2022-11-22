import json
from typing import Any, Dict

from geometry_msgs.msg import Point, Pose, Quaternion

from .base_rule import BaseRule


class ExampleRename(BaseRule):
    MIGRATE_TOPIC = {"/test/topic": "/rename/topic"}

    def migrate(self, src_topic: str, in_msg: Any) -> Dict[str, Any]:
        return {self.MIGRATE_TOPIC.get(src_topic, src_topic): in_msg}

    @classmethod
    def version(cls):
        return 1


class ExampleUpdateMsg(BaseRule):
    MIGRATE_TOPIC = ["/test/upd_msg"]

    def migrate(self, src_topic: str, in_msg: Any) -> Dict[str, Any]:
        if src_topic in self.MIGRATE_TOPIC:
            data = json.loads(in_msg.data)
            point = Point()
            point.x = data["pose"]["x"]
            point.y = data["pose"]["y"]
            point.z = data["pose"]["z"]

            quat = Quaternion()
            quat.x = data["orient"]["x"]
            quat.y = data["orient"]["y"]
            quat.z = data["orient"]["z"]
            quat.w = data["orient"]["w"]

            pose = Pose()
            pose.position = point
            pose.orientation = quat
            return {src_topic: pose}
        return {src_topic: in_msg}

    @classmethod
    def version(cls):
        return 2


class ExampleSplitMsg(BaseRule):
    MIGRATE_TOPIC = ["/test/split"]

    def migrate(self, src_topic: str, in_msg: Any) -> Dict[str, Any]:
        if src_topic in self.MIGRATE_TOPIC:
            data = json.loads(in_msg.data)
            point = Point()
            point.x = data["pose"]["x"]
            point.y = data["pose"]["y"]
            point.z = data["pose"]["z"]

            quat = Quaternion()
            quat.x = data["orient"]["x"]
            quat.y = data["orient"]["y"]
            quat.z = data["orient"]["z"]
            quat.w = data["orient"]["w"]
            return {f"{src_topic}/pose": point, f"{src_topic}/orient": quat}
        return {src_topic: in_msg}

    @classmethod
    def version(cls):
        return 3
