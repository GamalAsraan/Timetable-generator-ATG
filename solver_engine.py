import pandas as pd
import ast
import math
import time
import random
import copy
from dataclasses import dataclass

# --- DEFAULT CONFIGURATION ---
DEFAULT_OPTIMIZATION_WEIGHTS = {
    "gap_penalty": 1,
    "bad_time_penalty": 2,
    "building_change_penalty": 5,
    "daily_load_imbalance": 2
}

# --- DATA MODEL CLASSES ---

class Course:
    def __init__(self, course_id, name, lecture_duration, lab_duration, lab_type):
        self.course_id = course_id
        self.name = name
        self.lecture_duration = int(lecture_duration)
        self.lab_duration = int(lab_duration)
        self.lab_type = lab_type
    def __repr__(self):
        return f"Course(id={self.course_id}, name={self.name})"

class Room:
    def __init__(self, room_id, capacity, room_type, type_of_space):
        self.room_id = room_id
        self.capacity = int(capacity)
        self.room_type = room_type
        self.type_of_space = type_of_space
    def __repr__(self):
        return f"Room(id={self.room_id}, capacity={self.capacity}, type={self.type_of_space})"

class Instructor:
    def __init__(self, instructor_id, name, qualified_courses_set, not_preferred_slots_set):
        self.instructor_id = instructor_id
        self.name = name
        self.qualified_courses = qualified_courses_set
        self.not_preferred_slots = not_preferred_slots_set
    def __repr__(self):
        return f"Instructor(id={self.instructor_id}, name={self.name})"

class TimeSlot:
    def __init__(self, slot_id, day, start_time, end_time):
        self.slot_id = int(slot_id)
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
    def __repr__(self):
        return f"TimeSlot(id={self.slot_id}, day={self.day}, time={self.start_time})"

class Section:
    def __init__(self, section_id, department, level, specialization, student_count):
        self.section_id = section_id
        self.department = department
        self.level = int(level)
        self.specialization = specialization
        self.student_count = int(student_count)
    def __repr__(self):
        return f"Section(id={self.section_id}, level={self.level}, count={self.student_count})"

class AvailableCourse:
    def __init__(self, department, level, specialization, course_id, preferred_prof, preferred_assi_set):
        self.department = department
        self.level = int(level)
        self.specialization = specialization
        self.course_id = course_id
        self.preferred_prof = preferred_prof
        self.preferred_assi = preferred_assi_set
    def __repr__(self):
        return f"Available(level={self.level}, course={self.course_id}, prof={self.preferred_prof})"

# --- DATA INGESTOR CLASS (Replaces DataLoader) ---

