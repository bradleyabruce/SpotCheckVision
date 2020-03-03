class Spot:
    def __init__(self, spotID, isOpen, deviceID, topLeftXCoordinate, topLeftYCoordinate, bottomRightXCoordinate,
                 bottomRightYCoordinate, occupiedCounter, emptyCounter, updateDate):
        self.SpotID = spotID
        self.IsOpen = True
        self.DeviceID = deviceID
        self.TopLeftXCoordinate = topLeftXCoordinate
        self.TopLeftYCoordinate = topLeftYCoordinate
        self.BottomRightXCoordinate = bottomRightXCoordinate
        self.BottomRightYCoordinate = bottomRightYCoordinate
        self.OccupiedCounter = occupiedCounter
        self.EmptyCounter = emptyCounter
        self.UpdateDate = updateDate

    def decoder(obj):
        spot = Spot(obj['spotId'], obj['open'], obj['deviceId'], obj['topLeftXCoordinate'], obj['topLeftYCoordinate'],
                    obj['bottomRightXCoordinate'], obj['bottomRightYCoordinate'], 0, 0, obj['updateDate'])
        return spot
