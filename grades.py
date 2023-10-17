import os
import psycopg2
import psycopg2.extras
from pydantic import BaseModel, validator
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

class StateModel(BaseModel):
    state_id: int
    state_name: str

class StudentModel(BaseModel):
    student_id: int
    first_name: str
    last_name: str
    email: str
    date_of_birth: date
    gpa: float
    state_id: int

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    

    def get_age(self):
        today = datetime.today()
        age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return age
    

class CourseModel(BaseModel):
    course_id: int
    course_name: str

    def __str__(self):
        return f"{self.course_name}"
   
class ExamTypeModel(BaseModel):
    exam_type_id: int
    exam_name: str

class BuildingModel(BaseModel):
    building_id: int
    building_name: str

    def __str__(self):
        return f"{self.building_name}"

class RoomModel(BaseModel):
    room_id: int
    room_name: str
    building_id: int
    capacity: int
    has_projector: bool
    has_computers: bool
    is_accessible: bool

    def __str__(self):
        return f"{self.room_name}"
    
    def print_details(self):
        print(f" - {self.room_name}:")
        print(f"   - Capacity: {self.capacity}")
        print(f"   - Has projector: {'Yes' if self.has_projector else 'No'}")
        print(f"   - Has computers: {'Yes' if self.has_computers else 'No'}")
        print(f"   - Is accessible: {'Yes' if self.is_accessible else 'No'}")

class ExamEventModel(BaseModel):
    exam_event_id: int
    date: date
    exam_type_id: int
    course_id: int
    room_id: int

    def __str__(self):
        return f"Exam Event ID: {self.exam_event_id}, Date: {self.date}"

    def print_details(self):
        print(f" - Exam Event ID: {self.exam_event_id}")
        print(f" - Date: {self.date}")
        print(f" - Exam Type ID: {self.exam_type_id}")
        print(f" - Course ID: {self.course_id}")
        print(f" - Room ID: {self.room_id}")

class EnrollmentModel(BaseModel):
    student_id: int
    course_id: int

class Assessment(BaseModel):
    student_id: int
    exam_event_id: int
    grade: float

        


class Menu:
    # Database connection parameters
    db_params = {
        'host': os.getenv("HOST"),
        'port': os.getenv("PORT"),
        'database': os.getenv("DATABASE"),
        'user': os.getenv("DB_USER"),
        'password':os.getenv("DB_PASS")
    }
    def connect_to_database(self):
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            cursor.execute("SET search_path TO grades") 
            return conn
        except psycopg2.Error as e:
            print(f"Error connecting to the Database: {e}")
            return None

    def __init__(self):
        self.connection = self.connect_to_database()
        self.cursor = self.connection.cursor()
    
    def exit(self):
        """Exit Menu"""
        return self.exit

    def print_menu(self, options):
        print("Options:")
        options['0'] = self.exit
        for key, value in options.items():
            print(f"[{key}] {value.__doc__}")
        choice = input("What's your choice? ")
        if choice not in options:
            print("Invalid choice.")
            return self.print_menu(options)
            
        return options[choice]

    def initial_menu(self):
        """Return to the main menu."""
        options = {
            '1': Student().menu,
            '2': Course().menu,
            '3': Building().menu,
            '4': Room().menu,
            '5': ExamEvent().menu,
        }
        retorno = self.print_menu(options)
        return retorno
    
    
    def run(self):
        """Run main menu."""
        func = self.initial_menu
        while True:
            last_func = func()

            if last_func.__doc__ == self.exit.__doc__:
                print("Bye!")
                break
            if last_func:
                func = last_func

            print("\n\n-----------------------\n\n")
            
        self.cursor.close()
        self.connection.close()


