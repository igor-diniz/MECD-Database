# Importe os módulos necessários
import psycopg2
from datetime import datetime

# Parâmetros de conexão com o banco de dados
db_params = {
    'host': 'dbm.fe.up.pt',
    'port': '5433',
    'database': 'fced_ingrid_diniz',
    'user': 'fced_ingrid_diniz',
    'password': 'fced_ingrid_diniz'
}

# Função para conectar ao banco de dados
def connect_to_database():
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute("SET search_path TO grades")  # Adicionando a linha aqui
        print("Conexão estabelecida!\n")
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


# Função para criar o menu
def menu():
    print("Menu:")
    print("[1] Search Student")
    print("[2] Search Course")
    print("[3] Search Room")
    print("[4] Search Assessment")
    print("[0] Exit")
    choice = input("What's your choice? ")
    return choice

def calculate_age(date_of_birth):
    today = datetime.today()
    birthdate = datetime.strptime(date_of_birth, '%Y-%m-%d')
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def search_student(cursor):
    print("---")
    first_name = input("What student do you want to search: ")

    cursor.execute("""
        SELECT *
        FROM student
        WHERE first_name = %s;
    """, (first_name,))
    
    students = cursor.fetchall()

    if students:
        if len(students) > 1:
            print("Multiple students found with the same first name:")
            for i, student in enumerate(students, 1):
                print(f"[{i}] {student[1]} {student[2]} ({student[3]})")
            
            choice = int(input("Select a student by number: "))
            if 1 <= choice <= len(students):
                student = students[choice-1]
            else:
                print("Invalid choice.")
                return
        else:
            student = students[0]

        print(f"What do you want to know about the student '{student[1]} {student[2]}'?")
        print("[1] Personal Information")
        print("[2] Course")
        print("[3] GPA")
        choice = input("Enter your choice: ")

        if choice == '1':
            age = calculate_age(student[4].strftime('%Y-%m-%d'))
            print(f"Name: {student[1]} {student[2]}")
            print(f"Email: {student[3]}")
            print(f"Age: {age}")
        elif choice == '2':
            cursor.execute("""
                SELECT course.course_name
                FROM course
                JOIN enrollment ON course.course_id = enrollment.course_id
                WHERE enrollment.student_id = %s;
            """, (student[0],))
            courses = cursor.fetchall()
            print(f"The student '{student[1]} {student[2]}' is enrolled in the following courses:")
            for course in courses:
                print(f"- {course[0]}")
        elif choice == '3':
            cursor.execute("""
                SELECT AVG(gpa)
                FROM assessment
                WHERE student_id = %s;
            """, (student[0],))
            avg_gpa = cursor.fetchone()[0]
            print(f"The average GPA of the student '{student[1]} {student[2]}' is {avg_gpa:.2f}.")
        else:
            print("Invalid choice.")
    else:
        print(f"No students found with the name {first_name}.")

    print("[0] Back")



def search_course(cursor):
    print("---")
    course_name = input("What course do you want to search: ")

    cursor.execute("""
        SELECT course_id, course_name
        FROM course
        WHERE course_name = %s;
    """, (course_name,))
    
    course_info = cursor.fetchone()

    if course_info:
        course_id, course_name = course_info

        print(f"What do you want to know about the course '{course_name}'?")
        print("[1] How many students are enrolled?")
        print("[2] Average of the students?")
        print("[3] Date of the nearest assessment?")
        print("[4] In which building is the course taught?")
        choice = input("Enter your choice: ")

        if choice == '1':
            cursor.execute("""
                SELECT COUNT(*)
                FROM enrollment
                WHERE course_id = %s;
            """, (course_id,))
            num_students = cursor.fetchone()[0]
            print(f"There are {num_students} students enrolled in the course '{course_name}'.")
        elif choice == '2':
            cursor.execute("""
                SELECT AVG(gpa)
                FROM assessment
                JOIN exam_event ON assessment.exam_event_id = exam_event.exam_event_id
                WHERE exam_event.course_id = %s;
            """, (course_id,))
            avg_gpa = cursor.fetchone()[0]
            print(f"The average GPA of the students in the course '{course_name}' is {avg_gpa:.2f}.")
        elif choice == '3':
            cursor.execute("""
                SELECT MIN(date)
                FROM exam_event
                WHERE course_id = %s AND date >= current_date;
            """, (course_id,))
            nearest_exam_date = cursor.fetchone()[0]
            print(f"The date of the nearest assessment in the course '{course_name}' is {nearest_exam_date}.")
        elif choice == '4':
            cursor.execute("""
                SELECT building.building_name
                FROM building
                JOIN room ON building.building_id = room.building_id
                JOIN exam_event ON room.room_id = exam_event.room_id
                WHERE exam_event.course_id = %s
                LIMIT 1;
            """, (course_id,))
            building_name = cursor.fetchone()[0]
            print(f"The course '{course_name}' is taught in the building '{building_name}'.")
        else:
            print("Invalid choice.")
    else:
        print(f"No course found with the name {course_name}.")

    print("[0] Back")

