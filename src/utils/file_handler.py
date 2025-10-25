"""
File handling utilities for CSV/Excel I/O.
"""

import pandas as pd
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from config import OUTPUT_PATHS


def save_solution_to_csv(solution, model_data, filename=None):
    """Converts the list of Assignment objects into a readable CSV."""
    if filename is None:
        filename = OUTPUT_PATHS['timetable']
    
    print(f"\n--- Saving solution to {filename} ---")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # We need the TimeSlot objects for start/end times
    timeslots_map = model_data['timeslots']
    
    output_data = []
    for assignment in solution:
        session = assignment.session
        
        # Get timeslot info
        first_slot_id = assignment.timeslot_sequence[0]
        last_slot_id = assignment.timeslot_sequence[-1]
        
        start_time = timeslots_map[first_slot_id].start_time
        end_time = timeslots_map[last_slot_id].end_time
        day = timeslots_map[first_slot_id].day
        
        # Get section info
        section_ids = ", ".join([s.section_id for s in session.sections])
        
        output_data.append({
            "Day": day,
            "StartTime": start_time,
            "EndTime": end_time,
            "CourseID": session.course.course_id,
            "CourseName": session.course.name,
            "Type": session.session_type,
            "Instructor": assignment.instructor.name,
            "Room": assignment.room.room_id,
            "Sections": section_ids,
            "StudentCount": session.total_student_count
        })
        
    # Create DataFrame and save
    df = pd.DataFrame(output_data)
    # Sort for readability
    df = df.sort_values(by=["Day", "StartTime"])
    
    try:
        df.to_csv(filename, index=False)
        print(f"Successfully saved timetable to {filename}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False


def load_timetable_from_csv(filename):
    """Load a timetable from CSV file."""
    try:
        df = pd.read_csv(filename)
        return df
    except Exception as e:
        print(f"Error loading timetable: {e}")
        return None


def save_optimization_report(solution, initial_cost, final_cost, iterations, filename=None):
    """Save optimization report to file."""
    if filename is None:
        filename = OUTPUT_PATHS['report']
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    report_content = f"""
Optimization Report
==================

Initial Cost: {initial_cost}
Final Cost: {final_cost}
Improvement: {initial_cost - final_cost} ({((initial_cost - final_cost) / initial_cost * 100):.2f}%)
Iterations: {iterations}
Total Assignments: {len(solution)}

Optimization completed successfully.
"""
    
    try:
        with open(filename, 'w') as f:
            f.write(report_content)
        print(f"Optimization report saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving report: {e}")
        return False
