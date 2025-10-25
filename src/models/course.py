"""
Course model class.
"""

class Course:
    def __init__(self, course_id, name, lecture_duration, lab_duration, lab_type):
        self.course_id = course_id
        self.name = name
        self.lecture_duration = int(lecture_duration)
        self.lab_duration = int(lab_duration)
        self.lab_type = lab_type
    
    def __repr__(self):
        return f"Course(id={self.course_id}, name={self.name})"
