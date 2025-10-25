"""
Timetable state management for CSP solving.
"""

from dataclasses import dataclass


@dataclass
class Assignment:
    session: 'ClassSession'
    timeslot_sequence: list
    room: 'Room'
    instructor: 'Instructor'
    
    def __repr__(self):
        return (f"Assignment(Session={self.session.session_id}, "
                f"Course={self.session.course.course_id}, "
                f"Time={self.timeslot_sequence}, Room={self.room.room_id}, "
                f"Inst={self.instructor.instructor_id})")


class TimetableState:
    def __init__(self, model_data):
        self.instructor_schedule = {inst.instructor_id: set() for inst in model_data['instructors'].values()}
        self.room_schedule = {room.room_id: set() for room in model_data['rooms'].values()}
        self.section_schedule = {sec.section_id: set() for sec in model_data['sections'].values()}

    def is_consistent(self, session, timeslot_sequence, room, instructor):
        try:
            for slot_id in timeslot_sequence:
                if (slot_id in self.instructor_schedule[instructor.instructor_id] or
                    slot_id in self.room_schedule[room.room_id]):
                    return False
                for section in session.sections:
                    if slot_id in self.section_schedule[section.section_id]:
                        return False
            return True
        except KeyError as e:
            print(f"--- CRITICAL ERROR in TimetableState.is_consistent: {e} ---")
            return False

    def add_assignment(self, assignment):
        for slot_id in assignment.timeslot_sequence:
            self.instructor_schedule[assignment.instructor.instructor_id].add(slot_id)
            self.room_schedule[assignment.room.room_id].add(slot_id)
            for section in assignment.session.sections:
                self.section_schedule[section.section_id].add(slot_id)

    def remove_assignment(self, assignment):
        for slot_id in assignment.timeslot_sequence:
            self.instructor_schedule[assignment.instructor.instructor_id].remove(slot_id)
            self.room_schedule[assignment.room.room_id].remove(slot_id)
            for section in assignment.session.sections:
                self.section_schedule[section.section_id].remove(slot_id)
