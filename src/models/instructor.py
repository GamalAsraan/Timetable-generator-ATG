"""
Instructor model class.
"""

class Instructor:
    def __init__(self, instructor_id, name, qualified_courses_set, not_preferred_slots_set):
        self.instructor_id = instructor_id
        self.name = name
        self.qualified_courses = qualified_courses_set
        self.not_preferred_slots = not_preferred_slots_set
    
    def __repr__(self):
        return f"Instructor(id={self.instructor_id}, name={self.name})"
