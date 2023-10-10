# MECD Database Project

## UML designed for the grades CSV
<img src="uml.png" with="600px" height="470px">

## Relational Model from UML
1. Student (<u>**student_id**</u>, first_name [NN], last_name [NN], email [NN][UK], date_of_birth, [NN])

2. Course (<u>**course_id**</u>, course_name [NN][UK])

3. ExamType (<u>**exam_type_id**</u>, exam_name [NN][UK])

4. Building (<u>**building_id**</u>, building_name [NN][UK])

5. Room (<u>**room_id**</u>, room_name [NN][UK], #building_id -> Building [NN])

6. ExamEvent (<u>**exam_event_id**</u>, date [NN], #exam_type_id -> ExamType [NN], 
	   #course_id -> Course [NN], #room_id -> Room [NN])

7. Enrollment (<u>**#student_id -> Student**</u>, <u>**#course_id -> Course**</u>)

8. Assessment (<u>**#student_id -> Student**</u>, <u>**#exam_event_id -> ExamEvent**</u>, gpa [NN])

## Tables Creation Script
[Click here](grades.sql) to check out the creation script for the database tables over the **grades** schema.





