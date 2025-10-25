"""
Data model classes for the timetable CSP system.
"""

from .course import Course
from .room import Room
from .instructor import Instructor
from .timeslot import TimeSlot
from .section import Section
from .available_course import AvailableCourse

__all__ = [
    'Course',
    'Room', 
    'Instructor',
    'TimeSlot',
    'Section',
    'AvailableCourse'
]
