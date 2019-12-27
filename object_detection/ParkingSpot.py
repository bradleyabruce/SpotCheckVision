class ParkingSpot:
    def __init__(self, parkingSpotID, openFlag, deviceID, topLeftXCoordinate, topLeftYCoordinate, bottomRightXCoordinate, bottomRightYCoordinate, occupiedCounter, hasMovement, updateDate):
        self.ParkingSpotID = parkingSpotID
        self.IsOpen = True
        self.DeviceID = deviceID
        self.TopLeftXCoordinate = topLeftXCoordinate
        self.TopLeftYCoordinate = topLeftYCoordinate
        self.BottomRightXCoordinate = bottomRightXCoordinate
        self.BottomRightYCoordinate = bottomRightYCoordinate
        self.OccupiedCounter = occupiedCounter
        self.HasMovement = hasMovement
        self.UpdateDate = updateDate


def decoder(obj):
    spot = ParkingSpot(obj['spotId'], obj['openFlag'], obj['deviceId'], obj['topLeftXCoordinate'], obj['topLeftYCoordinate'], obj['bottomRightXCoordinate'], obj['bottomRightYCoordinate'], 0, False, obj['updateDate'])
    return spot
