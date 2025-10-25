"""
TimeSlot model class.
"""

class TimeSlot:
    def __init__(self, slot_id, day, start_time, end_time):
        self.slot_id = int(slot_id)
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
    
    def __repr__(self):
        return f"TimeSlot(id={self.slot_id}, day={self.day}, time={self.start_time})"
