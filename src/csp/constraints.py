"""
Constraint definitions for the timetable CSP.
"""

class ConstraintChecker:
    """Checks hard and soft constraints for timetable assignments."""
    
    def __init__(self, model_data):
        self.model_data = model_data
    
    def check_hard_constraints(self, assignment, state):
        """Check if an assignment violates any hard constraints."""
        session = assignment.session
        timeslot_sequence = assignment.timeslot_sequence
        room = assignment.room
        instructor = assignment.instructor
        
        # 1. Capacity constraint
        if room.capacity < session.total_student_count:
            return False, "Room capacity insufficient"
        
        # 2. Room type constraint
        if session.session_type == 'Lab' and room.type_of_space != session.course.lab_type:
            return False, "Room type mismatch for lab"
        
        # 3. Instructor qualification constraint
        if session.course.course_id not in instructor.qualified_courses:
            return False, "Instructor not qualified for course"
        
        # 4. Time conflict constraint
        if not state.is_consistent(session, timeslot_sequence, room, instructor):
            return False, "Time conflict detected"
        
        return True, "All hard constraints satisfied"
    
    def check_soft_constraints(self, assignment):
        """Check soft constraints and return penalty score."""
        penalty = 0
        session = assignment.session
        instructor = assignment.instructor
        timeslot_sequence = assignment.timeslot_sequence
        
        # 1. Not preferred time slot penalty
        for slot_id in timeslot_sequence:
            if slot_id in instructor.not_preferred_slots:
                penalty += 10
        
        # 2. Not preferred instructor penalty
        if (session.preferred_instructors and 
            instructor.instructor_id not in session.preferred_instructors):
            penalty += 5
        
        # 3. Preferred instructor reward
        if instructor.instructor_id in session.preferred_instructors:
            penalty -= 20
        
        return penalty
