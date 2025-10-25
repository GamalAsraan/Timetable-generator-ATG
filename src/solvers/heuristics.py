"""
Heuristic functions for CSP solving.
"""

class MRVHeuristic:
    """Minimum Remaining Values heuristic for variable selection."""
    
    @staticmethod
    def select_variable(unassigned_variables):
        """Select the variable with the smallest domain."""
        return min(unassigned_variables, key=lambda var: len(var.domain.timeslot_sequences) * 
                   len(var.domain.rooms) * len(var.domain.instructors))


class LCVHeuristic:
    """Least Constraining Value heuristic for value ordering."""
    
    @staticmethod
    def order_values(variable, state):
        """Order domain values by least constraining first."""
        all_combinations = []
        for time_seq in variable.domain.timeslot_sequences:
            for room in variable.domain.rooms:
                for inst in variable.domain.instructors:
                    all_combinations.append((time_seq, room, inst))
        
        def calculate_penalty(value_tuple):
            time_seq, room, inst = value_tuple
            penalty = 0
            
            # Penalty for not preferred slots
            for slot_id in time_seq:
                if slot_id in inst.not_preferred_slots:
                    penalty += 10
            
            # Penalty for not preferred instructor
            if inst.instructor_id not in variable.preferred_instructors and variable.preferred_instructors:
                penalty += 5
            
            # Reward for preferred instructor
            if inst.instructor_id in variable.preferred_instructors:
                penalty -= 20
                
            return penalty
            
        # Sort by penalty (lowest first)
        all_combinations.sort(key=calculate_penalty)
        return all_combinations


class DegreeHeuristic:
    """Degree heuristic for variable selection (selects variable with most constraints)."""
    
    @staticmethod
    def select_variable(unassigned_variables, state):
        """Select variable with most constraints with other unassigned variables."""
        def constraint_count(var):
            count = 0
            for other_var in unassigned_variables:
                if var != other_var:
                    # Check if they share sections (constraint)
                    if any(section in other_var.sections for section in var.sections):
                        count += 1
            return count
        
        return max(unassigned_variables, key=constraint_count)
