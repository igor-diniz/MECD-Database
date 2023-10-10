import csv
import psycopg2
from datetime import datetime

# Database connection parameters
db_params = {
    'host': 'your_db_host',
    'database': 'your_db_name',
    'user': 'your_db_user',
    'password': 'your_db_password'
}


def connect_to_database():
    """Establish a connection to the database."""
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def insert_student(cursor, first_name, last_name, email, date_of_birth):
    """Insert or retrieve a student record."""
    cursor.execute("""
        INSERT INTO student (first_name, last_name, email, date_of_birth)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (email) DO NOTHING
        RETURNING student_id;
    """, (first_name, last_name, email, date_of_birth))

    student_id = cursor.fetchone()
    if student_id is not None:
        student_id = student_id[0]
    else:
        cursor.execute("SELECT student_id FROM student WHERE email = %s;", (email,))
        student_id = cursor.fetchone()[0]
    
    return student_id

def insert_course(cursor, course_name):
    """Insert or retrieve a course record."""
    cursor.execute("""
        INSERT INTO course (course_name)
        VALUES (%s)
        ON CONFLICT (course_name) DO NOTHING
        RETURNING course_id;
    """, (course_name,))

    course_id = cursor.fetchone()
    if course_id is not None:
        course_id = course_id[0]
    else:
        cursor.execute("SELECT course_id FROM course WHERE course_name = %s;", (course_name,))
        course_id = cursor.fetchone()[0]
    
    return course_id

def insert_exam_type(cursor, exam_name):
    """Insert or retrieve an exam type record."""
    cursor.execute("""
        INSERT INTO exam_type (exam_name)
        VALUES (%s)
        ON CONFLICT (exam_name) DO NOTHING
        RETURNING exam_type_id;
    """, (exam_name,))

    exam_type_id = cursor.fetchone()
    if exam_type_id is not None:
        exam_type_id = exam_type_id[0]
    else:
        cursor.execute("SELECT exam_type_id FROM exam_type WHERE exam_name = %s;", (exam_name,))
        exam_type_id = cursor.fetchone()[0]
    
    return exam_type_id

def insert_building(cursor, building_name):
    """Insert or retrieve a building record."""
    cursor.execute("""
        INSERT INTO building (building_name)
        VALUES (%s)
        ON CONFLICT (building_name) DO NOTHING
        RETURNING building_id;
    """, (building_name,))

    building_id = cursor.fetchone()
    if building_id is not None:
        building_id = building_id[0]
    else:
        cursor.execute("SELECT building_id FROM building WHERE building_name = %s;", (building_name,))
        building_id = cursor.fetchone()[0]
    
    return building_id

def insert_room(cursor, room_name, building_id, has_projector, has_computers, is_accessible):
    """Insert or retrieve a room record."""
    cursor.execute("""
        INSERT INTO room (room_name, building_id, has_projector, has_computers, is_accessible)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (room_name) DO NOTHING
        RETURNING room_id;
    """, (room_name, building_id, has_projector, has_computers, is_accessible))

    room_id = cursor.fetchone()
    if room_id is not None:
        room_id = room_id[0]
    else:
        cursor.execute("SELECT room_id FROM room WHERE room_name = %s;", (room_name,))
        room_id = cursor.fetchone()[0]
    
    return room_id


def insert_data(cursor, exam_date, student_id, course_id, exam_type_id, room_id, gpa):
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
        INSERT INTO enrollment (student_id, course_id)
        VALUES (%s, %s)
        ON CONFLICT (student_id, course_id) DO NOTHING;
    """, (student_id, course_id))

    cursor.execute("""
        INSERT INTO assessment (student_id, exam_event_id, gpa)
        VALUES (%s, %s, %s);
    """, (student_id, exam_event_id, gpa))

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

        for row in csv_reader:
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
            has_projector = row['has_projector'] == 't'
            has_computers = row['has_computers'] == 't'
            is_accessible = row['is_accessible'] == 't'

            # Insert or retrieve IDs for student, course, exam type, building, and room
            student_id = insert_student(cursor, first_name, last_name, email, date_of_birth)
            course_id = insert_course(cursor, course_name)
            exam_type_id = insert_exam_type(cursor, exam_name)
            building_id = insert_building(cursor, building_name)
            room_id = insert_room(cursor, room_name, building_id, has_projector, has_computers, is_accessible)

            # Insert data into the database
            insert_data(cursor, exam_date, student_id, course_id, exam_type_id, room_id, gpa)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
