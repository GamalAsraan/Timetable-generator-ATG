"""
Data validation utilities.
"""

class DataValidator:
    """Validates loaded data for consistency and completeness."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_all(self, model_data):
        """Validate all loaded data."""
        self.errors = []
        self.warnings = []
        
        self._validate_courses(model_data.get('courses', {}))
        self._validate_rooms(model_data.get('rooms', {}))
        self._validate_instructors(model_data.get('instructors', {}))
        self._validate_timeslots(model_data.get('timeslots', {}))
        self._validate_sections(model_data.get('sections', {}))
        self._validate_available_courses(model_data.get('available_courses', []))
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_courses(self, courses):
        """Validate course data."""
        if not courses:
            self.errors.append("No courses loaded")
            return
        
        for course_id, course in courses.items():
            if course.lecture_duration < 0 or course.lab_duration < 0:
                self.errors.append(f"Course {course_id}: Invalid duration")
            if not course.name or course.name.strip() == "":
                self.warnings.append(f"Course {course_id}: Empty name")
    
    def _validate_rooms(self, rooms):
        """Validate room data."""
        if not rooms:
            self.errors.append("No rooms loaded")
            return
        
        for room_id, room in rooms.items():
            if room.capacity <= 0:
                self.errors.append(f"Room {room_id}: Invalid capacity")
    
    def _validate_instructors(self, instructors):
        """Validate instructor data."""
        if not instructors:
            self.errors.append("No instructors loaded")
            return
        
        for inst_id, instructor in instructors.items():
            if not instructor.qualified_courses:
                self.warnings.append(f"Instructor {inst_id}: No qualified courses")
    
    def _validate_timeslots(self, timeslots):
        """Validate timeslot data."""
        if not timeslots:
            self.errors.append("No timeslots loaded")
            return
    
    def _validate_sections(self, sections):
        """Validate section data."""
        if not sections:
            self.errors.append("No sections loaded")
            return
        
        for section_id, section in sections.items():
            if section.student_count <= 0:
                self.errors.append(f"Section {section_id}: Invalid student count")
    
    def _validate_available_courses(self, available_courses):
        """Validate available courses data."""
        if not available_courses:
            self.warnings.append("No available courses loaded")
            return
