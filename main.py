#!/usr/bin/python3
import random
import secrets

#Drop tables
print("DROP TABLE Courses")
print("DROP TABLE Students")
print("DROP TABLE Rosters")
print("DROP TABLE Course_period")
print("DROP TABLE Assignments")
print("DROP TABLE Assignment_Type")
print("DROP TABLE Teachers")
print("DROP TABLE Departments")
print("DROP TABLE Assignment_grade")
print("DROP TABLE Course_Types")

#Create tables
print("CREATE TABLE Courses (course_id integer PRIMARY KEY, course_name varchar(255), department_id integer);")
#FOREIGN KEY (department_id) REFERENCES Departments(department_id));
print("CREATE TABLE Students (student_id integer PRIMARY KEY, name varchar(255));")
print("CREATE TABLE Rosters (course_period_id integer, student_id integer);")
#FOREIGN KEY (course_period_id) REFERENCES Course_period(course_period_id), FOREIGN KEY (student_id) REFERENCES Students(student_id));")
print("CREATE TABLE Course_period (course_period_id integer PRIMARY KEY, period integer, room varchar(255), teacher_id integer, course_id integer);")
#FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id),
#FOREIGN KEY (course_id) REFERENCES Courses(course_id));")
print("CREATE TABLE Assignments (assignment_id integer PRIMARY KEY, name varchar(255), assignment_type varchar(255), course_id integer);")

#FOREIGN KEY (course_id) REFERENCES Course_period(course_period_id) course_id integer,
#FOREIGN KEY (course_id) REFERENCES Course_period(course_period_id)
#FOREIGN KEY (assignment_type) REFERENCES Assignment_Type (assignment_type_name)

print("CREATE TABLE Assignment_Type (assignment_type_name varchar(255), assignment_type_id integer PRIMARY KEY)")
print("CREATE TABLE Teachers (teacher_id integer PRIMARY KEY, name varchar(255), department_id integer);")
#FOREIGN KEY (department_id) REFERENCES Departments(department_id));")
print("CREATE TABLE Departments (department_id integer PRIMARY KEY, name varchar(255));")
print("CREATE TABLE Assignment_grade (assignment_id integer, student_id integer,grade varchar(255));")

#FOREIGN KEY (student_id) REFERENCES Students(student_id),
#FOREIGN KEY (assignment_id) REFERENCES Assignments(assignment_id)
print("CREATE TABLE Course_Types (type_id integer PRIMARY KEY, type_name varchar(255));")
#FOREIGN KEY (type_id) REFERENCES Courses(course_id));")

# Function to parse departments from file and avoid duplicates
def parse_departments_from_file(file_path):
    departments = {}
    current_department = None
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Department:"):
                current_department = line.replace("Department:", "").strip()
                departments[current_department] = []
            elif line and current_department:
                departments[current_department].append(line)
    return departments

# Parse teachers from 'teachers.txt' with numeric IDs
def parse_teachers(file_path):
    teachers = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    dept_id = parts[0].strip()  # Numeric ID (e.g., "1", "2")
                    teacher_list = [teacher.strip() for teacher in parts[1].split(',')]
                    teachers[dept_id] = teacher_list
    return teachers

# Generate all possible rooms
def generate_rooms():
    floors = ['B', '1', '2', '3', '4', '5', '6', '7', '8']
    wings = ['N', 'S', 'E', 'W']
    room_numbers = range(1, 21)
    return [f"{floor}{wing}{room_number:02}" for floor in floors for wing in wings for room_number in room_numbers]

