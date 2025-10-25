"""
Cost evaluator for timetable optimization.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from config import CONSTRAINT_WEIGHTS


class CostEvaluator:
    """Calculates the total penalty ('cost') of a complete solution."""
    
    def __init__(self, model_data):
        self.model_data = model_data
        # Pre-build day-to-slots map for gap calculation
        self.slots_by_day = {}
        for slot in model_data['timeslots'].values():
            if slot.day not in self.slots_by_day:
                self.slots_by_day[slot.day] = []
            self.slots_by_day[slot.day].append(slot.slot_id)
        for day in self.slots_by_day:
            self.slots_by_day[day].sort()

    def calculate_total_cost(self, solution, state):
        total_penalty = 0
        
        # 1. Instructor Preference Penalties
        for assignment in solution:
            inst = assignment.instructor
            # A. Not Preferred Slot
            for slot_id in assignment.timeslot_sequence:
                if slot_id in inst.not_preferred_slots:
                    total_penalty += CONSTRAINT_WEIGHTS['not_preferred_slot']
            
            # B. Not Preferred Instructor
            session = assignment.session
            if session.preferred_instructors and inst.instructor_id not in session.preferred_instructors:
                total_penalty += CONSTRAINT_WEIGHTS['not_preferred_instructor']
                
        # 2. Student Gap Penalties
        for section in self.model_data['sections'].values():
            total_penalty += self._calculate_gaps_for_section(section.section_id, state)
            
        return total_penalty

    def _calculate_gaps_for_section(self, section_id, state):
        """Calculates gap penalties for a single section."""
        gap_penalty = 0
        busy_slots = state.section_schedule[section_id]
        if not busy_slots:
            return 0
            
        for day, slot_ids_in_day in self.slots_by_day.items():
            # Get the slots this section is busy *on this day*
            day_busy_slots = [s for s in slot_ids_in_day if s in busy_slots]
            day_busy_slots.sort()
            
            # Find gaps between consecutive sessions
            for i in range(len(day_busy_slots) - 1):
                slot_after = day_busy_slots[i+1]
                slot_before = day_busy_slots[i]
                
                gap_size = slot_after - slot_before
                
                if gap_size == 2:  # 1 slot gap
                    gap_penalty += CONSTRAINT_WEIGHTS['gap_penalty_small']
                elif gap_size == 3:  # 2 slot gap
                    gap_penalty += CONSTRAINT_WEIGHTS['gap_penalty_medium']
                elif gap_size > 3:  # 3+ slot gap
                    gap_penalty += CONSTRAINT_WEIGHTS['gap_penalty_large']
        
        return gap_penalty
