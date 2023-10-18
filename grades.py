import os
import psycopg2
import psycopg2.extras
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from functools import wraps

load_dotenv()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
        print(bcolors.OKGREEN + f" - {self.room_name}:" + bcolors.ENDC)
        print(bcolors.OKGREEN + f"   - Capacity: {self.capacity}" + bcolors.ENDC)
        print(bcolors.OKGREEN + f"   - Has projector: {'Yes' if self.has_projector else 'No'}" + bcolors.ENDC)
        print(bcolors.OKGREEN + f"   - Has computers: {'Yes' if self.has_computers else 'No'}" + bcolors.ENDC)
        print(bcolors.OKGREEN + f"   - Is accessible: {'Yes' if self.is_accessible else 'No'}" + bcolors.ENDC)

class ExamEventModel(BaseModel):
    exam_event_id: int
    date: date
    exam_type_id: int
    course_id: int
    room_id: int
    course_name: Optional[str] = None
    exam_name: Optional[str] = None
    def __str__(self):
        return f"Exam Event ID: {self.exam_event_id}, Exam Name: {self.exam_name}, Date: {self.date}, Course Name: {self.course_name}, Room ID: {self.room_id}"

    def print_details(self):
        print(self.course_name)
        print(self.exam_name)
        print(bcolors.OKGREEN + f" - Exam Event ID: {self.exam_event_id}" + bcolors.ENDC)
        print(bcolors.OKGREEN + f" - Date: {self.date}" + bcolors.ENDC)
        if self.exam_name:
            print(bcolors.OKGREEN + f" - Exam Type Name: {self.exam_name}" + bcolors.ENDC)
        else:
            print(bcolors.OKGREEN + f" - Exam Type ID: {self.exam_type_id}" + bcolors.ENDC)
        
        if self.course_name:
            print(bcolors.OKGREEN + f" - Course Name: {self.course_name}" + bcolors.ENDC)
        else:
            print(bcolors.OKGREEN + f" - Course ID: {self.course_id}" + bcolors.ENDC)
        print(bcolors.OKGREEN + f" - Room ID: {self.room_id}" + bcolors.ENDC)

class EnrollmentModel(BaseModel):
    student_id: int
    course_id: int

class Assessment(BaseModel):
    student_id: int
    exam_event_id: int
    grade: float

        

