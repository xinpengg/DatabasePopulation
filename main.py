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


file_path = 'C:\\Users\\BT_4N2_02\\PycharmProjects\\pythonProject\\departments.txt'
departments = parse_departments_from_file(file_path)

department_id = 1  # Counter for department IDs
course_type_map = {"AP": 1, "Regents": 2, "Elective": 3}
type_id_counter = 4

print("INSERT INTO Course_Types (type_id, type_name) VALUES (1, 'AP');")
print("INSERT INTO Course_Types (type_id, type_name) VALUES (2, 'Regents');")
print("INSERT INTO Course_Types (type_id, type_name) VALUES (3, 'Elective');")

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
    department_id = 1  # Start department IDs from 1
    for dept_id, teachers in departments.items():
        # Insert department statement
        sql_statements.append(f"INSERT INTO Departments (department_id, name) VALUES ({department_id}, 'Department {dept_id}');")
        teacher_id = 1  # Reset teacher IDs for each department
        for teacher in teachers:
            sql_statements.append(f"INSERT INTO Teachers (teacher_id, name, department_id) VALUES ({teacher_id}, '{teacher}', {department_id});")
            teacher_id += 1
        department_id += 1
    return "\n".join(sql_statements)

# Usage example
file_path = 'teachers.txt'  # Replace with your actual file path
departments = parse_departments(file_path)
sql_output = generate_sql_insert(departments)
print(sql_output)
