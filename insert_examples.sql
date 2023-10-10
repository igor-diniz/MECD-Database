SET SEARCH_PATH TO grades;

INSERT INTO student (first_name, last_name, email, date_of_birth)
VALUES
    ('John', 'Doe', 'john.doe@example.com', '1995-03-15'),
    ('Alice', 'Smith', 'alice.smith@example.com', '1996-07-22'),
    ('Bob', 'Johnson', 'bob.johnson@example.com', '1994-11-10'),
    ('Sarah', 'Brown', 'sarah.brown@example.com', '1997-04-30'),
    ('Michael', 'Davis', 'michael.davis@example.com', '1993-09-05');


INSERT INTO course (course_name)
VALUES
    ('Mathematics'),
    ('History'),
    ('Computer Science'),
    ('Biology'),
    ('Chemistry');


INSERT INTO exam_type (exam_name)
VALUES
    ('Midterm Exam'),
    ('Final Exam'),
    ('Quiz 1'),
    ('Quiz 2'),
    ('Project Presentation');


INSERT INTO building (building_name)
VALUES
    ('Building A'),
    ('Building B'),
    ('Main Building'),
    ('Science Center'),
    ('Library');


INSERT INTO room (room_name, building_id)
VALUES
    ('Room 101', 1),
    ('Room 201', 1),
    ('Room 102', 2),
    ('Room 301', 3),
    ('Lab 1', 4);


INSERT INTO exam_event (date, exam_type_id, course_id, room_id)
VALUES
    ('2023-10-15', 1, 1, 1),
    ('2023-11-05', 2, 2, 2),
    ('2023-09-30', 3, 3, 3),
    ('2023-12-10', 1, 4, 4),
    ('2023-10-20', 2, 5, 5);


INSERT INTO enrollment (student_id, course_id)
VALUES
    (1, 1),
    (2, 2),
    (3, 1),
    (4, 3),
    (5, 2);


INSERT INTO assessment (student_id, exam_event_id, gpa)
VALUES
    (1, 1, 3.75),
    (2, 2, 4.0),
    (3, 1, 3.5),
    (4, 3, 3.8),
    (5, 2, 3.9);