class Student(Menu):

    """Student menu."""
    student: StudentModel = None
    def __str__(self) -> str:
        return "Student Menu"

    def search(self):
        """Search for a student by first name or last name."""
        
        name = input("Enter the student's first or last name: ")
        self.cursor.execute("""
            SELECT student_id, first_name, last_name, email, date_of_birth, gpa, state_id
            FROM student
            WHERE first_name = %s OR last_name = %s;
        """, (name,name))
        
        student = self.cursor.fetchall()
        if student:

            if len(student) > 1:
                print("Multiple students found with the same name:")
                docents = []
                for i, s in enumerate(student, 1):
                    docent = StudentModel(
                        student_id = s[0],
                        first_name = s[1],
                        last_name = s[2],
                        email = s[3],
                        date_of_birth = s[4],
                        gpa = s[5],
                        state_id = s[6]
                    )
                    print(f"[{i}] {docent} )")
                    docents.append(docent)

                choice = int(input("Select a student by number: "))
                if 1 <= choice <= len(student):
                    student = docents[choice-1]
                else:
                    print("Invalid choice.")
                    return None
            self.student =  student
            return self.menu
        else:
            print(f"No student found with the name {name}.")
            return self.menu

    def get_age(self):
        """Get the age of the student."""
        age = self.student.get_age()
        print(f"{self.student.first_name} {self.student.last_name} is {age} years old.")
        return self.menu

    # def get_courses(self):
        
    def menu(self):
        """Student menu."""
        if self.student:
            print(f"What do you want to know about the student {self.student}?")
            options = {
                '1': self.get_age,
            }
        else:
            options = {
                '1': self.search,
            }
        options['9'] = self.initial_menu
        return self.print_menu(options)