# Main function to generate SQL inserts
def generate_sql():
    # Initialize ID counters
    course_id = 1
    teacher_id = 1
    course_period_id = 1
    assignment_id = 1

    # Constants
    STUDENTS_PER_COURSE_PERIOD = 34
    TOTAL_STUDENTS = 5000
    TOTAL_PERIODS = 10
    TOTAL_ASSIGNMENTS = TOTAL_STUDENTS * TOTAL_PERIODS
    MIN_COURSE_PERIODS = (TOTAL_ASSIGNMENTS + STUDENTS_PER_COURSE_PERIOD - 1) // STUDENTS_PER_COURSE_PERIOD

    # Data structures
    department_name_to_id = {}
    course_to_department = {}
    department_to_teachers = {}
    period_to_course_periods = {p: [] for p in range(1, TOTAL_PERIODS + 1)}
    course_period_to_students = {}
    course_to_assignments = {}  # Map course_id to its assignment_ids
    course_period_to_course = {}  # Map course_period_id to course_id

    # Insert Course_Types
    print("INSERT INTO Course_Types (type_id, type_name) VALUES (1, 'AP');")
    print("INSERT INTO Course_Types (type_id, type_name) VALUES (2, 'Regents');")
    print("INSERT INTO Course_Types (type_id, type_name) VALUES (3, 'Elective');")

    # Insert Assignment_Type
    print("INSERT INTO Assignment_Type (assignment_type_id, assignment_type_name) VALUES (1, 'Minor');")
    print("INSERT INTO Assignment_Type (assignment_type_id, assignment_type_name) VALUES (2, 'Major');")

    # Step 1: Departments and Courses
    departments_courses = parse_departments_from_file('departments.txt')
    department_id = 1
    for department, courses in departments_courses.items():
        department_name_to_id[department] = department_id
        department_to_teachers[department_id] = []
        print(f"INSERT INTO Departments (department_id, name) VALUES ({department_id}, '{department}');")
        for course in courses:
            type_id = 1 if "AP" in course else 2 if "Regents" in course else 3
            print(f"INSERT INTO Courses (course_id, department_id, course_name, type_id) VALUES ({course_id}, {department_id}, '{course}', {type_id});")
            course_to_department[course_id] = department_id
            course_to_assignments[course_id] = []  # Initialize assignment list for this course
            course_id += 1
        department_id += 1

    total_courses = course_id - 1
    print(f"Total courses generated: {total_courses}")

    # Step 2: Teachers
    teachers_dict = parse_teachers('teachers.txt')
    for dept_numeric_id, teachers in teachers_dict.items():
        try:
            dep_id = int(dept_numeric_id)
            if dep_id in department_to_teachers:
                for teacher in teachers:
                    print(f"INSERT INTO Teachers (teacher_id, name, department_id) VALUES ({teacher_id}, '{teacher}', {dep_id});")
                    department_to_teachers[dep_id].append(teacher_id)
                    teacher_id += 1
            else:
                print(f"Warning: Numeric ID '{dept_numeric_id}' from teachers.txt does not match any department ID")
        except ValueError:
            print(f"Warning: Invalid numeric ID '{dept_numeric_id}' in teachers.txt")

    # Check for departments without teachers
    for dep_id, teachers in department_to_teachers.items():
        if not teachers:
            dep_name = [name for name, id_ in department_name_to_id.items() if id_ == dep_id][0]
            print(f"Warning: No teachers assigned to department '{dep_name}' (ID: {dep_id})")

    # Step 3: Rooms
    all_rooms = generate_rooms()

    # Step 4: Course Periods
    periods_per_course = MIN_COURSE_PERIODS // total_courses + 1
    for c_id in range(1, total_courses + 1):
        department_id = course_to_department[c_id]
        if not department_to_teachers[department_id]:
            print(f"Skipping course ID {c_id} in department ID {department_id} due to no teachers")
            continue
        num_offerings = min(periods_per_course, 5)
        periods_used = set()
        for _ in range(num_offerings):
            period = random.randint(1, TOTAL_PERIODS)
            while period in periods_used:
                period = random.randint(1, TOTAL_PERIODS)
            periods_used.add(period)
            room = random.choice(all_rooms)
            teacher_id = random.choice(department_to_teachers[department_id])
            print(f"INSERT INTO Course_period (course_period_id, period, room, teacher_id, course_id) VALUES ({course_period_id}, {period}, '{room}', {teacher_id}, {c_id});")
            period_to_course_periods[period].append(course_period_id)
            course_period_to_students[course_period_id] = []
            course_period_to_course[course_period_id] = c_id  # Map period to course
            course_period_id += 1

    # Ensure minimum course periods
    while course_period_id - 1 < MIN_COURSE_PERIODS:
        c_id = random.randint(1, total_courses)
        department_id = course_to_department[c_id]
        if department_to_teachers[department_id]:
            period = random.randint(1, TOTAL_PERIODS)
            room = random.choice(all_rooms)
            teacher_id = random.choice(department_to_teachers[department_id])
            print(f"INSERT INTO Course_period (course_period_id, period, room, teacher_id, course_id) VALUES ({course_period_id}, {period}, '{room}', {teacher_id}, {c_id});")
            period_to_course_periods[period].append(course_period_id)
            course_period_to_students[course_period_id] = []
            course_period_to_course[course_period_id] = c_id
            course_period_id += 1
        else:
            print(f"Warning: Could not generate fallback course period for period {period} due to no teachers")

    print(f"Total course periods generated: {course_period_id - 1}")
    for period in range(1, TOTAL_PERIODS + 1):
        print(f"Period {period} has {len(period_to_course_periods[period])} course periods")

    # Step 5: Students
    for s_id in range(1, TOTAL_STUDENTS + 1):
        print(f"INSERT INTO Students (student_id, name) VALUES ({s_id}, 'Student{s_id}');")

    # Step 6: Rosters
    student_ids = list(range(1, TOTAL_STUDENTS + 1))
    random.shuffle(student_ids)
    for period in range(1, TOTAL_PERIODS + 1):
        available_course_periods = period_to_course_periods[period].copy()
        for student_id in student_ids:
            if not available_course_periods:
                c_id = random.randint(1, total_courses)
                department_id = course_to_department[c_id]
                if department_to_teachers[department_id]:
                    room = random.choice(all_rooms)
                    teacher_id = random.choice(department_to_teachers[department_id])
                    print(f"INSERT INTO Course_period (course_period_id, period, room, teacher_id, course_id) VALUES ({course_period_id}, {period}, '{room}', {teacher_id}, {c_id});")
                    available_course_periods.append(course_period_id)
                    course_period_to_students[course_period_id] = []
                    course_period_to_course[course_period_id] = c_id
                    course_period_id += 1
                else:
                    print(f"Error: Cannot create additional course period for period {period} due to no teachers")
                    continue

            cp_id = None
            for candidate_cp in available_course_periods:
                if len(course_period_to_students[candidate_cp]) < STUDENTS_PER_COURSE_PERIOD:
                    cp_id = candidate_cp
                    break
            if cp_id is None:
                print(f"Error: No available course period with space for period {period}")
                break

            print(f"INSERT INTO Rosters (course_period_id, student_id) VALUES ({cp_id}, {student_id});")
            course_period_to_students[cp_id].append(student_id)
            if len(course_period_to_students[cp_id]) == STUDENTS_PER_COURSE_PERIOD:
                available_course_periods.remove(cp_id)

    # Verify roster assignments
    for cp_id, students in course_period_to_students.items():
        if len(students) != STUDENTS_PER_COURSE_PERIOD:
            print(f"Warning: Course period {cp_id} has {len(students)} students instead of {STUDENTS_PER_COURSE_PERIOD}")

    # Step 7: Assignments (One set per course_id)
    for c_id in range(1, total_courses + 1):
        if c_id not in course_to_department or not department_to_teachers[course_to_department[c_id]]:
            continue  # Skip courses with no teachers
        for i in range(1, 13):  # 12 minor
            print(f"INSERT INTO Assignments (assignment_id, name, assignment_type, course_id) VALUES ({assignment_id}, 'Minor Assignment {i}', 1, {c_id});")
            course_to_assignments[c_id].append(assignment_id)
            assignment_id += 1
        for i in range(1, 4):  # 3 major
            print(f"INSERT INTO Assignments (assignment_id, name, assignment_type, course_id) VALUES ({assignment_id}, 'Major Assignment {i}', 2, {c_id});")
            course_to_assignments[c_id].append(assignment_id)
            assignment_id += 1

    # Step 8: Grades (Based on course_id via course_period_id)
    for cp_id, students in course_period_to_students.items():
        c_id = course_period_to_course[cp_id]
        for student_id in students:
            for a_id in course_to_assignments[c_id]:
                grade = random.randint(75, 100)
                print(f"INSERT INTO Assignment_grade (assignment_id, student_id, grade) VALUES ({a_id}, {student_id}, '{grade}');")

# Execute the script
if __name__ == "__main__":
    generate_sql()
