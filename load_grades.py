import csv
import psycopg2
from datetime import datetime

# Connect to an existing database
conn = psycopg2.connect(
    host="localhost",
    database="database",
    user="pg",
    password="password")

# Open a cursor to perform database operations
cursor = conn.cursor()

# Execute a command: this creates all the tables
cursor.execute(open("grades.sql", "r").read())

# Populate the tables with data from the CSV file
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

        # Insert data into the tables
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
            # Student already exists, fetch the existing student_id
            cursor.execute("SELECT student_id FROM student WHERE email = %s;", (email,))
            student_id = cursor.fetchone()[0]

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
            # Course already exists, fetch the existing course_id
            cursor.execute("SELECT course_id FROM course WHERE course_name = %s;", (course_name,))
            course_id = cursor.fetchone()[0]

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
            # Exam type already exists, fetch the existing exam_type_id
            cursor.execute("SELECT exam_type_id FROM exam_type WHERE exam_name = %s;", (exam_name,))
            exam_type_id = cursor.fetchone()[0]

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
            # Building already exists, fetch the existing building_id
            cursor.execute("SELECT building_id FROM building WHERE building_name = %s;", (building_name,))
            building_id = cursor.fetchone()[0]

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
            # Room already exists, fetch the existing room_id
            cursor.execute("SELECT room_id FROM room WHERE room_name = %s;", (room_name,))
            room_id = cursor.fetchone()[0]

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

# Make the changes to the database persistent
conn.commit()
conn.close()
