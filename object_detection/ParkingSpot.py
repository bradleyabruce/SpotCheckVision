class ParkingSpot:
    def __init__(self, parkingSpotID, openFlag, deviceID, topLeftXCoordinate, topLeftYCoordinate, bottomRightXCoordinate, bottomRightYCoordinate, occupiedCounter, updateDate):
        self.ParkingSpotID = parkingSpotID
        self.IsOpen = openFlag
        self.DeviceID = deviceID
        self.TopLeftXCoordinate = topLeftXCoordinate
        self.TopLeftYCoordinate = topLeftYCoordinate
        self.BottomRightXCoordinate = bottomRightXCoordinate
        self.BottomRightYCoordinate = bottomRightYCoordinate
        self.OccupiedCounter = occupiedCounter
        self.UpdateDate = updateDate