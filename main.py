#!/usr/bin/python3

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


file_path = 'departments.txt'
departments = parse_departments_from_file(file_path)

department_id = 1  # Counter for department IDs
course_type_map = {"AP": 1, "Regents": 2, "Elective": 3}
type_id_counter = 4

print("INSERT INTO Course_Types (type_id, type_name) VALUES (1, 'AP');")
print("INSERT INTO Course_Types (type_id, type_name) VALUES (2, 'Regents');")
print("INSERT INTO Course_Types (type_id, type_name) VALUES (3, 'Elective');")
num_courses=0
for department, courses in departments.items():
    print(f"INSERT INTO Departments (department_id, name) VALUES ({department_id}, '{department}');")
    for course in courses:
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
        num_courses+=1
    department_id += 1

def parse_departments(file_path):
    departments = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:  # Ignore empty lines
                # Split department ID and teachers
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
        sql_statements.append(f"INSERT INTO Departments (department_id, name) VALUES ({department_id}, 'Department {dept_id}');")
        teacher_id = 1  # Reset teacher IDs for each department
        for teacher in teachers:
            sql_statements.append(f"INSERT INTO Teachers (teacher_id, name, department_id) VALUES ({teacher_id}, '{teacher}', {department_id});")
            teacher_list.append(teacher)  # Append the teacher's name to the list
            teacher_id += 1
        department_id += 1
    return "\n".join(sql_statements), teacher_list  # Return both the SQL statements and the teacher list

file_path = 'teachers.txt'
departments = parse_departments(file_path)
sql_output, teacher_list = generate_sql_insert(departments)

print(sql_output)

print("\nList of Teachers:")
print(teacher_list)


for i in range(1, 5001):
    print(f"INSERT INTO Students (student_id, name) VALUES ({i}, 'Student{i}');")
import random

floors = ['B', 1, 2, 3, 4, 5, 6, 7, 8]
wings = ['N', 'S', 'E', 'W']
room_numbers = range(1, 21)  # Room numbers from 1 to 20

all_rooms = [f"{floor}{wing}{room_number:02}" for floor in floors for wing in wings for room_number in room_numbers]

course_period_id = 1

room_index = 0

for course_id in range(1, num_courses + 1):
    num_offerings = random.randint(1, 5)  # Randomly generate 1–5 offerings per course
    offerings_count = 0  # Track the number of offerings per course

    while offerings_count < num_offerings and room_index < len(all_rooms):
        room = all_rooms[room_index]  # Get the next unique room
        teacher_id = random.choice(teacher_list)  # Randomly assign a teacher
        period = random.randint(1, 10)  # Randomly assign a period

        print(f"INSERT INTO Course_period (course_period_id, period, room, teacher_id, course_id) "
              f"VALUES ({course_period_id}, {period}, '{room}', '{teacher_id}', {course_id});")

        course_period_id += 1
        offerings_count += 1  # Increment the count of offerings for this course
        room_index += 1  # Move to the next room in the list
