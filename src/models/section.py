"""
Section model class.
"""

class Section:
    def __init__(self, section_id, department, level, specialization, student_count):
        self.section_id = section_id
        self.department = department
        self.level = int(level)
        self.specialization = specialization
        self.student_count = int(student_count)
    
    def __repr__(self):
        return f"Section(id={self.section_id}, level={self.level}, count={self.student_count})"