def search_room(cursor):
    print("---")
    room_name = input("What room do you want to search: ")

    cursor.execute("""
        SELECT room_id, room_name, building_id, has_projector, has_computers, is_accessible
        FROM room
        WHERE room_name = %s;
    """, (room_name,))
    
    room_info = cursor.fetchone()

    if room_info:
        room_id, room_name, building_id, has_projector, has_computers, is_accessible = room_info

        print(f"What do you want to know about the room '{room_name}'?")
        print("[1] Capacity")
        print("[2] Equipment (projector, computers)")
        print("[3] Is accessible?")
        print("[4] Availability Date (first)")
        choice = input("Enter your choice: ")

        if choice == '1':
            cursor.execute("""
                SELECT capacity
                FROM room
                WHERE room_id = %s;
            """, (room_id,))
            capacity = cursor.fetchone()[0]
            print(f"The capacity of the room '{room_name}' is {capacity}.")
        elif choice == '2':
            equipment = []
            if has_projector:
                equipment.append('projector')
            if has_computers:
                equipment.append('computers')
            if equipment:
                print(f"The room '{room_name}' is equipped with: {', '.join(equipment)}.")
            else:
                print(f"The room '{room_name}' has no special equipment.")
        elif choice == '3':
            print(f"The room '{room_name}' is {'accessible' if is_accessible else 'not accessible'}.")
        elif choice == '4':
            # Adicione a lógica para obter a data de disponibilidade (primeira)
            pass
        else:
            print("Invalid choice.")
    else:
        print(f"No room found with the name {room_name}.")

    print("[0] Back")

def search_assessment(cursor):
    print("---")
    assessment_id = input("What assessment do you want to search (ID): ")

    cursor.execute("""
        SELECT assessment.assessment_id, exam_name, course_name, date
        FROM assessment
        JOIN exam_event ON assessment.exam_event_id = exam_event.exam_event_id
        JOIN exam_type ON exam_event.exam_type_id = exam_type.exam_type_id
        JOIN course ON exam_event.course_id = course.course_id
        WHERE assessment.assessment_id = %s;
    """, (assessment_id,))
    
    assessment_info = cursor.fetchone()

    if assessment_info:
        assessment_id, exam_name, course_name, date = assessment_info

        print(f"What do you want to know about the assessment '{exam_name}'?")
        print("[1] Information (assessment name, course name, date)")
        print("[2] Room")
        print("[3] Minimum and Maximum Grade")
        choice = input("Enter your choice: ")

        if choice == '1':
            print(f"Assessment Name: {exam_name}")
            print(f"Course Name: {course_name}")
            print(f"Date: {date}")
        elif choice == '2':
            # Adicione a lógica para obter informações sobre a sala
            pass
        elif choice == '3':
            cursor.execute("""
                SELECT MIN(gpa), MAX(gpa)
                FROM assessment
                WHERE assessment_id = %s;
            """, (assessment_id,))
            min_grade, max_grade = cursor.fetchone()
            print(f"Minimum Grade: {min_grade}")
            print(f"Maximum Grade: {max_grade}")
        else:
            print("Invalid choice.")
    else:
        print(f"No assessment found with the ID {assessment_id}.")

    print("[0] Back")


# Função para executar a opção escolhida
def execute_option(choice, cursor):
    if choice == '1':
        search_student(cursor)
    elif choice == '2':
        search_course(cursor)
    elif choice == '3':
        search_room(cursor)
    elif choice == '4':
        search_assessment(cursor)
    elif choice == '0':
        exit()
    else:
        print("Opção inválida.")


def main():
    conn = connect_to_database()

    if conn is None:
        return

    cursor = conn.cursor()

    while True:
        choice = menu()
        execute_option(choice, cursor)

if __name__ == "__main__":
    main()