class Course(Menu):
    """Course menu."""
    course: CourseModel = None
         
    def count_students_enrolled(self):
        """Count the number of students enrolled in the course."""
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM enrollment
            WHERE course_id = %s;
        """, (self.course.course_id,))
        response = self.cursor.fetchone()[0]
        print(f"There are {response} students enrolled in the course '{self.course.course_name}'.")
        return self.menu
    
    def calculate_average_grade_by_exam_type(self):
        """Calculate the average grade for each exam type."""
        self.cursor.execute("""
            SELECT exam_type.exam_name, AVG(grade)
            FROM assessment
            JOIN exam_event ON assessment.exam_event_id = exam_event.exam_event_id
            join exam_type on exam_event.exam_type_id = exam_type.exam_type_id
            WHERE exam_event.course_id = %s
            group by exam_type.exam_name;
        """, (self.course.course_id,))
        response = self.cursor.fetchall()
        for exam in response:
            print(f"The average grade for the exam type '{exam[0]}' is {exam[1]:.2f}.")
        return self.menu

    def find_nearest_assessment_date(self):
        """Find the nearest assessment date for the course."""
        self.cursor.execute("""
            SELECT MIN(date)
            FROM exam_event
            WHERE course_id = %s AND date >= current_date;
        """, (self.course.course_id,))
        response = self.cursor.fetchone()[0]
        print(f"The nearest assessment date for the course '{self.course.course_name}' is {response}.")
        return self.menu

    def find_building_for_course(self):
        """Find the building where the course is taught."""
        self.cursor.execute("""
            SELECT building.building_name
            FROM building
            JOIN room ON building.building_id = room.building_id
            JOIN exam_event ON room.room_id = exam_event.room_id
            WHERE exam_event.course_id = %s
            limit 1;
        """, (self.course.course_id,))
        response = self.cursor.fetchone()[0]
        print(f"The course '{self.course.course_name}' is taught in the building '{response}'.")
        return self.menu

    def search_course(self):
        """Search for a course by name."""
        course_name = input("What course do you want to search: ")

        self.cursor.execute("""
            SELECT course_id, course_name
            FROM course
            WHERE course_name = %s;
        """, (course_name,))

        course_info = self.cursor.fetchone()

        if course_info:
            self.course = CourseModel(course_id = course_info[0], course_name = course_info[1])
            return self.menu
        else:
            print(f"No course found with the name {course_name}.")

        return None
    

    def menu(self):
        """Course menu."""
        if self.course:
            print(f"What do you want to know about the course '{self.course.course_name}'?")
            options = {
                '1': self.count_students_enrolled,
                '2': self.calculate_average_grade_by_exam_type,
                '3': self.find_nearest_assessment_date,
                '4': self.find_building_for_course,
            }
        else:
            print("What do you want to do?")
            options = {
                '1': self.search_course,
            }

        options['9'] = self.initial_menu
        
        return self.print_menu(options)

class Building(Menu):
    """Building menu."""
    building: BuildingModel = None
         
    def search_building(self):
        """Search for a building by name."""
        building_name = input("What building do you want to search: ")

        self.cursor.execute("""
            SELECT building_id, building_name
            FROM building
            WHERE building_name = %s;
        """, (building_name,))

        building_info = self.cursor.fetchone()

        if building_info:
            self.building = BuildingModel(building_id=building_info[0], building_name=building_info[1])
            return self.menu
        else:
            print(f"No building found with the name {building_name}.")

        return None

    def show_all_buildings(self):
        """Show all buildings."""
        self.cursor.execute("""
            SELECT building_id, building_name
            FROM building;
        """)
        buildings = self.cursor.fetchall()

        if buildings:
            print("All buildings:")
            for building in buildings:
                print(BuildingModel(building_id=building[0], building_name=building[1]))
                print()
        else:
            print("No buildings found in the database.")

        return self.menu


    def menu(self):
        """Building menu."""
        if self.building:
            print(f"What do you want to know about the building '{self.building.building_name}'?")
            options = {
                '1': Room().show_rooms_from_building,
            }
        else:
            print("What do you want to do?")
            options = {
                '1': self.search_building,
                '2': self.show_all_buildings,
            }

        options['9'] = self.initial_menu

        return self.print_menu(options)

class Room(Menu):
    """Room menu."""
    room: RoomModel = None

    def search_room(self):
        """Search for a room by name."""
        room_name = input("What room do you want to search: ")

        self.cursor.execute("""
            SELECT room_id, room_name, building_id, capacity, has_projector, has_computers, is_accessible
            FROM room
            WHERE room_name = %s;
        """, (room_name,))

        room_info = self.cursor.fetchone()

        if room_info:
            self.room = RoomModel(
                room_id=room_info[0],
                room_name=room_info[1],
                building_id=room_info[2],
                capacity=room_info[3],
                has_projector=room_info[4],
                has_computers=room_info[5],
                is_accessible=room_info[6]
            )
            return self.menu
        else:
            print(f"No room found with the name {room_name}.")

        return None

    def show_rooms_from_building(self, building_id):
        """Show rooms from building."""

        self.cursor.execute("""
            SELECT room_id, room_name, building_id, capacity, has_projector, has_computers, is_accessible
            FROM room
            JOIN building ON room.building_id = building.building_id
            WHERE building_id = %s;
        """, (building_id,))
        rooms = self.cursor.fetchall()
        print(f"Rooms in the building '{building_id}':")
        for room in rooms:
            RoomModel(
                room_id=room[0],
                room_name=room[1],
                building_id=room[2],
                capacity=room[3],
                has_projector=room[4],
                has_computers=room[5],
                is_accessible=room[6]
            ).print_details()
        return self.menu

    def show_all_rooms(self):
        """Show all rooms."""
        self.cursor.execute("""
            SELECT room_id, room_name, building_id, capacity, has_projector, has_computers, is_accessible
            FROM room;
        """)
        rooms = self.cursor.fetchall()

        if rooms:
            print("All rooms:")
            for room in rooms:
                room_model = RoomModel(
                    room_id=room[0],
                    room_name=room[1],
                    building_id=room[2],
                    capacity=room[3],
                    has_projector=room[4],
                    has_computers=room[5],
                    is_accessible=room[6]
                )
                room_model.print_details()  # Print room details using the RoomModel
                print()  # Add an empty line for better readability
        else:
            print("No rooms found in the database.")

        return self.menu

    def menu(self):
        """Room menu."""
        if self.room:
            print(f"What do you want to know about the room '{self.room.room_name}'?")
            options = {
                '1': self.show_room_details,
            }
        else:
            print("What do you want to do?")
            options = {
                '1': self.search_room,
                '2': self.show_all_rooms,
            }

        options['9'] = self.initial_menu

        return self.print_menu(options)

class ExamEvent(Menu):
    """Exam Event menu."""
    exam_event: ExamEventModel = None

    def search_exam_event_by_id(self):
        """Search for an exam event by ID."""
        exam_event_id = input("Enter the ID of the exam event: ")

        self.cursor.execute("""
            SELECT exam_event_id, date, exam_type_id, course_id, room_id
            FROM exam_event
            WHERE exam_event_id = %s;
        """, (exam_event_id,))

        exam_event_info = self.cursor.fetchone()
        print(exam_event_info[1])
        if exam_event_info:
            self.exam_event = ExamEventModel(exam_event_id=exam_event_info[0], date=exam_event_info[1].strftime("%Y-%m-%d"), exam_type_id=exam_event_info[2], course_id=exam_event_info[3], room_id=exam_event_info[4])
            return self.menu
        else:
            print(f"No exam event found with the ID {exam_event_id}.")

        return None

    def search_exam_event_by_date(self):
        """Search for an exam event by date."""
        date = input("Enter the date of the exam event (YYYY-MM-DD): ")

        self.cursor.execute("""
            SELECT exam_event_id, date, exam_type_id, course_id, room_id
            FROM exam_event
            WHERE date = %s;
        """, (date,))

        exam_event_info = self.cursor.fetchall()

        if len(exam_event_info) > 1:
            print("Multiple exam events found with the same date:")
            for i, exam_event in enumerate(exam_event_info, 1):
                print(f"[{i}] {ExamEventModel(exam_event_id=exam_event[0], date=exam_event[1].strftime('%Y-%m-%d'), exam_type_id=exam_event[2], course_id=exam_event[3], room_id=exam_event[4])}")
            choice = int(input("Select an exam event by number: "))
            if 1 <= choice <= len(exam_event_info):
                exam_event_info = exam_event_info[choice-1]
            else:
                print("Invalid choice.")
                return None
        elif len(exam_event_info) == 1:
            exam_event_info = exam_event_info[0]

        else:
            print(f"No exam event found on {date}.")
            return None
        
        self.exam_event = ExamEventModel(exam_event_id=exam_event_info[0], date=exam_event_info[1], exam_type_id=exam_event_info[2], course_id=exam_event_info[3], room_id=exam_event_info[4])
        return self.menu

    def calculate_average_grade(self):
        """Calculate the average grade for the exam event."""

        self.cursor.execute("""
            SELECT AVG(grade)
            FROM assessment
            WHERE exam_event_id = %s;
        """, (self.exam_event.exam_event_id,))
        response = self.cursor.fetchone()[0]
        print(f"The average grade for the exam event on {self.exam_event.date} is {response:.2f}.")
        return self.menu
    
    def get_grade_distribution(self):
        """Get the grade distribution for the exam event."""
        self.cursor.execute("""
            SELECT grade, COUNT(*)
            FROM assessment
            WHERE exam_event_id = %s
            GROUP BY grade
            ORDER BY grade;
        """, (self.exam_event.exam_event_id,))
        response = self.cursor.fetchall()
        print(f"Grade distribution for the exam event on {self.exam_event.date}:")
        for grade in response:
            print(f"- {grade[0]}: {grade[1]}")
        return self.menu
    
    def get_grade_from_students(self):
        """Get the grade for each student in the exam event."""
        self.cursor.execute("""
            SELECT student.first_name, student.last_name, assessment.grade
            FROM assessment
            JOIN student ON assessment.student_id = student.student_id
            WHERE exam_event_id = %s
            ORDER BY assessment.grade DESC;
        """, (self.exam_event.exam_event_id,))
        response = self.cursor.fetchall()
        print(f"Grades for the exam event on {self.exam_event.date}:")
        for grade in response:
            print(f"- {grade[0]} {grade[1]}: {grade[2]}")
        return self.menu

    def show_exam_event_details(self):
        """Show details of the selected exam event."""
        self.exam_event.print_details()

        return self.menu


    def menu(self):
        """Exam Event menu."""
        if self.exam_event:
            print(f"What do you want to know about the exam event on {self.exam_event.exam_event_id}?")
            options = {
                '1': self.show_exam_event_details,
                '2': self.calculate_average_grade,
                '3': self.get_grade_distribution,
                '4': self.get_grade_from_students,
            }
        else:
            print("What do you want to do?")
            options = {
                '1': self.search_exam_event_by_date,
                '2': self.search_exam_event_by_id,
            }

        options['9'] = self.initial_menu

        return self.print_menu(options)


if __name__ == "__main__":
    Menu().run()
