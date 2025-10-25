"""
AvailableCourse model class.
"""

class AvailableCourse:
    def __init__(self, department, level, specialization, course_id, preferred_prof, preferred_assi_set):
        self.department = department
        self.level = int(level)
        self.specialization = specialization
        self.course_id = course_id
        self.preferred_prof = preferred_prof
        self.preferred_assi = preferred_assi_set
    
    def __repr__(self):
        return f"Available(level={self.level}, course={self.course_id}, prof={self.preferred_prof})"