class DataIngestor:
    def __init__(self, data_frames):
        """
        data_frames: Dictionary of Pandas DataFrames with keys:
        'courses', 'rooms', 'instructors', 'timeslots', 'sections', 'available_courses'
        """
        self.data_frames = data_frames
        self.model_data = {}
    
    def ingest_all(self):
        print("Ingesting data from DataFrames...")
        try:
            self.model_data['courses'] = self._load_courses()
            self.model_data['rooms'] = self._load_rooms()
            self.model_data['instructors'] = self._load_instructors()
            slots_dict, slots_df = self._load_timeslots()
            self.model_data['timeslots'] = slots_dict
            self.model_data['timeslots_df'] = slots_df
            self.model_data['sections'] = self._load_sections()
            self.model_data['available_courses'] = self._load_available_courses()
            print("All data ingested and model objects created.")
            return self.model_data
        except Exception as e:
            print(f"Error during data ingestion: {e}")
            raise e

    def _load_courses(self):
        df = self.data_frames['courses']
        courses_dict = {}
        for row in df.to_dict('records'):
            course_id_clean = str(row['CourseID']).strip()
            course = Course(course_id_clean, row['CourseName'], row['Lecture'], row['Lab'], row['Lab_Type'])
            courses_dict[course.course_id] = course
        return courses_dict

    def _load_rooms(self):
        df = self.data_frames['rooms']
        return {row['RoomID']: Room(row['RoomID'], row['Capacity'], row['Type'], row['Type_of_Space']) for row in df.to_dict('records')}

    def _load_instructors(self):
        df = self.data_frames['instructors']
        instructors_dict = {}
        for row in df.to_dict('records'):
            qualified = set(c.strip() for c in str(row['QualifiedCourses']).split(','))
            not_preferred = set()
            try:
                not_preferred_list = ast.literal_eval(str(row['Not_PreferredSlots']))
                if isinstance(not_preferred_list, list): not_preferred = set(not_preferred_list)
            except Exception: pass
            instructors_dict[row['InstructorID']] = Instructor(row['InstructorID'], row['Name'], qualified, not_preferred)
        return instructors_dict

    def _load_timeslots(self):
        df = self.data_frames['timeslots']
        df = df.sort_values(by='ID').reset_index(drop=True)
        timeslots_dict = {row['ID']: TimeSlot(row['ID'], row['Day'], row['StartTime'], row['EndTime']) for row in df.to_dict('records')}
        return timeslots_dict, df

    def _load_sections(self):
        df = self.data_frames['sections']
        return {row['SectionID']: Section(row['SectionID'], row['Department'], row['Level'], row['Specialization'], row['StudentCount']) for row in df.to_dict('records')}

    def _load_available_courses(self):
        df = self.data_frames['available_courses']
        available_list = []
        for row in df.to_dict('records'):
            prof = row['preferred_Prof'] if pd.notna(row['preferred_Prof']) else None
            assi_set = set()
            assi_str = str(row['preferred_Assi'])
            if pd.notna(assi_str) and assi_str.lower() != 'nan':
                 assi_set = set(c.strip() for c in assi_str.split(','))
            course_id_clean = str(row['CourseID']).strip()
            available_list.append(AvailableCourse(row['Department'], row['Level'], row['Specialization'], course_id_clean, prof, assi_set))
        return available_list

# --- CORE LOGIC CLASSES ---

class ClassSession:
    _session_counter = 0
    def __init__(self, course, session_type, duration_slots):
        ClassSession._session_counter += 1
        self.session_id = f"S{ClassSession._session_counter}"
        self.course, self.session_type, self.duration_slots = course, session_type, duration_slots
        self.sections, self.preferred_instructors = [], set()
        self.total_student_count, self.is_small_group = 0, False
        self.domain = None
    def add_section(self, section):
        if section not in self.sections:
            self.sections.append(section)
            self.total_student_count += section.student_count
    def set_small_group_flag(self, max_capacity):
        self.is_small_group = (self.total_student_count < max_capacity)
    def get_group_name(self):
        return self.sections[0].section_id if self.session_type == 'Lab' else f"Group ({','.join([s.section_id for s in self.sections])})"
    def __repr__(self):
        return f"ClassSession(id={self.session_id}, desc='{self.session_type[:3].upper()}-{self.course.course_id}', students={self.total_student_count})"

class VariableGenerator:
    def __init__(self, model_data, max_group_capacity=75):
        self.model_data, self.max_capacity = model_data, max_group_capacity
        self.all_variables = []
    def generate_all_variables(self):
        ClassSession._session_counter = 0
        for req in self.model_data['available_courses']:
            try:
                course_obj = self.model_data['courses'][req.course_id]
            except KeyError: continue
            matching_sections = [sec for sec in self.model_data['sections'].values() if
                                 (sec.department == req.department and sec.level == req.level and
                                  (req.specialization == 'Core' or req.specialization == sec.specialization))]
            if not matching_sections: continue
            if course_obj.lecture_duration > 0: self._create_lecture_variables(course_obj, matching_sections, req)
            if course_obj.lab_duration > 0: self._create_lab_variables(course_obj, matching_sections, req)
        return self.all_variables
    def _create_lecture_variables(self, course_obj, sections, request):
        sections_sorted = sorted(sections, key=lambda s: s.section_id)
        current_group = None
        for section in sections_sorted:
            if current_group is None or (current_group.total_student_count + section.student_count) > self.max_capacity:
                if current_group:
                    current_group.set_small_group_flag(self.max_capacity)
                    self.all_variables.append(current_group)
                current_group = ClassSession(course_obj, 'Lecture', course_obj.lecture_duration)
                if request.preferred_prof: current_group.preferred_instructors.add(request.preferred_prof)
            current_group.add_section(section)
        if current_group:
            current_group.set_small_group_flag(self.max_capacity)
            self.all_variables.append(current_group)
    def _create_lab_variables(self, course_obj, sections, request):
        for section in sections:
            lab_session = ClassSession(course_obj, 'Lab', course_obj.lab_duration)
            lab_session.add_section(section)
            lab_session.set_small_group_flag(self.max_capacity)
            lab_session.preferred_instructors = request.preferred_assi
            self.all_variables.append(lab_session)

