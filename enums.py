from enum import Enum

class LogType(Enum):
    ActiveTime = "Has active time only"
    StartAndEndDate = "Has start and end date"
    Timestamp = "Has timestamp only"
