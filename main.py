#!/usr/bin/python3
import random
import secrets

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
def parse_departments(file_path):
    departments = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:  # Ignore empty lines
                parts = line.split(':', 1)
                if len(parts) == 2:
                    department_id = parts[0].strip()
                    teachers = [teacher.strip() for teacher in parts[1].split(',')]
                    departments[department_id] = teachers
    return departments

def generate_sql_insert(departments):
    sql_statements = []
    teacher_list = []  # Initialize an empty list to store teacher names
    department_id = 1  # Start department IDs from 1
    for dept_id, teachers in departments.items():
        # Insert department statement
        teacher_id = 1  # Reset teacher IDs for each department
        for teacher in teachers:
            sql_statements.append(f"INSERT INTO Teachers (teacher_id, name, department_id) VALUES ({teacher_id}, '{teacher}', {department_id});")
            teacher_list.append(teacher)  # Append the teacher's name to the list
            teacher_id += 1
        department_id += 1
    return "\n".join(sql_statements), teacher_list

def generate_course_periods(num_courses, all_rooms, teachersize):
    course_to_course_periods = {}
    course_period_id = 1
    room_index = 0

    for course_id in range(1, num_courses + 1):
        num_offerings = random.randint(1, 5)  # Randomly generate 1–5 offerings per course
        offerings_count = 0  # Track the number of offerings per course

        # Create an entry in the dictionary for this course_id if it doesn't exist
        if course_id not in course_to_course_periods:
            course_to_course_periods[course_id] = []

        while offerings_count < num_offerings and room_index < len(all_rooms):
            room = all_rooms[room_index]  # Get the next unique room
            teacher_index = random.randint(0, teachersize - 1)  # Generate a random index
            period = random.randint(1, 10)  # Randomly assign a period

            # Print SQL statement
            print(f"INSERT INTO Course_period (course_period_id, period, room, teacher_id, course_id) "
                  f"VALUES ({course_period_id}, {period}, '{room}', {teacher_index}, {course_id});")

            # Append the course_period_id to the list for this course_id
            course_to_course_periods[course_id].append(course_period_id)

            course_period_id += 1
            offerings_count += 1  # Increment the count of offerings for this course
            room_index += 1

    return course_to_course_periods


file_path = 'departments.txt'
departments = parse_departments_from_file(file_path)

department_id = 1  # Counter for department IDs
course_type_map = {"AP": 1, "Regents": 2, "Elective": 3}
type_id_counter = 4

print("INSERT INTO Course_Types (type_id, type_name) VALUES (1, 'AP');")
print("INSERT INTO Course_Types (type_id, type_name) VALUES (2, 'Regents');")
print("INSERT INTO Course_Types (type_id, type_name) VALUES (3, 'Elective');")
num_courses = 0

inserted_departments = set()
print(f"INSERT INTO Assignment_Type (assignment_type_name) VALUES ('Minor');")
print(f"INSERT INTO Assignment_Type (assignment_type_name) VALUES ('Major');")
assignment_id = 1
course_assignments = {}
for department, courses in departments.items():
    if department not in inserted_departments:
        print(f"INSERT INTO Departments (department_id, name) VALUES ({department_id}, '{department}');")
        inserted_departments.add(department)
        for course in courses:
            # Determine the course type
            if "AP" in course:
                type_id = course_type_map["AP"]
            elif "Regents" in course:
                type_id = course_type_map["Regents"]
            else:
                if "Elective" not in course_type_map:
                    course_type_map["Elective"] = type_id_counter
                    print(f"INSERT INTO Course_Types (type_id, type_name) VALUES ({type_id_counter}, 'Elective');")
                    type_id_counter += 1
                type_id = course_type_map["Elective"]

            print(f"INSERT INTO Courses (department_id, course_name, type_id) "
                  f"VALUES ({department_id}, '{course}', {type_id});")
            course_id = num_courses
            num_minor_assignments = 12
            num_major_assignments = 3
            if course_id not in course_assignments:
                course_assignments[course_id] = []
            for i in range(1, num_minor_assignments + 1):
                print(f"INSERT INTO Assignments (assignment_id, name, assignment_type, course_id) "
                      f"VALUES ({assignment_id}, 'Minor Assignment {assignment_id}', 0, {num_courses});")
                course_assignments[course_id].append(assignment_id)
                assignment_id += 1
            for i in range(1, num_major_assignments + 1):
                print(f"INSERT INTO Assignments (assignment_id, name, assignment_type, course_id) "
                      f"VALUES ({assignment_id}, 'Major Assignment {assignment_id - num_minor_assignments}', 1, {num_courses});")
                course_assignments[course_id].append(assignment_id)
                assignment_id += 1  # Increment assignment_id

            num_courses += 1
        department_id += 1