class Domain:
    def __init__(self, session_variable, model_data):
        self.variable = session_variable
        self.timeslot_sequences = self._generate_consecutive_sequences(
            model_data['timeslots_df'], session_variable.duration_slots)
        self.rooms = self._filter_rooms(
            session_variable, model_data['rooms'])
        self.instructors = self._filter_instructors(
            session_variable, model_data['instructors'])
    def _generate_consecutive_sequences(self, all_timeslots_df, duration):
        sequences, day_slots = [], {}
        for row in all_timeslots_df.sort_values(by='ID').to_dict('records'):
            day = row['Day']
            if day not in day_slots: day_slots[day] = []
            day_slots[day].append(row['ID'])
        for day in day_slots:
            slots = day_slots[day]
            for i in range(len(slots) - duration + 1):
                sequence = slots[i : i + duration]
                if all(sequence[j+1] == sequence[j] + 1 for j in range(len(sequence) - 1)):
                    sequences.append(sequence)
        return sequences
    def _filter_rooms(self, session, all_rooms):
        valid_rooms, EXCLUDED_LECTURE_SPACES = [], {'Drawing Studio', 'Computer'}
        for room in all_rooms.values():
            if room.capacity < session.total_student_count: continue
            if session.session_type == 'Lab':
                if room.type_of_space != session.course.lab_type: continue
            elif session.session_type == 'Lecture':
                if room.type_of_space in EXCLUDED_LECTURE_SPACES: continue
                if not session.is_small_group and room.room_type != 'Lecture': continue
            valid_rooms.append(room)
        return valid_rooms
    def _filter_instructors(self, session, all_instructors):
        course_id = session.course.course_id
        if session.preferred_instructors:
            candidates = [inst for inst in all_instructors.values() if inst.instructor_id in session.preferred_instructors]
            if candidates:
                return candidates
        return [inst for inst in all_instructors.values() if course_id in inst.qualified_courses]
    def __repr__(self):
        return (f"Domain for {self.variable.session_id}: "
                f"T={len(self.timeslot_sequences)}, R={len(self.rooms)}, I={len(self.instructors)}")

class DomainBuilder:
    def __init__(self, model_data):
        self.model_data = model_data
    def build_all_domains(self, variables):
        unsolvable_count = 0
        for var in variables:
            var.domain = Domain(var, self.model_data)
            if not var.domain.timeslot_sequences or not var.domain.rooms or not var.domain.instructors:
                unsolvable_count += 1
        return unsolvable_count

@dataclass
class Assignment:
    session: ClassSession
    timeslot_sequence: list
    room: Room
    instructor: Instructor
    
    def __repr__(self):
        return (f"Assignment(Session={self.session.session_id}, "
                f"Course={self.session.course.course_id}, "
                f"Time={self.timeslot_sequence}, Room={self.room.room_id}, "
                f"Inst={self.instructor.instructor_id})")

