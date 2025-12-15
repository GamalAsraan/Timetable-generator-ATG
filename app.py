import streamlit as st
import pandas as pd
import solver_engine


# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="University Timetable Generator", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'config'
if 'results_data' not in st.session_state:
    st.session_state['results_data'] = None

st.title("🎓 University Timetable Generator")

# ==========================================
# PAGE 1: CONFIGURATION & UPLOAD
# ==========================================
if st.session_state['page'] == 'config':
    st.markdown("""
    Upload your data files, configure the optimization weights, and generate a conflict-free timetable.
    """)

    # --- SIDEBAR: CONFIGURATION ---
    st.sidebar.header("⚙️ Optimization Weights")
    st.sidebar.markdown("Adjust the penalties for soft constraints.")

    gap_penalty = st.sidebar.slider("Gap Penalty (1 hour)", 0, 10, 1, help="Penalty for 1-hour gaps between classes.")
    bad_time_penalty = st.sidebar.slider("Bad Time Penalty", 0, 10, 2, help="Penalty for early morning (before 9) or late evening (after 16) slots.")
    building_change_penalty = st.sidebar.slider("Building Change Penalty", 0, 20, 5, help="Penalty for instructors changing buildings within the same day.")
    daily_load_imbalance = st.sidebar.slider("Daily Load Imbalance", 0, 10, 2, help="Penalty multiplier for uneven daily teaching hours.")

    weights = {
        "gap_penalty": gap_penalty,
        "bad_time_penalty": bad_time_penalty,
        "building_change_penalty": building_change_penalty,
        "daily_load_imbalance": daily_load_imbalance
    }

    # --- MAIN AREA: DATA UPLOAD ---
    st.header("1. Upload Data")

    col1, col2 = st.columns(2)

    data_frames = {}

    def load_file(label, key, example_file, col):
        uploaded = col.file_uploader(label, type=['csv', 'xlsx'], key=key)
        if uploaded:
            try:
                if uploaded.name.endswith('.csv'):
                    df = pd.read_csv(uploaded)
                else:
                    df = pd.read_excel(uploaded)
                return df
            except Exception as e:
                st.error(f"Error loading {label}: {e}")
        return None

    with col1:
        data_frames['courses'] = load_file("Courses (CSV)", "courses", "Data/Courses.csv", st)
        data_frames['rooms'] = load_file("Rooms (CSV)", "rooms", "Data/Rooms.csv", st)
        data_frames['instructors'] = load_file("Instructors (CSV)", "instructors", "Data/Instructors.csv", st)

    with col2:
        data_frames['timeslots'] = load_file("TimeSlots (CSV)", "timeslots", "Data/TimeSlots.csv", st)
        data_frames['sections'] = load_file("Sections (Excel)", "sections", "Data/sections_data.xlsx", st)
        data_frames['available_courses'] = load_file("Available Courses (CSV)", "available_courses", "Data/Avilable_Course.csv", st)

    # --- DATA EDITOR ---
    st.header("2. Review & Edit Data")

    edited_data_frames = {}

    if all(df is not None for df in data_frames.values()):
        st.success("All files uploaded successfully!")
        
        with st.expander("View and Edit Uploaded Data"):
            tabs = st.tabs(["Courses", "Rooms", "Instructors", "TimeSlots", "Sections", "Available Courses"])
            
            with tabs[0]:
                edited_data_frames['courses'] = st.data_editor(data_frames['courses'], num_rows="dynamic", key="editor_courses")
            with tabs[1]:
                edited_data_frames['rooms'] = st.data_editor(data_frames['rooms'], num_rows="dynamic", key="editor_rooms")
            with tabs[2]:
                edited_data_frames['instructors'] = st.data_editor(data_frames['instructors'], num_rows="dynamic", key="editor_instructors")
            with tabs[3]:
                edited_data_frames['timeslots'] = st.data_editor(data_frames['timeslots'], num_rows="dynamic", key="editor_timeslots")
            with tabs[4]:
                edited_data_frames['sections'] = st.data_editor(data_frames['sections'], num_rows="dynamic", key="editor_sections")
            with tabs[5]:
                edited_data_frames['available_courses'] = st.data_editor(data_frames['available_courses'], num_rows="dynamic", key="editor_available")
    else:
        st.info("Please upload all 6 required files to proceed.")

    # --- RUN SOLVER ---
    st.header("3. Generate Timetable")

    if all(df is not None for df in data_frames.values()):
        if st.button("🚀 Run Optimizer"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def progress_callback(current_iter, total_iter, current_cost):
                progress = int((current_iter / total_iter) * 100)
                progress_bar.progress(progress)
                status_text.text(f"Optimization in progress... Iteration {current_iter}/{total_iter} | Best Cost: {current_cost}")

            try:
                with st.spinner("Solving... (This may take a minute)"):
                    # Use the EDITED data frames
                    final_df = solver_engine.run_web_solver(edited_data_frames, weights, progress_callback)
                    
                    # Store results and switch page
                    st.session_state['results_data'] = final_df
                    st.session_state['page'] = 'results'
                    st.rerun()
                    
            except Exception as e:
                st.error(f"An error occurred during solving: {e}")

# ==========================================
# PAGE 2: RESULTS & FILTERING
# ==========================================
else: # st.session_state['page'] == 'results'
    
    col_head1, col_head2 = st.columns([1, 5])
    with col_head1:
        if st.button("⬅️ Back to Config"):
            st.session_state['page'] = 'config'
            st.rerun()
    with col_head2:
        st.header("Generated Timetable Results")

    if st.session_state['results_data'] is not None:
        df = st.session_state['results_data']
        
        # --- CATEGORY SELECTION ---
        col_cat1, col_cat2 = st.columns(2)
        with col_cat1:
            category = st.radio("Select View Category:", ["Instructors", "Rooms", "Student Groups"], horizontal=True)
        with col_cat2:
            filter_mode = st.radio("Filter Mode:", ["Exclude Selected", "Include Only Selected"], horizontal=True)
        
        # --- DYNAMIC FILTERING ---
        filtered_df = df.copy()
        
        if category == "Instructors":
            all_items = sorted(df['Instructor'].unique())
            selected_items = st.multiselect(f"{filter_mode.split()[0]} Instructors:", options=all_items)
            
            if selected_items:
                if filter_mode == "Exclude Selected":
                    filtered_df = filtered_df[~filtered_df['Instructor'].isin(selected_items)]
                else:
                    filtered_df = filtered_df[filtered_df['Instructor'].isin(selected_items)]
                
        elif category == "Rooms":
            all_items = sorted(df['Room'].unique())
            selected_items = st.multiselect(f"{filter_mode.split()[0]} Rooms:", options=all_items)
            
            if selected_items:
                if filter_mode == "Exclude Selected":
                    filtered_df = filtered_df[~filtered_df['Room'].isin(selected_items)]
                else:
                    filtered_df = filtered_df[filtered_df['Room'].isin(selected_items)]
                
        elif category == "Student Groups":
            # 1. Extract unique individual sections from comma-separated strings
            unique_sections = set()
            for item in df['Sections'].dropna():
                parts = [p.strip() for p in item.split(',')]
                unique_sections.update(parts)
            all_items = sorted(list(unique_sections))
            
            selected_items = st.multiselect(f"{filter_mode.split()[0]} Student Groups:", options=all_items)
            
            if selected_items:
                # Helper function to check if any selected item is in the row's sections
                def check_match(row_val):
                    if pd.isna(row_val): return False
                    row_parts = [p.strip() for p in row_val.split(',')]
                    # Check intersection
                    return not set(row_parts).isdisjoint(selected_items)

                mask = filtered_df['Sections'].apply(check_match)
                
                if filter_mode == "Exclude Selected":
                    filtered_df = filtered_df[~mask]
                else:
                    filtered_df = filtered_df[mask]

        # --- DISPLAY ---
        st.dataframe(filtered_df, width='stretch')
        
        # --- DOWNLOAD ---
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Download {category} Schedule as CSV",
            data=csv,
            file_name=f'timetable_{category.lower().replace(" ", "_")}.csv',
            mime='text/csv',
        )
    else:
        st.error("No results found. Please go back and run the optimizer.")
