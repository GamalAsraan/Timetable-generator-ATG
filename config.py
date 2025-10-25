"""
Configuration settings for the Intelligent Timetable CSP system.
"""

# File paths
FILE_PATHS = {
    "courses": "data/raw/Courses.csv",
    "rooms": "data/raw/Rooms.csv",
    "instructors": "data/raw/Instructors.csv",
    "timeslots": "data/raw/TimeSlots.csv",
    "sections": "data/raw/sections_data.xlsx",
    "available_courses": "data/raw/Avilable_Course.csv"
}

# Output paths
OUTPUT_PATHS = {
    "timetable": "output/timetables/final_timetable.csv",
    "report": "output/reports/optimization_report.txt",
    "log": "output/logs/solver_log.txt"
}

# Solver configuration
SOLVER_CONFIG = {
    "max_group_capacity": 75,
    "optimization_iterations": 20000,
    "backtracking_timeout": 300,  # seconds
    "optimization_timeout": 600   # seconds
}

# Constraint weights for cost evaluation
CONSTRAINT_WEIGHTS = {
    "not_preferred_slot": 10,
    "not_preferred_instructor": 5,
    "preferred_instructor_reward": -20,
    "gap_penalty_small": 1,      # 1 slot gap
    "gap_penalty_medium": 3,     # 2 slot gap
    "gap_penalty_large": 5       # 3+ slot gap
}

# Room type exclusions for lectures
EXCLUDED_LECTURE_SPACES = {'Drawing Studio', 'Computer'}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "output/logs/solver_log.txt"
}
