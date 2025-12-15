# University Timetable Generator

A comprehensive automated timetable generation system using Constraint Satisfaction Problems (CSP) and Simulated Annealing optimization.

## 🚀 Features

- **Automated Scheduling**: Generates conflict-free timetables for courses, instructors, and rooms.
- **Optimization**: Uses Simulated Annealing to optimize for soft constraints like:
  - Minimizing gaps between classes.
  - Avoiding early morning/late evening slots.
  - Reducing instructor building changes.
  - Balancing daily teaching loads.
- **Interactive Web Interface**: Built with Streamlit for easy data upload, configuration, and result visualization.
- **Excel & HTML Export**: Export generated timetables for further use.

## 📂 Project Structure

- **`app.py`**: The main Streamlit web application.
- **`solver_engine.py`**: Core logic for CSP and optimization algorithms.
- **`Data/`**: Directory containing input CSV/Excel files (Courses, Instructors, Rooms, etc.).
- **`utils/`**: Helper scripts for specific export tasks.
  - `generate_timetable.py`: Generates formatted Excel/HTML timetables for student levels.
  - `instructor_timetable.py`: Generates individual timetables for instructors.
- **`docs/`**: Project documentation.

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd Timetable-generator-ATG
    ```

2.  **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Usage

### Running the Web App
To start the interactive timetable generator:

```bash
streamlit run app.py
```

1.  **Upload Data**: Upload your CSV/Excel files in the "Upload Data" section.
2.  **Configure**: Adjust optimization weights in the sidebar.
3.  **Run**: Click "Run Optimizer" to generate the timetable.
4.  **View & Export**: Filter results by Instructor, Room, or Student Group and download as CSV.

### Generating Formatted Reports
You can use the utility scripts to generate detailed Excel/HTML reports.

**Student Timetables:**
```bash
python -m utils.generate_timetable
```

**Instructor Timetables:**
```bash
python -m utils.instructor_timetable
```

## 📋 Requirements
- Python 3.8+
- pandas
- streamlit
- openpyxl

## 📝 License
[MIT](LICENSE)
