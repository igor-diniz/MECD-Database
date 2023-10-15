import csv
import psycopg2
from datetime import datetime

# Database connection parameters
db_params = {
    'host': '',
    'port': '',
    'database': '',
    'user': '',
    'password': ''
}


def connect_to_database():
    """Establish a connection to the database."""
    try:
        conn = psycopg2.connect(**db_params)
        print("Connection established!\n")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def insert_student(cursor, first_name, last_name, email, date_of_birth, gpa, state_id):
    """Insert or retrieve a student record."""
    cursor.execute("SELECT student_id FROM student WHERE email = %s;", (email,))
    student_id = cursor.fetchone()

    if student_id is not None:
        return student_id[0]

    cursor.execute("""
        INSERT INTO student (first_name, last_name, email, date_of_birth, gpa, state_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING student_id;
    """, (first_name, last_name, email, date_of_birth, gpa, state_id))

    return cursor.fetchone()[0]

def insert_state(cursor, state):
    """Insert or retrieve a state record."""
    cursor.execute("SELECT state_id FROM state WHERE state_name = %s;", (state,))
    state_id = cursor.fetchone()

    if state_id is not None:
        return state_id[0]

    cursor.execute("""
        INSERT INTO state (state_name)
        VALUES (%s)
        RETURNING state_id;
    """, (state,))

    return cursor.fetchone()[0]

def insert_course(cursor, course_name):
    """Insert or retrieve a course record."""
    cursor.execute("SELECT course_id FROM course WHERE course_name = %s;", (course_name,))
    course_id = cursor.fetchone()

    if course_id is not None:
        return course_id[0]

    cursor.execute("""
        INSERT INTO course (course_name)
        VALUES (%s)
        RETURNING course_id;
    """, (course_name,))

    return cursor.fetchone()[0]

def insert_exam_type(cursor, exam_name):
    """Insert or retrieve an exam type record."""
    cursor.execute("SELECT exam_type_id FROM exam_type WHERE exam_name = %s;", (exam_name,))
    exam_type_id = cursor.fetchone()

    if exam_type_id is not None:
        return exam_type_id[0]

    cursor.execute("""
        INSERT INTO exam_type (exam_name)
        VALUES (%s)
        RETURNING exam_type_id;
    """, (exam_name,))

    return cursor.fetchone()[0]

def insert_building(cursor, building_name):
    """Insert or retrieve a building record."""
    cursor.execute("SELECT building_id FROM building WHERE building_name = %s;", (building_name,))
    building_id = cursor.fetchone()

    if building_id is not None:
        return building_id[0]

    cursor.execute("""
        INSERT INTO building (building_name)
        VALUES (%s)
        RETURNING building_id;
    """, (building_name,))

    return cursor.fetchone()[0]

def insert_room(cursor, room_name, building_id, capacity, has_projector, has_computers, is_accessible):
    """Insert or retrieve a room record."""
    cursor.execute("SELECT room_id FROM room WHERE room_name = %s;", (room_name,))
    room_id = cursor.fetchone()

    if room_id is not None:
        return room_id[0]

    cursor.execute("""
        INSERT INTO room (room_name, building_id, capacity, has_projector, has_computers, is_accessible)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING room_id;
    """, (room_name, building_id, capacity, has_projector, has_computers, is_accessible))

    return cursor.fetchone()[0]


def insert_data(cursor, exam_date, student_id, course_id, exam_type_id, room_id, grade):
    """Insert data into assessment, exam_event, and enrollment tables."""
    cursor.execute("""
        INSERT INTO exam_event (date, exam_type_id, course_id, room_id)
        VALUES (%s, %s, %s, %s)
        RETURNING exam_event_id;
    """, (exam_date, exam_type_id, course_id, room_id))

    exam_event_id = cursor.fetchone()

    if exam_event_id is not None:
        exam_event_id = exam_event_id[0]

    cursor.execute("""
        SELECT student_id, course_id FROM enrollment
            WHERE student_id = %s AND course_id = %s;
    """, (student_id, course_id))

    enrollment = cursor.fetchone()

    if enrollment is None:
        cursor.execute("""
            INSERT INTO enrollment (student_id, course_id)
            VALUES (%s, %s)
        """, (student_id, course_id))

    cursor.execute("""
        INSERT INTO assessment (student_id, exam_event_id, grade)
        VALUES (%s, %s, %s);
    """, (student_id, exam_event_id, grade))


def main():
    # Open a connection to the database
    conn = connect_to_database()
    if conn is None:
        return
    
    # Open a cursor to perform database operations
    cursor = conn.cursor()

    # Create all the tables
    cursor.execute(open("grades.sql", "r").read())

    # Read data from the CSV file
    with open('grades.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        try:
            for row in csv_reader:
                # Just to act as a log during inserting
                print(f"Inserting row:\n{row}", end="\n\n")

                # Extract data from the CSV row
                exam_date = datetime.strptime(row['exam_date'], '%Y-%m-%d')
                first_name = row['first_name']
                last_name = row['last_name']
                email = row['email']
                date_of_birth = datetime.strptime(row['date_of_birth'], '%Y-%m-%d')
                gpa = float(row['gpa'])
                course_name = row['course_name']
                exam_name = row['exam_name']
                building_name = row['building_name']
                room_name = row['room_name']
                capacity = row["capacity"]
                has_projector = row['has_projector'] == 't'
                has_computers = row['has_computers'] == 't'
                is_accessible = row['is_accessible'] == 't'
                state_name = row["state"]
                grade = row["grade"]

                # Insert or retrieve IDs for student, course, exam type, building, and room
                state_id = insert_state(cursor, state_name)
                student_id = insert_student(cursor, first_name, last_name, email, date_of_birth, gpa, state_id)
                course_id = insert_course(cursor, course_name)
                exam_type_id = insert_exam_type(cursor, exam_name)
                building_id = insert_building(cursor, building_name)
                room_id = insert_room(cursor, room_name, building_id, capacity, has_projector, has_computers, is_accessible)

                # Insert data into the database
                insert_data(cursor, exam_date, student_id, course_id, exam_type_id, room_id, grade)

            # Commit the changes and close the connection
            conn.commit()
            conn.close()

        except Exception as error:
            conn.close()
            raise error

if __name__ == "__main__":
    main()
