CREATE SCHEMA IF NOT EXISTS grades;
SET SEARCH_PATH TO grades;

-- Drop the tables to run this script whenever necessary without problems
DROP TABLE IF EXISTS assessment;
DROP TABLE IF EXISTS enrollment;
DROP TABLE IF EXISTS exam_event;
DROP TABLE IF EXISTS room;
DROP TABLE IF EXISTS building;
DROP TABLE IF EXISTS exam_type;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS state;


-- Create scripts

CREATE TABLE state (
    state_id SERIAL PRIMARY KEY,
    state_name TEXT NOT NULL
);


CREATE TABLE student (
    student_id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    gpa NUMERIC(3,2) NOT NULL CHECK (gpa >= 0 AND gpa <= 4),
    state_id INTEGER NOT NULL,
    FOREIGN KEY (state_id) REFERENCES State
);


CREATE TABLE course (
    course_id SERIAL PRIMARY KEY,
    course_name TEXT NOT NULL UNIQUE
);


CREATE TABLE exam_type (
    exam_type_id SERIAL PRIMARY KEY,
    exam_name TEXT NOT NULL UNIQUE
);


CREATE TABLE building (
    building_id SERIAL PRIMARY KEY,
    building_name TEXT NOT NULL UNIQUE
);


CREATE TABLE room (
    room_id SERIAL PRIMARY KEY,
    room_name TEXT NOT NULL UNIQUE,
    building_id INTEGER NOT NULL,
    capacity INTEGER NOT NULL,
    has_projector BOOLEAN NOT NULL,
    has_computers BOOLEAN NOT NULL,
    is_accessible BOOLEAN NOT NULL,
    FOREIGN KEY (building_id) REFERENCES building
);


CREATE TABLE exam_event (
    exam_event_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    exam_type_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    FOREIGN KEY (exam_type_id) REFERENCES exam_type,
    FOREIGN KEY (course_id) REFERENCES course,
    FOREIGN KEY (room_id) REFERENCES room,
    UNIQUE (date, room_id, exam_type_id)
);


CREATE TABLE enrollment (
    student_id INTEGER,
    course_id INTEGER,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES student,
    FOREIGN KEY (course_id) REFERENCES course
);


CREATE TABLE assessment (
    student_id INTEGER,
    exam_event_id INTEGER,
    grade NUMERIC(5, 2) NOT NULL CHECK (grade >= 0 AND grade <= 100),
    PRIMARY KEY (student_id, exam_event_id),
    FOREIGN KEY (student_id) REFERENCES student (student_id),
    FOREIGN KEY (exam_event_id) REFERENCES exam_event (exam_event_id)
);
