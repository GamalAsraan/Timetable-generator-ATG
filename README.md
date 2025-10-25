# Intelligent Timetable CSP System

A sophisticated Constraint Satisfaction Problem (CSP) solver for generating optimal university timetables using backtracking search and iterative optimization.

## Features

- **Two-Phase Solving**: Backtracking search for initial solution + iterative optimization for improvement
- **Advanced Heuristics**: MRV (Minimum Remaining Values), LCV (Least Constraining Value), and Degree heuristics
- **Soft Constraints**: Instructor preferences, time slot preferences, and student gap minimization
- **Modular Architecture**: Clean separation of concerns with well-organized codebase
- **Comprehensive Logging**: Detailed logging and reporting capabilities
- **Data Validation**: Robust data loading and validation system

## Project Structure

```
intelligent-timetable-csp/
│
├── README.md
├── requirements.txt
├── .gitignore
├── config.py                    # Configuration settings
│
├── data/                        # Input data files
│   ├── raw/                     # Original, immutable data
│   │   ├── Courses.csv
│   │   ├── Rooms.csv
│   │   ├── Instructors.csv
│   │   ├── TimeSlots.csv
│   │   ├── sections_data.xlsx
│   │   └── Avilable_Course.csv
│   │
│   └── processed/               # Cleaned/preprocessed data (optional)
│
├── output/                      # Generated timetables and reports
│   ├── timetables/
│   │   └── final_timetable.csv
│   ├── reports/
│   │   └── optimization_report.txt
│   └── logs/
│       └── solver_log.txt
│
├── src/                         # Source code
│   ├── __init__.py
│   │
│   ├── models/                  # Data model classes
│   │   ├── __init__.py
│   │   ├── course.py
│   │   ├── room.py
│   │   ├── instructor.py
│   │   ├── timeslot.py
│   │   ├── section.py
│   │   └── available_course.py
│   │
│   ├── data_loader/             # Data loading and validation
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── validator.py
│   │
│   ├── csp/                     # CSP core components
│   │   ├── __init__.py
│   │   ├── variable.py          # ClassSession, VariableGenerator
│   │   ├── domain.py            # Domain, DomainBuilder
│   │   ├── constraints.py       # Hard and soft constraint definitions
│   │   └── state.py             # TimetableState, Assignment
│   │
│   ├── solvers/                 # Solving algorithms
│   │   ├── __init__.py
│   │   ├── backtracking.py      # Phase 1: BacktrackingSolver
│   │   ├── optimizer.py         # Phase 2: IterativeSolver
│   │   ├── heuristics.py        # MRV, LCV, Degree heuristics
│   │   └── evaluator.py         # CostEvaluator
│   │
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── file_handler.py      # CSV/Excel I/O
│   │   ├── logger.py            # Logging utilities
│   │   └── visualizer.py        # Timetable visualization
│   │
│   └── ui/                      # User interface
│       ├── __init__.py
│       └── cli.py               # Command-line interface
│
├── tests/                       # Unit and integration tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_loader.py
│   ├── test_domain.py
│   ├── test_constraints.py
│   ├── test_backtracking.py
│   └── test_optimizer.py
│
├── notebooks/                   # Jupyter notebooks (for analysis)
│   ├── data_exploration.ipynb
│   └── results_analysis.ipynb
│
├── docs/                        # Documentation
│   ├── project_description.md
│   ├── csp_formulation.md
│   ├── algorithm_design.md
│   └── user_guide.md
│
└── main.py                      # Main entry point
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd intelligent-timetable-csp
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the timetable generator with default settings:

```bash
python main.py
```

### Advanced Usage

```bash
# Set custom parameters
python main.py --max-capacity 100 --iterations 50000 --output custom_timetable.csv

# Validate data only
python main.py --validate-only

# Enable verbose logging
python main.py --verbose
```

### Configuration

Edit `config.py` to customize:

- File paths for input data
- Solver parameters (max capacity, iterations, timeouts)
- Constraint weights for optimization
- Logging configuration

## Algorithm Overview

### Phase 1: Backtracking Search
- Uses MRV (Minimum Remaining Values) heuristic for variable selection
- Employs LCV (Least Constraining Value) heuristic for value ordering
- Implements soft constraint penalties for instructor preferences
- Generates initial valid solution respecting all hard constraints

### Phase 2: Iterative Optimization
- Hill-climbing metaheuristic for solution improvement
- Random swap operations between compatible assignments
- Cost evaluation based on soft constraints:
  - Instructor preference violations
  - Time slot preference violations
  - Student gap penalties
- Configurable number of optimization iterations

## Data Format

### Input Files

1. **Courses.csv**: Course definitions with lecture/lab durations
2. **Rooms.csv**: Room capacity and type information
3. **Instructors.csv**: Instructor qualifications and preferences
4. **TimeSlots.csv**: Available time slots
5. **sections_data.xlsx**: Student section information
6. **Avilable_Course.csv**: Course availability and preferences

### Output Files

- **final_timetable.csv**: Generated timetable
- **optimization_report.txt**: Optimization statistics
- **solver_log.txt**: Detailed execution log

## Hard Constraints

- **Capacity**: Room capacity must accommodate student count
- **Room Type**: Labs must use appropriate room types
- **Instructor Qualification**: Instructors must be qualified for courses
- **Time Conflicts**: No overlapping assignments for instructors, rooms, or sections

## Soft Constraints

- **Instructor Preferences**: Penalty for non-preferred instructors
- **Time Preferences**: Penalty for non-preferred time slots
- **Student Gaps**: Penalty for gaps between consecutive sessions
- **Room Utilization**: Preference for appropriate room types

## Performance

The system is designed to handle:
- Up to 100+ course sessions
- 50+ instructors
- 30+ rooms
- 20+ time slots
- Multiple student sections

Typical execution times:
- Phase 1 (Backtracking): 1-5 minutes
- Phase 2 (Optimization): 2-10 minutes (depending on iterations)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Constraint Satisfaction Problem theory and algorithms
- University timetable generation research
- Python optimization libraries and tools
