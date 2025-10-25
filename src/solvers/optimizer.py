"""
Iterative optimizer for Phase 2 of timetable generation.
"""

import time
import random
import copy
from ..csp import Assignment


class IterativeSolver:
    """
    Phase 2: Takes a valid solution and tries to improve it
    using a simple hill-climbing metaheuristic.
    """
    def __init__(self, solution, state, evaluator, model_data, iterations=10000):
        self.current_solution = solution  # List of Assignments
        self.current_state = state  # TimetableState object
        self.evaluator = evaluator
        self.model_data = model_data
        self.iterations = iterations
        self.current_cost = evaluator.calculate_total_cost(solution, state)

    def optimize(self):
        print(f"\n--- Phase 2: Iterative Optimizer Starting ---")
        print(f"Initial Cost: {self.current_cost}")
        start_time = time.time()
        
        for i in range(self.iterations):
            if i % 2000 == 0:
                print(f"Iteration {i}...")

            # 1. Generate a "neighbor" solution
            neighbor_solution, neighbor_state = self.generate_neighbor()
            if neighbor_solution is None:
                continue  # Could not find a valid swap

            # 2. Evaluate the neighbor
            new_cost = self.evaluator.calculate_total_cost(neighbor_solution, neighbor_state)

            # 3. Decide to accept (Hill Climbing: only accept better solutions)
            if new_cost < self.current_cost:
                self.current_solution = neighbor_solution
                self.current_state = neighbor_state
                self.current_cost = new_cost
                print(f"  > Improvement found! New Cost: {new_cost} (Iteration {i})")

        end_time = time.time()
        print(f"--- Optimizer Finished in {end_time - start_time:.2f} seconds ---")
        print(f"Final Optimized Cost: {self.current_cost}")
        return self.current_solution

    def generate_neighbor(self):
        """Tries to make one valid swap."""
        
        # Pick two random assignments to try and swap
        if len(self.current_solution) < 2:
            return None, None
            
        a1, a2 = random.sample(self.current_solution, 2)
        
        # We can only swap if they have the same duration
        if a1.session.duration_slots != a2.session.duration_slots:
            return None, None
            
        # Create copies to work with
        neighbor_state = copy.deepcopy(self.current_state)
        neighbor_solution = list(self.current_solution)  # Shallow copy of list
        
        # --- The Swap ---
        # 1. Remove both from state
        neighbor_state.remove_assignment(a1)
        neighbor_state.remove_assignment(a2)
        
        # 2. Create the two "swapped" potential assignments
        new_a1 = Assignment(a1.session, a2.timeslot_sequence, a2.room, a2.instructor)
        new_a2 = Assignment(a2.session, a1.timeslot_sequence, a1.room, a1.instructor)

        # 3. Check if the swap is valid (respects hard constraints)
        valid_a1 = (new_a1.instructor in a1.session.domain.instructors and
                   new_a1.room in a1.session.domain.rooms and
                   new_a1.timeslot_sequence in a1.session.domain.timeslot_sequences and
                   neighbor_state.is_consistent(new_a1.session, new_a1.timeslot_sequence, new_a1.room, new_a1.instructor))
        
        if not valid_a1:
            return None, None  # Swap failed

        # Add new_a1 to the state so we can check new_a2 against it
        neighbor_state.add_assignment(new_a1)

        # Check if new_a2 is valid for session a2
        valid_a2 = (new_a2.instructor in a2.session.domain.instructors and
                   new_a2.room in a2.session.domain.rooms and
                   new_a2.timeslot_sequence in a2.session.domain.timeslot_sequences and
                   neighbor_state.is_consistent(new_a2.session, new_a2.timeslot_sequence, new_a2.room, new_a2.instructor))

        if not valid_a2:
            return None, None  # Swap failed

        # 4. If both are valid, finalize the neighbor
        neighbor_state.add_assignment(new_a2)
        
        # Update the neighbor solution list
        neighbor_solution.remove(a1)
        neighbor_solution.remove(a2)
        neighbor_solution.append(new_a1)
        neighbor_solution.append(new_a2)
        
        return neighbor_solution, neighbor_state
