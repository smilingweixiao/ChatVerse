from enum import Enum

class EventType(Enum):
    USER_INPUT = 1
    AGENT_INPUT = 2

agentMap = {
    1: "joy",
    2: "debater",
    3: "hater",
    4: "joker",
    5: "thinker",
    6: "nova",
    7: "expert",
    8: "evil"
}