# University Timetable Generator - Technical Report

## 1. Executive Summary
The University Timetable Generator is a sophisticated software solution designed to automate the complex process of scheduling university courses. By leveraging Artificial Intelligence (AI) and Constraint Satisfaction Problem (CSP) techniques, the system generates conflict-free timetables that optimize for instructor preferences, room utilization, and student schedules. The project has been recently refactored into a modular web application using **Streamlit**, providing a user-friendly interface for data management, configuration, and result visualization.

## 2. System Architecture
The application follows a clean separation of concerns, divided into a frontend user interface and a backend solver engine.

### 2.1 Frontend (`app.py`)
Built with **Streamlit**, the frontend serves as the interaction layer:
- **Data Ingestion**: Handles the upload of 6 required CSV/Excel files (Courses, Rooms, Instructors, TimeSlots, Sections, Available Courses).
- **Data Editor**: Provides an interactive spreadsheet-like interface for users to review and modify data before processing.
- **Configuration Dashboard**: Allows users to dynamically adjust optimization weights (e.g., penalties for gaps or building changes) via sliders.
- **Multi-Page Workflow**: Implements a state-managed flow:
    1.  **Configuration Page**: For setup and execution.
    2.  **Results Page**: For viewing, filtering, and downloading the generated timetable.

### 2.2 Backend (`solver_engine.py`)
Encapsulates the core logic and algorithmic intelligence:
- **DataIngestor**: Standardizes input data from Pandas DataFrames into internal model objects.
- **Domain Models**: Classes representing `Course`, `Room`, `Instructor`, `Section`, and `TimeSlot`.
- **Solver Logic**: Contains the implementation of the Backtracking and Simulated Annealing algorithms.

## 3. Algorithmic Approach
The timetabling problem is modeled as a **Constraint Satisfaction Problem (CSP)**.

### 3.1 Phase 1: Feasibility (Backtracking)
The first phase aims to find *any* valid solution that satisfies all hard constraints.
- **Variables**: Each class session (Lecture or Lab) is a variable.
- **Domains**: The domain of a variable consists of all valid tuples of `(TimeSlotSequence, Room, Instructor)`.
- **Hard Constraints**:
    - No double-booking of Instructors.
    - No double-booking of Rooms.
    - No double-booking of Student Groups (Sections).
    - Room capacity must meet or exceed student count.
    - Room type must match session type (e.g., Lab sessions in Lab rooms).
    - Instructor must be qualified for the course.
- **Algorithm**: A recursive **Backtracking Solver** with Minimum Remaining Values (MRV) heuristic is used to efficiently search the solution space.

### 3.2 Phase 2: Optimization (Simulated Annealing)
Once a feasible solution is found, the system optimizes it to improve quality based on soft constraints.
- **Objective Function**: A cost function calculates a penalty score based on:
    - **Gaps**: Penalties for 1-hour gaps in student schedules.
    - **Bad Times**: Penalties for very early or late slots.
    - **Building Changes**: Penalties for instructors moving between buildings on the same day.
    - **Load Imbalance**: Penalties for uneven daily teaching loads.
- **Algorithm**: **Simulated Annealing** explores the search space by making local moves (swapping assignments or moving a single assignment). It accepts worse solutions with a probability that decreases over time (Temperature), allowing it to escape local optima.
- **Smart Neighbor Generation**: The solver intelligently generates candidate moves by pre-calculating valid options, significantly speeding up convergence.

## 4. Key Features
- **Dynamic Weight Adjustment**: Users can prioritize different soft constraints (e.g., minimize gaps vs. minimize building changes) in real-time.
- **Interactive Results**:
    - **Category Views**: Switch between Instructor, Room, and Student Group perspectives.
    - **Advanced Filtering**: "Include" or "Exclude" specific entities (e.g., view only specific instructors).
    - **Robust Search**: Handles complex data like comma-separated student groups correctly.
- **Persistence**: Application state is preserved during interaction, preventing the need to re-run the solver when changing filters.

## 5. Usage Guide
1.  **Installation**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Execution**:
    ```bash
    streamlit run app.py
    ```
3.  **Workflow**:
    - Upload the required data files.
    - (Optional) Edit data in the preview tables.
    - Adjust optimization weights in the sidebar.
    - Click **Run Optimizer**.
    - View, filter, and download the results on the Results page.
