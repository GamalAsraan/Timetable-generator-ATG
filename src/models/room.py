"""
Room model class.
"""

class Room:
    def __init__(self, room_id, capacity, room_type, type_of_space):
        self.room_id = room_id
        self.capacity = int(capacity)
        self.room_type = room_type
        self.type_of_space = type_of_space
    
    def __repr__(self):
        return f"Room(id={self.room_id}, capacity={self.capacity}, type={self.type_of_space})"
