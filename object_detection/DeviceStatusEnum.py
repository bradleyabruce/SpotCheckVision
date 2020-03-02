from enum import Enum


class DeviceStatus(Enum):
    NoCompany = 1
    Undeployed = 2
    WaitingForImage = 3
    ReadyForSpots = 4
    Deployed = 5