def enter_to_continue(func):
    """Decorator to add extra input in order to continue."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        input("Press enter to continue...")
        return result

    return wrapper


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
            self.print(f"Error connecting to the Database: {e}", bcolors.FAIL)
            return None

    def __init__(self):
        self.connection = self.connect_to_database()
        self.cursor = self.connection.cursor()
    

    def print(self, text="", color=bcolors.OKGREEN):
        if isinstance(text, BaseModel):
            text = text.__str__()
        print(color + text + bcolors.ENDC)


    def exit(self):
        """Exit Menu"""
        return self.exit

    def print_menu(self, options):
        self.print("Options:", bcolors.HEADER)
        options['0'] = self.exit
        for key, value in options.items():
            color = bcolors.OKBLUE
            if key == '0':
                color = bcolors.WARNING
            if key == '9':
                color = bcolors.WARNING
            self.print(f"[{key}] {value.__doc__}", color)

        choice = input("What's your choice? ")
        if choice not in options:
            self.print("Invalid choice.", bcolors.FAIL)
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
                self.print("Bye!", bcolors.OKGREEN)
                break
            if last_func:
                func = last_func
            self.print("-"*50, bcolors.OKCYAN)

            
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
                self.print("Multiple students found with the same name:", bcolors.WARNING)
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
                    self.print(f"[{i}] {docent} )")
                    docents.append(docent)

                choice = int(input("Select a student by number: "))
                if 1 <= choice <= len(student):
                    student = docents[choice-1]
                else:
                    self.print("Invalid choice.", bcolors.FAIL)
                    return None
            else:
                student = StudentModel(
                    student_id = student[0][0],
                    first_name = student[0][1],
                    last_name = student[0][2],
                    email = student[0][3],
                    date_of_birth = student[0][4],
                    gpa = student[0][5],
                    state_id = student[0][6]
                )
            self.student = student
            return self.menu
        else:
            self.print(f"No student found with the name {name}.", bcolors.FAIL)
            return self.menu

    @enter_to_continue
    def get_age(self):
        """Get the age of the student."""
        age = self.student.get_age()
        self.print(f"{self.student.first_name} {self.student.last_name} is {age} years old.")
        return self.menu
    
    @enter_to_continue
    def get_courses(self):
        """Show the courses the student is enrolled in."""
        self.cursor.execute("""
            SELECT course.course_name
            FROM course
            JOIN enrollment ON course.course_id = enrollment.course_id
            WHERE student_id = %s;
        """, (self.student.student_id,))
        courses = self.cursor.fetchall()
        self.print(f"{self.student.first_name} {self.student.last_name} is enrolled in the following courses:")
        for course in courses:
            self.print(f"- {course[0]}")
        return self.menu
    
    @enter_to_continue
    def get_gpa(self):
        """Get the GPA of the student."""
        self.print(f"{self.student.first_name} {self.student.last_name}'s GPA is {self.student.gpa:.2f}.")
        return self.menu
    
    @enter_to_continue
    def get_grade_for_all_courses(self):
        """Get the grade for each course the student is enrolled in."""
        self.cursor.execute("""
            SELECT course.course_name, assessment.grade
            FROM assessment
            JOIN exam_event ON assessment.exam_event_id = exam_event.exam_event_id
            JOIN course ON exam_event.course_id = course.course_id
            WHERE student_id = %s
            ORDER BY assesment.grade DESC;
        """, (self.student.student_id,))
        grades = self.cursor.fetchall()
        self.print(f"Grades for {self.student.first_name} {self.student.last_name}:")
        for grade in grades:
            self.print(f"- {grade[0]}: {grade[1]}")
        return self.menu
    
    @enter_to_continue
    def show_all_students(self):
        """Show all students."""
        self.cursor.execute("""
            SELECT student_id, first_name, last_name, email, date_of_birth, gpa, state_id
            FROM student;
        """)
        students = self.cursor.fetchall()

        if students:
            self.print("All students:")
            for student in students:
                self.print(StudentModel(
                    student_id = student[0],
                    first_name = student[1],
                    last_name = student[2],
                    email = student[3],
                    date_of_birth = student[4],
                    gpa = student[5],
                    state_id = student[6]
                ))
                self.print()
        else:
            self.print("No students found in the database.", bcolors.FAIL)

        return self.menu
    
    def histogram_of_gpa(self):
        """Show a histogram of the GPA of all students."""
        self.cursor.execute("""
            SELECT gpa
            FROM student;
        """)
        gpas = [row[0] for row in self.cursor.fetchall()]

        if not gpas:
            self.print("No GPAs recorded for the students.", bcolors.FAIL)
            return None, self.menu

        plt.hist(gpas, bins=20, alpha=0.7, color='b', edgecolor='k')
        plt.xlabel('GPAs')
        plt.ylabel('Frequency')
        plt.title('GPA Distribution')
        plt.grid(True)

        plt.show()
        return self.menu

    def gpa_vs_grade(self):
        """Show a scatter plot of the GPA vs. the grade for all students."""
        self.cursor.execute("""
            SELECT gpa, AVG(grade)
            FROM student
            JOIN assessment ON student.student_id = assessment.student_id
            GROUP BY student.student_id;
        """)
        gpas, grades = zip(*self.cursor.fetchall())

        if not gpas or not grades:
            self.print("No GPAs or grades recorded for the students.", bcolors.FAIL)
            return None, self.menu

        plt.scatter(gpas, grades, alpha=0.7, color='b')
        plt.xlabel('GPAs')
        plt.ylabel('Grades (average)')
        plt.title('GPAs vs. Grades (average)')
        plt.grid(True)

        plt.show()
        return self.menu
    
    def grades_by_course(self):
        """Show a bar plot of the average grade for each course."""
        self.cursor.execute("""
            SELECT course.course_name, AVG(grade)
            FROM assessment
            JOIN exam_event ON assessment.exam_event_id = exam_event.exam_event_id
            JOIN course ON exam_event.course_id = course.course_id
            GROUP BY course.course_name
            ORDER BY AVG(grade) DESC;
        """)
        courses, grades = zip(*self.cursor.fetchall())

        if not courses or not grades:
            self.print("No courses or grades recorded for the students.", bcolors.FAIL)
            return None, self.menu

        plt.bar(courses, grades, alpha=0.7, color='b')
        plt.xlabel('Courses')
        plt.ylabel('Grades (average)')
        plt.title('Average Grades by Course')
        plt.grid(True)
        plt.xticks(rotation=90)
        plt.show()
        return self.menu

    @enter_to_continue
    def average_grade_for_each_students(self):
        """Get the average grade for each student."""
        self.cursor.execute("""
            SELECT student.first_name, student.last_name, AVG(grade)
            FROM assessment
            JOIN student ON assessment.student_id = student.student_id
            GROUP BY student.student_id
            ORDER BY AVG(grade) DESC;
        """)
        response = self.cursor.fetchall()
        self.print(f"Average grades for each student:")
        for student in response:
            self.print(f"{student[0]} {student[1]}: {student[2]:.2f}")
        return self.menu

    def grades_over_time(self):
        """Plot one line of the average grade of a student for each course over time."""
        self.cursor.execute("""
            SELECT course.course_name, assessment.grade, exam_event.date
            FROM assessment
            JOIN exam_event ON assessment.exam_event_id = exam_event.exam_event_id
            JOIN course ON exam_event.course_id = course.course_id
            WHERE student_id = %s
            ORDER BY exam_event.date;
        """, (self.student.student_id,))
        grades = self.cursor.fetchall()

        if not grades:
            self.print("No grades recorded for the student.", bcolors.FAIL)
            return None, self.menu


        courses = {}
        for grade in grades:
            if grade[0] not in courses:
                courses[grade[0]] = [[grade[2], grade[1]]]
            else:
                courses[grade[0]].append([grade[2], grade[1]])

        for course, grades in courses.items():
            dates, grades = zip(*grades)
            plt.plot(dates, grades, label=course)

        plt.xlabel('Date')
        plt.ylabel('Grades')
        plt.title('Grades over Time')
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=90)
        plt.show()
        return self.menu
    


    def menu(self):
        """Student menu."""
        if self.student:
            self.print(f"What do you want to know about the student {self.student}?", bcolors.HEADER)
            options = {
                '1': self.get_age,
                '2': self.get_courses,
                '3': self.get_gpa,
                '4': self.get_grade_for_all_courses,
                '5': self.grades_over_time,
            }
        else:
            options = {
                '1': self.search,
                '2': self.show_all_students,
                '3': self.histogram_of_gpa,
                '4': self.gpa_vs_grade,
                '5': self.grades_by_course,
                '6': self.average_grade_for_each_students,
            }
        options['9'] = self.initial_menu
        return self.print_menu(options)

class Course(Menu):
    """Course menu."""
    course: CourseModel = None
         
    @enter_to_continue
    def count_students_enrolled(self):
        """Count the number of students enrolled in the course."""
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM enrollment
            WHERE course_id = %s;
        """, (self.course.course_id,))
        response = self.cursor.fetchone()[0]
        self.print(f"There are {response} students enrolled in the course '{self.course.course_name}'.")
        return self.menu
    
    @enter_to_continue
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
            self.print(f"The average grade for the exam type '{exam[0]}' is {exam[1]:.2f}.")
        return self.menu

    @enter_to_continue
    def find_nearest_assessment_date(self):
        """Find the nearest assessment date for the course."""
        self.cursor.execute("""
            SELECT MIN(date)
            FROM exam_event
            WHERE course_id = %s AND date >= current_date;
        """, (self.course.course_id,))
        response = self.cursor.fetchone()[0]
        self.print(f"The nearest assessment date for the course '{self.course.course_name}' is {response}.")
        return self.menu

    @enter_to_continue
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
        self.print(f"The course '{self.course.course_name}' is taught in the building '{response}'.")
        return self.menu

    @enter_to_continue
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
            self.print(f"No course found with the name {course_name}.", bcolors.FAIL)

        return None
    
    @enter_to_continue
    def show_all_courses(self):
        """Show all courses."""
        self.cursor.execute("""
            SELECT course_id, course_name
            FROM course;
        """)
        courses = self.cursor.fetchall()

        if courses:
            self.print("All courses:")
            for course in courses:
                self.print(CourseModel(course_id = course[0], course_name = course[1]))
                self.print()
        else:
            self.print("No courses found in the database.", bcolors.FAIL)

        return self.menu

    def bar_plot_number_of_students(self):
        """Show a bar plot of the number of students enrolled in each course."""
        self.cursor.execute("""
            SELECT course.course_name, COUNT(*)
            FROM enrollment
            JOIN course ON enrollment.course_id = course.course_id
            GROUP BY course.course_name
            ORDER BY COUNT(*) DESC;
        """)
        courses, counts = zip(*self.cursor.fetchall())

        if not courses or not counts:
            self.print("No courses or counts recorded for the students.", bcolors.FAIL)
            return None, self.menu

        plt.bar(courses, counts, alpha=0.7, color='b')
        plt.xlabel('Courses')
        plt.ylabel('Number of students')
        plt.title('Number of Students by Course')
        plt.grid(True)
        plt.xticks(rotation=90)
        plt.show()
        return self.menu

    def menu(self):
        """Course menu."""
        if self.course:
            self.print(f"What do you want to know about the course '{self.course.course_name}'?", bcolors.HEADER)
            options = {
                '1': self.count_students_enrolled,
                '2': self.calculate_average_grade_by_exam_type,
                '3': self.find_nearest_assessment_date,
                '4': self.find_building_for_course,
            }
        else:
            self.print("What do you want to do?", bcolors.HEADER)
            options = {
                '1': self.search_course,
                '2': self.show_all_courses,
                '3': self.bar_plot_number_of_students,
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
            self.print(f"No building found with the name {building_name}.", bcolors.FAIL)

        return None

    @enter_to_continue
    def show_all_buildings(self):
        """Show all buildings."""
        self.cursor.execute("""
            SELECT building_id, building_name
            FROM building;
        """)
        buildings = self.cursor.fetchall()

        if buildings:
            self.print("All buildings:")
            for building in buildings:
                self.print(BuildingModel(building_id=building[0], building_name=building[1]))
                self.print()
        else:
            self.print("No buildings found in the database.", bcolors.FAIL)

        return self.menu


    def menu(self):
        """Building menu."""
        if self.building:
            self.print(f"What do you want to know about the building '{self.building.building_name}'?", bcolors.HEADER)
            options = {
                '1': Room().show_rooms_from_building,
            }
        else:
            self.print("What do you want to do?", bcolors.HEADER)
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
            self.print(f"No room found with the name {room_name}.", bcolors.FAIL)

        return None

    @enter_to_continue
    def show_rooms_from_building(self, building_id):
        """Show rooms from building."""

        self.cursor.execute("""
            SELECT room_id, room_name, building_id, capacity, has_projector, has_computers, is_accessible
            FROM room
            JOIN building ON room.building_id = building.building_id
            WHERE building_id = %s;
        """, (building_id,))
        rooms = self.cursor.fetchall()
        self.print(f"Rooms in the building '{building_id}':")
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

    @enter_to_continue
    def show_all_rooms(self):
        """Show all rooms."""
        self.cursor.execute("""
            SELECT room_id, room_name, building_id, capacity, has_projector, has_computers, is_accessible
            FROM room;
        """)
        rooms = self.cursor.fetchall()

        if rooms:
            self.print("All rooms:")
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
                room_model.print_details() 
                self.print()  # Add an empty line for better readability
        else:
            self.print("No rooms found in the database.", bcolors.FAIL)

        return self.menu

    def plot_room_utilization(self):
        """Plot a bar plot of the room utilization."""
        self.cursor.execute("""
            SELECT room.room_name, COUNT(*)
            FROM assessment
            JOIN exam_event ON assessment.exam_event_id = exam_event.exam_event_id
            JOIN room ON exam_event.room_id = room.room_id
            GROUP BY room.room_name
            ORDER BY COUNT(*) DESC;
        """)
        rooms, counts = zip(*self.cursor.fetchall())

        if not rooms or not counts:
            self.print("No rooms or counts recorded for the students.", bcolors.FAIL)
            return None, self.menu

        plt.bar(rooms, counts, alpha=0.7, color='b')
        plt.xlabel('Rooms')
        plt.ylabel('Number of exams')
        plt.title('Room Utilization')
        plt.grid(True)
        plt.xticks(rotation=90)
        plt.show()
        return self.menu
    
    def show_details(self):
        """Show details of the room."""
        self.room.print_details()
        return self.menu

    def menu(self):
        """Room menu."""
        if self.room:
            self.print(f"What do you want to know about the room '{self.room.room_name}'?", bcolors.HEADER)
            options = {
                '1': self.show_details,
                '2': self.plot_room_utilization,
            }
        else:
            self.print("What do you want to do?", bcolors.HEADER)
            options = {
                '1': self.search_room,
                '2': self.show_all_rooms,
            }

        options['9'] = self.initial_menu

        return self.print_menu(options)

class ExamEvent(Menu):
    """Exam Event menu."""
    exam_event: ExamEventModel = None

    @enter_to_continue
    def search_exam_event_by_id(self):
        """Search for an exam event by ID."""
        exam_event_id = input("Enter the ID of the exam event: ")

        self.cursor.execute("""
            SELECT exam_event_id, date, exam_event.exam_type_id, course.course_id, room_id, course_name, exam_name 
            FROM exam_event
            Join exam_type on exam_event.exam_type_id = exam_type.exam_type_id
            Join course on exam_event.course_id = course.course_id
            WHERE exam_event_id = %s;
        """, (exam_event_id,))

        exam_event_info = self.cursor.fetchone()
        if exam_event_info:
            self.exam_event = ExamEventModel(
                exam_event_id=exam_event_info[0],
                date=exam_event_info[1].strftime("%Y-%m-%d"),
                exam_type_id=exam_event_info[2], 
                course_id=exam_event_info[3], 
                room_id=exam_event_info[4],
                course_name=exam_event_info[5],
                exam_name=exam_event_info[6]
                )
            return self.menu
        else:
            self.print(f"No exam event found with the ID {exam_event_id}.", bcolors.FAIL)

        return None

    @enter_to_continue
    def search_exam_event_by_date(self):
        """Search for an exam event by date."""
        date = input("Enter the date of the exam event (YYYY-MM-DD): ")

        self.cursor.execute("""
            SELECT exam_event_id, date, exam_type.exam_type_id, course.course_id, room_id, course_name, exam_name
            FROM exam_event
            JOIN exam_type ON exam_event.exam_type_id = exam_type.exam_type_id
            JOIN course ON exam_event.course_id = course.course_id
            WHERE date = %s;
        """, (date,))

        exam_event_info = self.cursor.fetchall()

        if len(exam_event_info) > 1:
            self.print("Multiple exam events found with the same date:", bcolors.WARNING)
            for i, exam_event in enumerate(exam_event_info, 1):
                exam = ExamEventModel(
                    exam_event_id=exam_event[0],
                    date=exam_event[1].strftime("%Y-%m-%d"),
                    exam_type_id=exam_event[2], 
                    course_id=exam_event[3], 
                    room_id=exam_event[4],
                    course_name=exam_event[5],
                    exam_name=exam_event[6]
                    )
                self.print(f"[{i}] {exam} )")
            choice = int(input("Select an exam event by number: "))
            if 1 <= choice <= len(exam_event_info):
                exam_event_info = exam_event_info[choice-1]
            else:
                self.print("Invalid choice.", bcolors.FAIL)
                return None
        elif len(exam_event_info) == 1:
            exam_event_info = exam_event_info[0]

        else:
            self.print(f"No exam event found on {date}.", bcolors.FAIL)
            return None
        
        self.exam_event = ExamEventModel(
            exam_event_id=exam_event_info[0], 
            date=exam_event_info[1], 
            exam_type_id=exam_event_info[2], 
            course_id=exam_event_info[3], 
            room_id=exam_event_info[4],
            course_name=exam_event_info[5],
            exam_name=exam_event_info[6]
        )
        return self.menu

    @enter_to_continue
    def calculate_average_grade(self):
        """Calculate the average grade for the exam event."""

        self.cursor.execute("""
            SELECT AVG(grade)
            FROM assessment
            WHERE exam_event_id = %s;
        """, (self.exam_event.exam_event_id,))
        response = self.cursor.fetchone()[0]
        self.print(f"The average grade for the exam event on {self.exam_event.date} is {response:.2f}.")
        return self.menu
    
    
    def get_grade_distribution(self):
        """Get the grade distribution for the exam event."""
        self.cursor.execute("""
            SELECT grade
            FROM assessment
            WHERE exam_event_id = %s
            ORDER BY grade;
        """, (self.exam_event.exam_event_id,))
        
        grades = [row[0] for row in self.cursor.fetchall()]

        if not grades:
            self.print(f"No grades recorded for the exam event on {self.exam_event.date}.", bcolors.FAIL)
            return None, self.menu

        plt.hist(grades, bins=20, alpha=0.7, color='b', edgecolor='k')
        plt.xlabel('Grades')
        plt.ylabel('Frequency')
        plt.title(f"Grade Distribution for the Exam Event on {self.exam_event.date}")
        plt.grid(True)

        plt.show()
        return self.menu

    @enter_to_continue
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
        self.print(f"Grades for the exam event on {self.exam_event.date}:")
        for grade in response:
            self.print(f"- {grade[0]} {grade[1]}: {grade[2]}")
        return self.menu

    @enter_to_continue
    def show_exam_event_details(self):
        """Show details of the selected exam event."""
        self.exam_event.print_details()

        return self.menu
    
    def show_all_exam_events(self):
        """Show all exam events."""
        self.cursor.execute("""
            SELECT exam_event_id, date, exam_event.exam_type_id, course.course_id, room_id, course_name, exam_name
            FROM exam_event
            JOIN exam_type ON exam_event.exam_type_id = exam_type.exam_type_id
            JOIN course ON exam_event.course_id = course.course_id
            ;
        """)
        exam_events = self.cursor.fetchall()

        if exam_events:
            self.print("All exam events:")
            for exam_event in exam_events:
                self.print(ExamEventModel(
                    exam_event_id=exam_event[0], 
                    date=exam_event[1], 
                    exam_type_id=exam_event[2], 
                    course_id=exam_event[3], 
                    room_id=exam_event[4],
                    course_name=exam_event[5],
                    exam_name=exam_event[6]
                ))
                self.print()
        else:
            self.print("No exam events found in the database.", bcolors.FAIL)

        return self.menu

    @enter_to_continue
    def get_exam_event_by_course(self):
        """Get the exam events for by a course name."""
        course_name = input("What course do you want to search: ")

        self.cursor.execute("""
            SELECT exam_event_id, date, exam_event.exam_type_id, course.course_id, room_id, course_name, exam_name
            FROM exam_event
            JOIN course ON exam_event.course_id = course.course_id
            JOIN exam_type ON exam_event.exam_type_id = exam_type.exam_type_id
            WHERE course_name = %s;
        """, (course_name,))

        exam_event_info = self.cursor.fetchall()
        
        if len(exam_event_info) > 1:
            self.print("Multiple exam events found for the course:", bcolors.WARNING)
            for i, exam_event in enumerate(exam_event_info, 1):
                print(exam_event)
                exam = ExamEventModel(
                    exam_event_id=exam_event[0],
                    date=exam_event[1].strftime("%Y-%m-%d"),
                    exam_type_id=exam_event[2], 
                    course_id=exam_event[3], 
                    room_id=exam_event[4],
                    course_name=exam_event[5],
                    exam_name=exam_event[6]
                    )
                self.print(f"[{i}] {exam} )")
            choice = int(input("Select an exam event by number: "))
            if 1 <= choice <= len(exam_event_info):
                exam_event_info = exam_event_info[choice-1]
            else:
                self.print("Invalid choice.", bcolors.FAIL)
                return None
        elif exam_event_info == 1:
            exam_event_info = exam_event_info[0]

        else:
            self.print(f"No exam event found for the course {course_name}.", bcolors.FAIL)

        self.exam_event = ExamEventModel(
            exam_event_id=exam_event_info[0], 
            date=exam_event_info[1], 
            exam_type_id=exam_event_info[2], 
            course_id=exam_event_info[3], 
            room_id=exam_event_info[4],
            course_name=exam_event_info[5],
            exam_name=exam_event_info[6]
        )
        return self.menu

    def menu(self):
        """Exam Event menu."""
        if self.exam_event:
            self.print(f"What do you want to know about the exam event on {self.exam_event.course_name}: {self.exam_event.exam_name}?", bcolors.HEADER)
            options = {
                '1': self.show_exam_event_details,
                '2': self.calculate_average_grade,
                '3': self.get_grade_distribution,
                '4': self.get_grade_from_students,
            }
        else:
            self.print("What do you want to do?", bcolors.HEADER)
            options = {
                '1': self.search_exam_event_by_date,
                '2': self.search_exam_event_by_id,
                '3': self.show_all_exam_events,
                '4': self.get_exam_event_by_course,
            }

        options['9'] = self.initial_menu

        return self.print_menu(options)


if __name__ == "__main__":
    Menu().run()
