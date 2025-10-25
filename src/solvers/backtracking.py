"""
Backtracking solver for Phase 1 of timetable generation.
"""

import time
from ..csp import TimetableState, Assignment


class BacktrackingSolver:
    def __init__(self, variables, model_data):
        self.unassigned_variables = list(variables)
        self.state = TimetableState(model_data)
        self.solution = []
        self.model_data = model_data

    def solve(self):
        print("\n--- Phase 1: Backtracking Solver Starting ---")
        start_time = time.time()
        
        self.unassigned_variables.sort(key=self.get_domain_size)
        
        solution_found = self.recursive_solve()
        
        end_time = time.time()
        print(f"--- Solver Finished in {end_time - start_time:.2f} seconds ---")
        
        if solution_found:
            print(f"SUCCESS: Found a valid timetable with {len(self.solution)} assignments.")
            return self.solution, self.state
        else:
            print("FAILURE: Could not find a valid solution.")
            return None, None

    def get_domain_size(self, var):
        d = var.domain
        return len(d.timeslot_sequences) * len(d.rooms) * len(d.instructors)

    def select_variable_mrv(self):
        """Select variable using Minimum Remaining Values heuristic."""
        self.unassigned_variables.sort(key=self.get_domain_size)
        return self.unassigned_variables.pop(0)

    def get_ordered_domain_values(self, var):
        """Get domain values ordered by LCV heuristic."""
        all_combinations = []
        for time_seq in var.domain.timeslot_sequences:
            for room in var.domain.rooms:
                for inst in var.domain.instructors:
                    all_combinations.append((time_seq, room, inst))
        
        # LCV / Soft Constraint Heuristic
        def calculate_penalty(value_tuple):
            time_seq, room, inst = value_tuple
            penalty = 0
            
            # 1. Penalty for Not Preferred Slot
            for slot_id in time_seq:
                if slot_id in inst.not_preferred_slots:
                    penalty += 10
            
            # 2. Penalty for Not Preferred Instructor
            if inst.instructor_id not in var.preferred_instructors and var.preferred_instructors:
                penalty += 5
            
            # 3. Reward for Preferred Instructor
            if inst.instructor_id in var.preferred_instructors:
                penalty -= 20
                
            return penalty
            
        # Sort combinations: lowest penalty score first
        all_combinations.sort(key=calculate_penalty)
        return all_combinations

    def recursive_solve(self):
        if not self.unassigned_variables:
            return True 
        
        var = self.unassigned_variables.pop(0) 

        for time_seq, room, inst in self.get_ordered_domain_values(var):
            if self.state.is_consistent(var, time_seq, room, inst):
                assignment = Assignment(var, time_seq, room, inst)
                self.state.add_assignment(assignment)
                self.solution.append(assignment)
                
                if self.recursive_solve():
                    return True 
                
                self.solution.pop()
                self.state.remove_assignment(assignment)
        
        self.unassigned_variables.insert(0, var)
        return False
