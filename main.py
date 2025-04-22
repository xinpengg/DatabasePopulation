#!/usr/bin/env python3
import random
import secrets
import sys
with open("insert.sql", "w") as f:
        pass

# Function to parse departments from file and avoid duplicates\
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
    # Drop tables
    print("DROP TABLE IF EXISTS Courses;")
    print("DROP TABLE IF EXISTS Students;")
    print("DROP TABLE IF EXISTS Rosters;")
    print("DROP TABLE IF EXISTS Course_period;")
    print("DROP TABLE IF EXISTS Assignments;")
    print("DROP TABLE IF EXISTS Assignment_Type;")
    print("DROP TABLE IF EXISTS Teachers;")
    print("DROP TABLE IF EXISTS Departments;")
    print("DROP TABLE IF EXISTS Assignment_grade;")
    print("DROP TABLE IF EXISTS Course_Types;")

    # Create tables
    print("""
    CREATE TABLE Course_Types (
        type_id INT PRIMARY KEY,
        type_name VARCHAR(50) NOT NULL
    );
    """)
    print("""
    CREATE TABLE Assignment_Type (
        assignment_type_id INT PRIMARY KEY,
        assignment_type_name VARCHAR(50) NOT NULL
    );
    """)
    print("""
    CREATE TABLE Departments (
        department_id INT PRIMARY KEY,
        name VARCHAR(100) NOT NULL
    );
    """)
    print("""
    CREATE TABLE Courses (
        course_id INT PRIMARY KEY,
        department_id INT NOT NULL,
        course_name VARCHAR(255) NOT NULL,
        type_id INT NOT NULL,
        FOREIGN KEY (department_id) REFERENCES Departments(department_id),
        FOREIGN KEY (type_id) REFERENCES Course_Types(type_id)
    );
    """)
    print("""
    CREATE TABLE Teachers (
        teacher_id INT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        department_id INT NOT NULL,
        FOREIGN KEY (department_id) REFERENCES Departments(department_id)
    );
    """)
    print("""
    CREATE TABLE Course_period (
        course_period_id INT PRIMARY KEY,
        period INT NOT NULL,
        room VARCHAR(10) NOT NULL,
        teacher_id INT NOT NULL,
        course_id INT NOT NULL,
        FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id),
        FOREIGN KEY (course_id) REFERENCES Courses(course_id)
    );
    """)
    print("""
    CREATE TABLE Students (
        student_id INT PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );
    """)
    print


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
    print()

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
                print()
        except ValueError:
            print()

    # Check for departments without teachers
    for dep_id, teachers in department_to_teachers.items():
        if not teachers:
            dep_name = [name for name, id_ in department_name_to_id.items() if id_ == dep_id][0]
            print()

    # Step 3: Rooms
    all_rooms = generate_rooms()

    # Step 4: Course Periods
    periods_per_course = MIN_COURSE_PERIODS // total_courses + 1
    for c_id in range(1, total_courses + 1):
        department_id = course_to_department[c_id]
        if not department_to_teachers[department_id]:
            print()
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
            print()

    print(f"Total course periods generated: {course_period_id - 1}")
    for period in range(1, TOTAL_PERIODS + 1):
        print()

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
                    print()
                    continue

            cp_id = None
            for candidate_cp in available_course_periods:
                if len(course_period_to_students[candidate_cp]) < STUDENTS_PER_COURSE_PERIOD:
                    cp_id = candidate_cp
                    break
            if cp_id is None:
                print()
                break

            print(f"INSERT INTO Rosters (course_period_id, student_id) VALUES ({cp_id}, {student_id});")
            course_period_to_students[cp_id].append(student_id)
            if len(course_period_to_students[cp_id]) == STUDENTS_PER_COURSE_PERIOD:
                available_course_periods.remove(cp_id)

    # Verify roster assignments
    for cp_id, students in course_period_to_students.items():
        if len(students) != STUDENTS_PER_COURSE_PERIOD:
            print()

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
sys.stdout = open("insert.sql", "w")
# Execute the script
if __name__ == "__main__":
    generate_sql()