class TimetableState:
    def __init__(self, model_data):
        self.instructor_schedule = {inst.instructor_id: set() for inst in model_data['instructors'].values()}
        self.room_schedule = {room.room_id: set() for room in model_data['rooms'].values()}
        self.section_schedule = {sec.section_id: set() for sec in model_data['sections'].values()}

    def is_consistent(self, session, timeslot_sequence, room, instructor):
        try:
            for slot_id in timeslot_sequence:
                if (slot_id in self.instructor_schedule[instructor.instructor_id] or
                    slot_id in self.room_schedule[room.room_id]):
                    return False
                for section in session.sections:
                    if slot_id in self.section_schedule[section.section_id]:
                        return False
            return True
        except KeyError as e:
            print(f"--- CRITICAL ERROR in TimetableState.is_consistent: {e} ---")
            return False

    def add_assignment(self, assignment):
        for slot_id in assignment.timeslot_sequence:
            self.instructor_schedule[assignment.instructor.instructor_id].add(slot_id)
            self.room_schedule[assignment.room.room_id].add(slot_id)
            for section in assignment.session.sections:
                self.section_schedule[section.section_id].add(slot_id)

    def remove_assignment(self, assignment):
        for slot_id in assignment.timeslot_sequence:
            self.instructor_schedule[assignment.instructor.instructor_id].remove(slot_id)
            self.room_schedule[assignment.room.room_id].remove(slot_id)
            for section in assignment.session.sections:
                self.section_schedule[section.section_id].remove(slot_id)

class BacktrackingSolver:
    def __init__(self, variables, model_data):
        self.unassigned_variables = list(variables)
        self.state = TimetableState(model_data)
        self.solution = []
        self.model_data = model_data
        self.nodes_visited = 0

    def solve(self):
        self.unassigned_variables.sort(key=self.get_domain_size)
        solution_found = self.recursive_solve()
        if solution_found:
            return self.solution, self.state
        else:
            return None, None

    def get_domain_size(self, var):
        d = var.domain
        return len(d.timeslot_sequences) * len(d.rooms) * len(d.instructors)

    def get_ordered_domain_values(self, var):
        all_combinations = []
        for time_seq in var.domain.timeslot_sequences:
            for inst in var.domain.instructors:
                if any(slot_id in inst.not_preferred_slots for slot_id in time_seq):
                    continue 
                for room in var.domain.rooms:
                    all_combinations.append((time_seq, room, inst))
        
        def heuristic_score(value_tuple):
            _, _, inst = value_tuple
            score = 0
            if inst.instructor_id in var.preferred_instructors:
                score -= 10
            return score
            
        all_combinations.sort(key=heuristic_score)
        return all_combinations

    def recursive_solve(self):
        self.nodes_visited += 1
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

class CostEvaluator:
    def __init__(self, model_data, weights=None):
        self.model_data = model_data
        self.weights = weights if weights else DEFAULT_OPTIMIZATION_WEIGHTS
        
        self.early_late_slots = set()
        for slot in model_data['timeslots'].values():
            start_hour = int(slot.start_time.split(':')[0])
            end_hour = int(slot.end_time.split(':')[0])
            if start_hour < 9: self.early_late_slots.add(slot.slot_id)
            elif end_hour >= 16: self.early_late_slots.add(slot.slot_id)

        self.slots_by_day = {}
        for slot in model_data['timeslots'].values():
            if slot.day not in self.slots_by_day: self.slots_by_day[slot.day] = []
            self.slots_by_day[slot.day].append(slot.slot_id)
        for d in self.slots_by_day: self.slots_by_day[d].sort()

    def calculate_total_cost(self, solution, state):
        total_penalty = 0
        inst_assignments = {} 
        
        for assignment in solution:
            inst_id = assignment.instructor.instructor_id
            if inst_id not in inst_assignments: inst_assignments[inst_id] = []
            inst_assignments[inst_id].append(assignment)
            
            for slot_id in assignment.timeslot_sequence:
                if slot_id in self.early_late_slots:
                    total_penalty += self.weights["bad_time_penalty"]

        for inst_id, assigns in inst_assignments.items():
            assigns.sort(key=lambda a: a.timeslot_sequence[0])
            for i in range(len(assigns) - 1):
                curr = assigns[i]
                next_a = assigns[i+1]
                curr_day = self.model_data['timeslots'][curr.timeslot_sequence[0]].day
                next_day = self.model_data['timeslots'][next_a.timeslot_sequence[0]].day
                
                if curr_day == next_day:
                    b1 = curr.room.room_id.split()[0]
                    b2 = next_a.room.room_id.split()[0]
                    if b1 != b2:
                        total_penalty += self.weights["building_change_penalty"]

        for section in self.model_data['sections'].values():
            sec_schedule = state.section_schedule[section.section_id]
            total_penalty += self._calculate_gaps(sec_schedule)
            
            daily_load = []
            for day, day_slots in self.slots_by_day.items():
                hours = sum(1 for s in day_slots if s in sec_schedule)
                daily_load.append(hours)
            
            if daily_load:
                load_imbalance = max(daily_load) - min(daily_load)
                if load_imbalance > 3:
                    total_penalty += (load_imbalance * self.weights["daily_load_imbalance"])

        return total_penalty

    def _calculate_gaps(self, busy_slots):
        gap_penalty = 0
        if not busy_slots: return 0
        for day, slot_ids_in_day in self.slots_by_day.items():
            day_busy = [s for s in slot_ids_in_day if s in busy_slots]
            day_busy.sort()
            for i in range(len(day_busy) - 1):
                gap = day_busy[i+1] - day_busy[i]
                if gap == 2: gap_penalty += self.weights["gap_penalty"]
                elif gap == 3: gap_penalty += (self.weights["gap_penalty"] * 3)
                elif gap > 3: gap_penalty += (self.weights["gap_penalty"] * 5)
        return gap_penalty