file_path = 'teachers.txt'
departments = parse_departments(file_path)
sql_output, teacher_list = generate_sql_insert(departments)
teachersize = len(teacher_list)
student_courses_periods = {}
num_courses = 314

for i in range(1, 5001):
    print(f"INSERT INTO Students (student_id, name) VALUES ({i}, 'Student{i}');")
    listOfRandCoursePeriod = []
    enrolled_courses = set()  # To keep track of unique courses

    for j in range(1, 11):  # Each student gets enrolled in up to 10 unique courses
        randCoursePeriod = random.randint(1, num_courses)  # Random course_period_id

        # Ensure course_period_id maps to a unique course for the student
        while randCoursePeriod in listOfRandCoursePeriod or randCoursePeriod % num_courses in enrolled_courses:
            randCoursePeriod = random.randint(1, num_courses)

        listOfRandCoursePeriod.append(randCoursePeriod)
        enrolled_courses.add(randCoursePeriod % num_courses)  # Track the base course ID

        print(f"INSERT INTO Roster (course_period_id, student_id) VALUES ({randCoursePeriod}, {i});")

    student_courses_periods[i] = listOfRandCoursePeriod

for i in range(1, 5001):
    print(f"INSERT INTO Students (student_id, name) VALUES ({i}, 'Student{i}');")
    listOfRandCoursePeriod = []

    for j in range(1, 11):
        randCoursePeriod = random.randint(1, 314)
        while randCoursePeriod in listOfRandCoursePeriod:
            randCoursePeriod = random.randint(1, 314)

        listOfRandCoursePeriod.append(randCoursePeriod)
        print(f"INSERT INTO Roster (course_period_id, student_id) VALUES ({randCoursePeriod}, {i});")
    student_courses_periods[i] = listOfRandCoursePeriod

# Map students to courses
students_to_courses = {}
floors = ['B', 1, 2, 3, 4, 5, 6, 7, 8]
wings = ['N', 'S', 'E', 'W']
room_numbers = range(1, 21)  # Room numbers from 1 to 20

all_rooms = [f"{floor}{wing}{room_number:02}" for floor in floors for wing in wings for room_number in room_numbers]

# Generate course periods using the method
teachersize = 50  # Example number of teachers
course_to_course_periods = generate_course_periods(num_courses, all_rooms, teachersize)

# Generate students and their course periods
student_courses_periods = {}

for i in range(1, 5001):
    print(f"INSERT INTO Students (student_id, name) VALUES ({i}, 'Student{i}');")
    listOfRandCoursePeriod = []

    for j in range(1, 11):
        randCoursePeriod = random.randint(1, 314)
        while randCoursePeriod in listOfRandCoursePeriod:
            randCoursePeriod = random.randint(1, 314)

        listOfRandCoursePeriod.append(randCoursePeriod)
        print(f"INSERT INTO Roster (course_period_id, student_id) VALUES ({randCoursePeriod}, {i});")
    student_courses_periods[i] = listOfRandCoursePeriod

# Map students to courses
students_to_courses = {}

for student_id, course_period_list in student_courses_periods.items():
    students_to_courses[student_id] = []

    for course_id, course_period_ids in course_to_course_periods.items():
        if any(course_period_id in course_period_list for course_period_id in course_period_ids):
            students_to_courses[student_id].append(course_id)
print(course_assignments)
students_to_assignments = {}

# Map each student to their assignments
for student_id, course_ids in students_to_courses.items():
    students_to_assignments[student_id] = []  # Create an empty list for assignments
    for course_id in course_ids:
        if course_id in course_assignments:  # Check if the course has assignments
            students_to_assignments[student_id].extend(course_assignments[course_id])

# Print the assignments for each student
for student_id, assignments in students_to_assignments.items():
    print(f"Student ID: {student_id}, Assignments: {assignments}")

for student_id, courses in students_to_courses.items():
    if ((len(set(courses))) == 7):
        print(str(student_id) + " " + str(courses))



for i in range(1, 5001):

    random_number = secrets.randbelow(26) + 75

