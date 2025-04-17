from flask_server import db
from sqlalchemy import Column, Text, Integer, String, ForeignKey, Date, CheckConstraint
from sqlalchemy.orm import relationship, backref
from datetime import datetime


class Student(db.Model):
    __tablename__ = 'students'

    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(123), nullable=False)
    last_name = db.Column(db.String(123), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(
        db.String(6),
        db.CheckConstraint("gender IN ('Male', 'Female', 'Other')"),
        nullable=False,
    )
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    join_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    # Relationship with Department
    department = relationship('Department', back_populates='students')

    def __repr__(self):
        return f"<Student({self.first_name} {self.last_name}, Email: {self.email})>"


class Department(db.Model):
    __tablename__ = 'departments'

    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_name = db.Column(db.String(255), unique=True, nullable=False)
    head_of_department = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=True)  # <-- New column added

    # Relationship with Student
    students = relationship('Student', back_populates='department', lazy='dynamic')

    # Other Relationships
    faculty = relationship('Faculty', back_populates='department', lazy='dynamic')
    courses = relationship('Course', back_populates='department', lazy='dynamic')

    def __repr__(self):
        return f"<Department({self.department_name}, Head: {self.head_of_department})>"
class Course(db.Model):
    __tablename__ = 'courses'

    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(255), nullable=False)
    course_code = db.Column(db.String(50), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.String(50), nullable=False)

    # Relationship with Department
    department = relationship('Department', back_populates='courses')
    class_schedules = relationship('ClassSchedule', back_populates='course')
    # Many-to-Many relationship with Faculty
    faculty_members = relationship(
        'Faculty',
        secondary='faculty_course_association',
        back_populates='courses',
    )

    def __repr__(self):
        return f"<Course({self.course_name}, Code: {self.course_code}, Credits: {self.credits})>"


class Faculty(db.Model):
    __tablename__ = 'faculty'

    faculty_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(123), nullable=False)
    last_name = db.Column(db.String(123), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    department_id = db.Column(db.Integer, ForeignKey('departments.department_id'), nullable=False)
    hire_date = db.Column(Date, nullable=False)

    # Relationships
    class_schedules = relationship('ClassSchedule', back_populates='faculty')
    department = relationship('Department', back_populates='faculty')
    courses = relationship(
        'Course',
        secondary='faculty_course_association',
        back_populates='faculty_members',
    )

    def __repr__(self):
        return f"<Faculty({self.first_name} {self.last_name}, Email: {self.email})>"


# Association Table for Many-to-Many between Faculty and Course
faculty_course_association = db.Table(
    'faculty_course_association',
    db.Column('faculty_id', db.Integer, db.ForeignKey('faculty.faculty_id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.course_id'), primary_key=True),
)

class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=True)  # New column for faculty reference
    semester = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.Float, nullable=True)  # Nullable to allow grades to be set later
    total_classes = db.Column(db.Integer, nullable=True)  # New column for total classes
    classes_attended = db.Column(db.Integer, nullable=True)  # New column for classes attended

    # Relationships
    student = db.relationship('Student', backref='enrollments')
    course = db.relationship('Course', backref='enrollments')
    faculty = db.relationship('Faculty', backref='enrollments')  # New relationship for faculty

    def __repr__(self):
        return f"<Enrollment(id={self.enrollment_id}, student_id={self.student_id}, course_id={self.course_id}, faculty_id={self.faculty_id}, semester={self.semester}, grade={self.grade}, total_classes={self.total_classes}, classes_attended={self.classes_attended})>"

class ClassSchedule(db.Model):
    __tablename__ = 'class_schedule'

    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.course_id'), nullable=False)
    faculty_id = Column(Integer, ForeignKey('faculty.faculty_id'), nullable=False)
    day_of_week = Column(Text, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    room_number = Column(String)
    semester = Column(Integer, nullable=False)

    # Relationship with Course and Faculty
    course = relationship('Course', back_populates='class_schedules')
    faculty = relationship('Faculty', back_populates='class_schedules')

    def __repr__(self):
        return f"<ClassSchedule(Course ID: {self.course_id}, Faculty ID: {self.faculty_id}, Day: {self.day_of_week}, Time: {self.start_time}-{self.end_time})>"


class Admin(db.Model):
    __tablename__ = 'admin'
    
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String, nullable=True)
    role = db.Column(db.String, nullable=False, 
                     check_constraint=db.CheckConstraint("role IN ('Super Admin', 'Admin')"))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Admin(username='{self.username}', role='{self.role}')>"