class SimulatedAnnealingSolver:
    def __init__(self, solution, state, evaluator, model_data, iterations=50000, initial_temp=10.0, cooling_rate=0.9995, progress_callback=None):
        self.current_solution = solution
        self.current_state = state
        self.evaluator = evaluator
        self.model_data = model_data
        self.iterations = iterations
        self.temp = initial_temp
        self.cooling_rate = cooling_rate
        self.current_cost = evaluator.calculate_total_cost(solution, state)
        self.best_solution = copy.deepcopy(solution)
        self.best_cost = self.current_cost
        self.progress_callback = progress_callback

    def optimize(self):
        print(f"Start Cost: {self.current_cost}")
        
        for i in range(self.iterations):
            self.temp *= self.cooling_rate
            
            if random.random() < 0.5:
                neighbor_solution, neighbor_state = self.generate_swap_neighbor()
            else:
                neighbor_solution, neighbor_state = self.generate_move_neighbor()

            if neighbor_solution is None:
                continue

            new_cost = self.evaluator.calculate_total_cost(neighbor_solution, neighbor_state)
            delta = new_cost - self.current_cost

            acceptance_prob = 1.0
            if delta > 0:
                acceptance_prob = math.exp(-delta / self.temp)
            
            if random.random() < acceptance_prob:
                self.current_solution = neighbor_solution
                self.current_state = neighbor_state
                self.current_cost = new_cost
                
                if new_cost < self.best_cost:
                    self.best_cost = new_cost
                    self.best_solution = copy.deepcopy(neighbor_solution)
            
            # Progress Callback
            if self.progress_callback and i % 100 == 0:
                self.progress_callback(i, self.iterations, self.best_cost)

        return self.best_solution

    def generate_swap_neighbor(self):
        if len(self.current_solution) < 2: return None, None
        a1, a2 = random.sample(self.current_solution, 2)
        if a1.session.duration_slots != a2.session.duration_slots: return None, None
            
        neighbor_state = copy.deepcopy(self.current_state)
        neighbor_solution = list(self.current_solution)
        
        neighbor_state.remove_assignment(a1)
        neighbor_state.remove_assignment(a2)
        
        new_a1 = Assignment(a1.session, a2.timeslot_sequence, a2.room, a2.instructor)
        new_a2 = Assignment(a2.session, a1.timeslot_sequence, a1.room, a1.instructor)

        if any(slot in new_a1.instructor.not_preferred_slots for slot in new_a1.timeslot_sequence): return None, None
        valid_a1 = (new_a1.instructor in a1.session.domain.instructors and
                    new_a1.room in a1.session.domain.rooms and
                    new_a1.timeslot_sequence in a1.session.domain.timeslot_sequences and
                    neighbor_state.is_consistent(new_a1.session, new_a1.timeslot_sequence, new_a1.room, new_a1.instructor))
        if not valid_a1: return None, None

        neighbor_state.add_assignment(new_a1)

        if any(slot in new_a2.instructor.not_preferred_slots for slot in new_a2.timeslot_sequence): return None, None
        valid_a2 = (new_a2.instructor in a2.session.domain.instructors and
                    new_a2.room in a2.session.domain.rooms and
                    new_a2.timeslot_sequence in a2.session.domain.timeslot_sequences and
                    neighbor_state.is_consistent(new_a2.session, new_a2.timeslot_sequence, new_a2.room, new_a2.instructor))
        if not valid_a2: return None, None

        neighbor_state.add_assignment(new_a2)
        
        neighbor_solution.remove(a1)
        neighbor_solution.remove(a2)
        neighbor_solution.append(new_a1)
        neighbor_solution.append(new_a2)
        
        return neighbor_solution, neighbor_state

    def generate_move_neighbor(self):
        if not self.current_solution: return None, None
        
        target_idx = random.randint(0, len(self.current_solution) - 1)
        target_assignment = self.current_solution[target_idx]
        var = target_assignment.session
        
        neighbor_state = copy.deepcopy(self.current_state)
        neighbor_solution = list(self.current_solution)
        neighbor_state.remove_assignment(target_assignment)
        
        candidates = []
        inst = target_assignment.instructor
        
        for t_seq in var.domain.timeslot_sequences:
            if any(slot in inst.not_preferred_slots for slot in t_seq):
                continue
            for room in var.domain.rooms:
                candidates.append((t_seq, room))
        
        random.shuffle(candidates)
        
        for (rand_time, rand_room) in candidates:
             if neighbor_state.is_consistent(var, rand_time, rand_room, inst):
                new_assignment = Assignment(var, rand_time, rand_room, inst)
                neighbor_state.add_assignment(new_assignment)
                neighbor_solution[target_idx] = new_assignment
                return neighbor_solution, neighbor_state
                
        return None, None

def run_web_solver(data_frames, weights, progress_callback=None):
    """
    Main entry point for the web app.
    """
    print("--- Starting Web Solver ---")
    
    # 1. Ingest Data
    ingestor = DataIngestor(data_frames)
    model_data = ingestor.ingest_all()
    
    if not model_data:
        raise ValueError("Failed to load data model.")

    # 2. Generate Variables
    var_generator = VariableGenerator(model_data, max_group_capacity=75)
    all_variables = var_generator.generate_all_variables()
    
    # 3. Build Domains
    domain_builder = DomainBuilder(model_data)
    domain_builder.build_all_domains(all_variables)
    
    # 4. Phase 1: Backtracking
    solver = BacktrackingSolver(all_variables, model_data)
    phase1_solution, phase1_state = solver.solve()
    
    if not phase1_solution:
        raise ValueError("Phase 1 Solver failed to find a valid initial timetable.")
        
    # 5. Phase 2: Simulated Annealing
    evaluator = CostEvaluator(model_data, weights=weights)
    optimizer = SimulatedAnnealingSolver(
        phase1_solution, 
        phase1_state, 
        evaluator, 
        model_data,
        iterations=10000, # Reduced for web responsiveness, or make configurable
        initial_temp=20.0,
        progress_callback=progress_callback
    )
    
    final_solution = optimizer.optimize()
    
    # 6. Convert to DataFrame
    output_data = []
    timeslots_map = model_data['timeslots']
    for assignment in final_solution:
        session = assignment.session
        first_slot_id = assignment.timeslot_sequence[0]
        last_slot_id = assignment.timeslot_sequence[-1]
        
        output_data.append({
            "Day": timeslots_map[first_slot_id].day,
            "StartTime": timeslots_map[first_slot_id].start_time,
            "EndTime": timeslots_map[last_slot_id].end_time,
            "CourseID": session.course.course_id,
            "CourseName": session.course.name,
            "Type": session.session_type,
            "Instructor": assignment.instructor.name,
            "Room": assignment.room.room_id,
            "Sections": ", ".join([s.section_id for s in session.sections]),
            "StudentCount": session.total_student_count
        })
        
    df = pd.DataFrame(output_data)
    df = df.sort_values(by=["Day", "StartTime"])
    return df
