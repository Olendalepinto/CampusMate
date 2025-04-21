from .models import   Student, Course, Admin, Department, Faculty, Enrollment, ClassSchedule
from flask_server import db, app
from flask import render_template, request, jsonify, redirect, url_for, Blueprint, send_file, flash,session
from io import BytesIO
from datetime import datetime
from werkzeug.security import check_password_hash

@app.route("/")
def hello_world():
    db.create_all()
    return render_template('frontend/index.html')

@app.route("/home1/")
def home1():
    return render_template('frontend/home.html')



@app.route("/regdep/")
def regdep():
    mode = request.args.get('mode', 'signup')
    return render_template('frontend/login/login/index.html', mode=mode)

@app.route("/faculty/", methods=['POST', 'GET'])
def faculty():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form.get('phone_number')  # Optional
        department_id = request.form['department_id']
        hire_date = request.form['hire_date']

        new_faculty = Faculty(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            department_id=department_id,
            hire_date=hire_date,
        )
        db.session.add(new_faculty)
        db.session.commit()
        return redirect(url_for('faculty'))

    faculty_list = Faculty.query.all()
    return render_template('dashboards/faculty.html', faculty=faculty_list)


@app.route("/faculty/delete/<int:id>/")
def faculty_delete(id):
    faculty_member = Faculty.query.get(id)
    if faculty_member:
        db.session.delete(faculty_member)
        db.session.commit()

    return redirect(url_for('faculty'))


@app.route("/faculty/api/")
def faculty_api():
    faculty_list = Faculty.query.all()
    return jsonify([
        {
            "name": f"{faculty.first_name} {faculty.last_name}",
            "email": faculty.email,
            "phone_number": faculty.phone_number,
            "department": faculty.department.department_name,
            "hire_date": faculty.hire_date.strftime('%Y-%m-%d'),
        } for faculty in faculty_list
    ])


@app.route("/faculty/api/<int:dept_id>/")
def department_faculty_api(dept_id):
    faculty_list = Faculty.query.filter_by(department_id=dept_id).all()
    return jsonify([
        {
            "faculty_id": faculty.faculty_id,
            "first_name": faculty.first_name,
            "last_name": faculty.last_name,
            "email": faculty.email,
            "phone_number": faculty.phone_number,
            "department": faculty.department.department_name,
            "hire_date": faculty.hire_date.strftime('%Y-%m-%d'),
        } for faculty in faculty_list
    ])

# =============================
# HOLIDAYS
# =============================

# @app.route("/holidays/", methods=['POST', 'GET'])
# def holidays():
#     if request.method == 'POST':
#         year = request.form['year']
#         data = request.files['file']
#         new_holiday = Holidays(
#             year=year, file_name=data.filename, data=data.read())
#         db.session.add(new_holiday)
#         db.session.commit()
#         print(f"{new_holiday} added")
#         return redirect(url_for('holidays'))

#     holidays = Holidays.query.all()
#     return render_template('holidays.html', holidays=holidays)


# @app.route("/holidays/download/<int:id>/")
# def holidays_file_api(id):
#     holiday = Holidays.query.filter_by(id=id).first()
#     return send_file(BytesIO(holiday.data), download_name=holiday.file_name)


# ====================================
#  STUDENTS
# ====================================
@app.route("/students/", methods=['POST', 'GET'])
def students():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        gender = request.form['gender']
        email = request.form['email']
        phone_number = request.form['phone_number']
        department_id = request.form['department_id']
        address = request.form['address']
        join_date = request.form['join_date']

        # Add new student
        new_student = Student(
            first_name=first_name,
            last_name=last_name,
            dob=datetime.strptime(dob, '%Y-%m-%d'),  # Ensure correct date format
            gender=gender,
            email=email,
            phone_number=phone_number,
            department_id=department_id,
            address=address,
            join_date=datetime.strptime(join_date, '%Y-%m-%d')  # Ensure correct date format
        )
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('students'))

    students = Student.query.all()
    return render_template('dashboards/students.html', students=students)


@app.route("/students/delete/<int:id>/")
def studentsdelete(id):
    student = Student.query.get(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('students'))


@app.route("/students/api/", methods=['GET'])
def students_api():
    students = Student.query.all()
    return jsonify([
        {
            "student_id": student.student_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "dob": student.dob.strftime('%Y-%m-%d'),
            "gender": student.gender,
            "email": student.email,
            "phone_number": student.phone_number,
            "department_id": student.department_id,
            "address": student.address,
            "join_date": student.join_date.strftime('%Y-%m-%d')
        } for student in students
    ])



@app.route("/students/update/<int:id>/", methods=['POST', 'GET'])
def studentsupdate(id):
    student = Student().query.get(id)

    if request.method == 'POST':
        student.cgpa = request.form['cgpa']
        student.name = request.form['name']
        student.id = request.form['studentID']
        # student.update(request.form)
        db.session.commit()
        return redirect(url_for('students'))

    return render_template('student_update.html', student=student)

# ====================================
#  COURSES
# ====================================


@app.route("/courses/", methods=['POST', 'GET'])
def courses():
    if request.method == 'POST':
        course_name = request.form['course_name']
        course_code = request.form['course_code']
        department_id = request.form['department_id']
        credits = request.form['credits']
        semester = request.form['semester']  # Added semester

        new_course = Course(course_name=course_name,
                            course_code=course_code,
                            department_id=department_id,
                            credits=credits,
                            semester=semester)  # Added semester
        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for('courses'))

    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route("/courses/update/<int:id>/", methods=['POST', 'GET'])
def coursesupdate(id):
    course = Course.query.get(id)

    if request.method == 'POST':
        course.course_name = request.form['course_name']
        course.course_code = request.form['course_code']
        course.department_id = request.form['department_id']
        course.credits = request.form['credits']
        course.semester = request.form['semester']  # Added semester
        db.session.commit()
        return redirect(url_for('courses'))

    return render_template('course_update.html', course=course)

@app.route("/courses/api/", methods=['GET'])
def courses_api():
    courses = Course.query.all()
    return jsonify([{
        "course_id": course.course_id,
        "course_name": course.course_name,
        "course_code": course.course_code,
        "credits": course.credits,
        "semester": course.semester,  # Added semester
        "department": {
            "id": course.department.department_id,
            "name": course.department.department_name,
            "head": course.department.head_of_department
        },
        "faculty_members": [
            {
                "faculty_id": faculty.faculty_id,
                "name": f"{faculty.first_name} {faculty.last_name}",
                "email": faculty.email,
                "phone_number": faculty.phone_number,
            } for faculty in course.faculty_members
        ]
    } for course in courses])


# ENROLLMENTS
@app.route("/enrollments/", methods=['POST', 'GET'])
def enrollments():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        semester = request.form['semester']
        grade = request.form.get('grade')  # Optional
        total_classes = request.form.get('total_classes')  # Optional
        classes_attended = request.form.get('classes_attended')  # Optional
        faculty_id = request.form.get('faculty_id')  # Optional

        new_enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            semester=semester,
            grade=grade if grade else None,  # Handle optional values
            total_classes=total_classes if total_classes else None,  # Handle optional values
            classes_attended=classes_attended if classes_attended else None,  # Handle optional values
            faculty_id=faculty_id if faculty_id else None  # Handle optional values
        )
        db.session.add(new_enrollment)
        db.session.commit()
        return redirect(url_for('enrollments'))

    enrollments = Enrollment.query.all()
    students = Student.query.all()
    courses = Course.query.all()
    faculties = Faculty.query.all()  # Get all faculty members
    return render_template('enrollments.html', enrollments=enrollments, students=students, courses=courses, faculties=faculties)


@app.route("/enrollments/update/<int:id>/", methods=['POST', 'GET'])
def enrollments_update(id):
    enrollment = Enrollment.query.get(id)

    if request.method == 'POST':
        enrollment.student_id = request.form['student_id']
        enrollment.course_id = request.form['course_id']
        enrollment.semester = request.form['semester']
        enrollment.grade = request.form.get('grade')  # Optional
        enrollment.total_classes = request.form.get('total_classes')  # Optional
        enrollment.classes_attended = request.form.get('classes_attended')  # Optional
        enrollment.faculty_id = request.form.get('faculty_id')  # Optional
        db.session.commit()
        return redirect(url_for('enrollments'))

    students = Student.query.all()
    courses = Course.query.all()
    faculties = Faculty.query.all()  # Get all faculty members
    return render_template('enrollment_update.html', enrollment=enrollment, students=students, courses=courses, faculties=faculties)


@app.route("/enrollments/delete/<int:id>/")
def enrollments_delete(id):
    enrollment = Enrollment.query.get(id)
    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()
    return redirect(url_for('enrollments'))


@app.route("/enrollments/api/", methods=['GET'])
def enrollments_api():
    enrollments = Enrollment.query.all()
    
    response_data = []
    for enrollment in enrollments:
        course_data = None
        if enrollment.course:
            course_data = {
                "course_id": enrollment.course.course_id,
                "course_name": enrollment.course.course_name,
                "course_code": enrollment.course.course_code
            }

        response_data.append({
            "enrollment_id": enrollment.enrollment_id,
            "student_id": enrollment.student_id,
            "course": course_data,  # This will be None if course is missing
            "semester": enrollment.semester,
            "grade": enrollment.grade,
            "total_classes": enrollment.total_classes,  # Include total_classes
            "classes_attended": enrollment.classes_attended,  # Include classes_attended
            "faculty_id": enrollment.faculty_id  # Include faculty_id
        })
    
    return jsonify(response_data)


#SCHEDULES

@app.route("/class_schedules/", methods=['POST', 'GET'])
def class_schedules():
    if request.method == 'POST':
        course_id = request.form['course_id']
        faculty_id = request.form['faculty_id']
        day_of_week = request.form['day_of_week']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        room_number = request.form.get('room_number')
        semester = request.form['semester']  # Added semester

        new_schedule = ClassSchedule(
            course_id=course_id,
            faculty_id=faculty_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            room_number=room_number,
            semester=semester  # Saving semester value
        )
        db.session.add(new_schedule)
        db.session.commit()
        return redirect(url_for('class_schedules'))

    schedules = ClassSchedule.query.all()
    courses = Course.query.all()
    faculty_members = Faculty.query.all()  # Load faculty members

    return render_template('class_schedules.html', schedules=schedules, courses=courses, faculty_members=faculty_members)


# Route to handle updating class schedules
@app.route("/class_schedules/update/<int:id>/", methods=['POST', 'GET'])
def class_schedules_update(id):
    schedule = ClassSchedule.query.get(id)

    if request.method == 'POST':
        schedule.course_id = request.form['course_id']
        schedule.faculty_id = request.form['faculty_id']
        schedule.day_of_week = request.form['day_of_week']
        schedule.start_time = request.form['start_time']
        schedule.end_time = request.form['end_time']
        schedule.room_number = request.form.get('room_number')  # Optional
        schedule.semester = request.form['semester']  # Updating semester value
        db.session.commit()
        return redirect(url_for('class_schedules'))

    courses = Course.query.all()
    faculty_members = Faculty.query.all()
    return render_template('class_schedule_update.html', schedule=schedule, courses=courses, faculty_members=faculty_members)


# Route to handle deleting class schedules
@app.route("/class_schedules/delete/<int:id>/")
def class_schedules_delete(id):
    schedule = ClassSchedule.query.get(id)
    if schedule:
        db.session.delete(schedule)
        db.session.commit()
    return redirect(url_for('class_schedules'))


# Route to handle class schedule data as JSON (API)
@app.route("/class_schedules/api/", methods=['GET'])
def class_schedules_api():
    class_schedules = ClassSchedule.query.all()

    response_data = []
    for schedule in class_schedules:
        # Collect associated course and faculty data
        course_data = {
            "course_id": schedule.course.course_id,
            "course_name": schedule.course.course_name,
            "course_code": schedule.course.course_code,
            "semester": schedule.semester  # Adding semester to the API response
        }

        faculty_data = {
            "faculty_id": schedule.faculty.faculty_id,
            "faculty_name": f"{schedule.faculty.first_name} {schedule.faculty.last_name}",
            "faculty_email": schedule.faculty.email
        }

        response_data.append({
            "schedule_id": schedule.schedule_id,
            "course": course_data,
            "faculty": faculty_data,
            "day_of_week": schedule.day_of_week,
            "start_time": schedule.start_time,
            "end_time": schedule.end_time,
            "room_number": schedule.room_number,
            "semester": schedule.semester  # Adding semester to the response data
        })

    return jsonify(response_data)

# ADMIN

@app.route("/admins/", methods=['POST', 'GET'])
def admins():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone_number = request.form['phone_number']
        role = request.form['role']

        # Add new admin
        new_admin = Admin(
            username=username,
            password=password,  # Make sure to hash the password before storing it
            email=email,
            phone_number=phone_number,
            role=role
        )
        db.session.add(new_admin)
        db.session.commit()
        return redirect(url_for('admins'))

    admins = Admin.query.all()
    return render_template('dashboards/admins.html', admins=admins)


@app.route("/admins/delete/<int:id>/")
def adminsdelete(id):
    admin = Admin.query.get(id)
    db.session.delete(admin)
    db.session.commit()
    return redirect(url_for('admins'))


@app.route("/admins/api/", methods=['GET'])
def admins_api():
    admins = Admin.query.all()
    return jsonify([
        {
            "id": admin.admin_id,
            "username": admin.username,
            "email": admin.email,
            "phone_number": admin.phone_number,
            "role": admin.role,
            "created_at": admin.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for admin in admins
    ])

# DEPARTMENTS
@app.route("/departments/", methods=['POST', 'GET'])
def departments():
    if request.method == 'POST':
        department_name = request.form['department_name']
        head_of_department = request.form['head_of_department']

        new_department = Department(department_name=department_name, 
                                    head_of_department=head_of_department)
        db.session.add(new_department)
        db.session.commit()
        return redirect(url_for('departments'))

    departments = Department.query.all()
    return render_template('departments.html', departments=departments)


@app.route("/departments/update/<int:id>/", methods=['POST', 'GET'])
def departments_update(id):
    department = Department.query.get(id)

    if request.method == 'POST':
        department.department_name = request.form['department_name']
        department.head_of_department = request.form['head_of_department']
        db.session.commit()
        return redirect(url_for('departments'))

    return render_template('department_update.html', department=department)


@app.route("/departments/api/", methods=['GET'])
def departments_api():
    departments = Department.query.all()
    return jsonify([
        {
            "department_id": department.department_id,
            "department_name": department.department_name,
            "head_of_department": department.head_of_department
        } for department in departments
    ])

app.config['SECRET_KEY'] = 'b6c44b8f1f7c69eec9e9fba3562fe046d0b7043eb5d991f19a86ea96a4b67b9a'

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the database for matching admin
        admin = Admin.query.filter_by(email=email, password=password).first()

        if admin:
            # Set session and redirect to dashboard
            session['admin_id'] = admin.admin_id
            session['admin_email'] = admin.email
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            # Flash error and render login page again
            flash('Invalid credentials. Please try again.', 'danger')
            return render_template('frontend/admin-login/index.html')

    # Render login form for GET
    return render_template('frontend/admin-login/index.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin_id' not in session:
        flash('You must be logged in to access the dashboard.', 'danger')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'add_student':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
            gender = request.form['gender']
            email = request.form['email']
            phone_number = request.form['phone_number']
            department_id = request.form['department_id']
            address = request.form['address']
            join_date = datetime.strptime(request.form['join_date'], '%Y-%m-%d')

            new_student = Student(
                first_name=first_name,
                last_name=last_name,
                dob=dob,
                gender=gender,
                email=email,
                phone_number=phone_number,
                department_id=department_id,
                address=address,
                join_date=join_date
            )
            db.session.add(new_student)
            db.session.commit()
            flash('New student added successfully!', 'success')

        elif form_type == 'edit_student':
            student_id = request.form.get('student_id')
            student = Student.query.get(student_id)

            if student:
                student.first_name = request.form['first_name']
                student.last_name = request.form['last_name']
                student.dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
                student.gender = request.form['gender']
                student.email = request.form['email']
                student.phone_number = request.form['phone_number']
                student.department_id = request.form['department_id']
                student.address = request.form['address']
                student.join_date = datetime.strptime(request.form['join_date'], '%Y-%m-%d')
                db.session.commit()
                flash('Student updated successfully!', 'success')
            else:
                flash('Student not found!', 'danger')

        elif form_type == 'delete_student':
            student_id = request.form.get('student_id')
            student = Student.query.get(student_id)
            if student:
                db.session.delete(student)
                db.session.commit()
                flash('Student deleted successfully!', 'success')
            else:
                flash('Student not found!', 'danger')

        elif form_type == 'add_faculty':
            faculty_id = request.form.get('faculty_id')
            if faculty_id:  # Editing existing faculty
                faculty_member = Faculty.query.get(faculty_id)
                if faculty_member:
                    faculty_member.first_name = request.form['first_name']
                    faculty_member.last_name = request.form['last_name']
                    faculty_member.email = request.form['email']
                    faculty_member.phone_number = request.form.get('phone_number')
                    faculty_member.department_id = request.form['department_id']
                    faculty_member.hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d')
                    db.session.commit()
                    flash('Faculty updated successfully!', 'success')
                else:
                    flash('Faculty not found!', 'danger')
            else:  # Adding new faculty
                new_faculty = Faculty(
                    first_name=request.form['first_name'],
                    last_name=request.form['last_name'],
                    email=request.form['email'],
                    phone_number=request.form.get('phone_number'),
                    department_id=request.form['department_id'],
                    hire_date=datetime.strptime(request.form['hire_date'], '%Y-%m-%d')
                )
                db.session.add(new_faculty)
                db.session.commit()
                flash('New faculty member added successfully!', 'success')

        elif form_type == 'delete_faculty':
            faculty_id = request.form.get('faculty_id')
            faculty_member = Faculty.query.get(faculty_id)
            if faculty_member:
                db.session.delete(faculty_member)
                db.session.commit()
                flash('Faculty member deleted successfully!', 'success')
            else:
                flash('Faculty member not found!', 'danger')

        elif form_type == 'add_department':
            department_name = request.form['department_name']
            head_id = request.form['head_of_department']
            new_department = Department(
                department_name=department_name,
                head_of_department=head_id
            )
            db.session.add(new_department)
            db.session.commit()
            flash('New department added successfully!', 'success')

        elif form_type == 'edit_department':
            department_id = request.form.get('department_id')
            department = Department.query.get(department_id)
            if department:
                department.department_name = request.form['department_name']
                department.head_of_department = request.form['head_of_department']
                db.session.commit()
                flash('Department updated successfully!', 'success')
            else:
                flash('Department not found!', 'danger')

        elif form_type == 'delete_department':
            department_id = request.form.get('department_id')
            department = Department.query.get(department_id)
            if department:
                db.session.delete(department)
                db.session.commit()
                flash('Department deleted successfully!', 'success')
            else:
                flash('Department not found!', 'danger')

        elif form_type == 'add_course':
            course_name = request.form['course_name']
            course_code = request.form['course_code']
            department_id = request.form['department_id']
            credits = request.form['credits']
            semester = request.form['semester']

            new_course = Course(
                course_name=course_name,
                course_code=course_code,
                department_id=department_id,
                credits=credits,
                semester=semester
            )
            db.session.add(new_course)
            db.session.commit()
            flash('New course added successfully!', 'success')

        return redirect(url_for('admin_dashboard'))

    # GET request handling
    students = Student.query.all()
    faculty = Faculty.query.all()
    departments = Department.query.all()
    courses = Course.query.all()

    return render_template('dashboards/admins.html',
                           students=students,
                           faculty=faculty,
                           departments=departments,
                           courses=courses)



@app.route("/admin/faculty/delete/<int:id>/", methods=['POST'])
def admin_faculty_delete(id):
    if 'admin_id' in session:
        faculty_member = Faculty.query.get_or_404(id)
        db.session.delete(faculty_member)
        db.session.commit()
        flash('Faculty deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/")
def admin():
    # Redirect /admin/ to login
    return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('hello_world'))  # This should take you to index.html



@app.route("/home2/")
def hello_world2():
    # Render the faculty login page
    return render_template('frontend/login/login/index.html')


@app.route('/faculty/login', methods=['GET', 'POST'])
def faculty_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        faculty = Faculty.query.filter_by(email=email).first()
        if faculty and password.lower() == faculty.first_name.lower():
            # Save faculty info in session
            session['faculty_id'] = faculty.faculty_id
            session['faculty_name'] = f"{faculty.first_name} {faculty.last_name}"
            session['department_name'] = faculty.department.department_name
            flash('Login successful!', 'success')
            return redirect(url_for('faculty_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('frontend/index.html')

@app.route('/faculty/logout')
def faculty_logout():
    session.pop('faculty_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('faculty_login'))




@app.route('/department/login', methods=['GET', 'POST'])
def department_login():
    if request.method == 'POST':
        department_name = request.form['department_name']
        password = request.form['password']

        # Find the department with matching credentials
        department = Department.query.filter_by(department_name=department_name, password=password).first()

        if department:
            session['department_id'] = department.department_id
            session['department_name'] = department.department_name
            # flash('Department login successful!', 'success')
            return redirect(url_for('department_dashboard'))  # Create this view
        else:
            flash('Invalid department credentials.', 'danger')
    
    return render_template('frontend/admin-login/index.html')
@app.route('/department/dashboard', methods=['GET', 'POST'])
def department_dashboard():
    if 'department_id' not in session:
        flash('Please log in to access the department dashboard.', 'warning')
        return redirect(url_for('department_login'))

    # Fetch department details
    department_id = session.get('department_id')
    department = Department.query.get(department_id)

    if not department:
        flash('Department not found.', 'danger')
        return redirect(url_for('department_login'))

    # Fetch all courses under this department
    courses = Course.query.filter_by(department_id=department_id).all()
    course_ids = [course.course_id for course in courses]

    # Fetch enrollments only from courses in this department
    enrollments = Enrollment.query.filter(Enrollment.course_id.in_(course_ids)).all()

    # Fetch students and faculty under this department
    students = Student.query.filter_by(department_id=department_id).all()
    faculties = Faculty.query.filter_by(department_id=department_id).all()

    # Fetch all class schedules for this department's courses
    class_schedules = ClassSchedule.query.join(Course).filter(Course.department_id == department_id).all()

    # Handle form submission for adding a new enrollment
    if request.method == 'POST' and request.form.get('form_type') == 'add_enrollment':
        student_id = request.form.get('student_id')
        course_id = request.form.get('course_id')
        faculty_id = request.form.get('faculty_id') or None
        semester = request.form.get('semester', type=int)
        grade = request.form.get('grade', type=float)
        total_classes = request.form.get('total_classes', type=int)
        classes_attended = request.form.get('classes_attended', type=int)

        # Check for semester range
        if semester < 1 or semester > 8:
            flash("Semester must be between 1 and 8.", 'danger')
            return redirect(url_for('department_dashboard'))

        # Check for valid classes attended
        if classes_attended > total_classes:
            flash("Classes attended cannot be greater than total classes.", 'danger')
            return redirect(url_for('department_dashboard'))

        # Create the new enrollment
        new_enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            faculty_id=faculty_id,
            semester=semester,
            grade=grade,
            total_classes=total_classes,
            classes_attended=classes_attended
        )
        
        db.session.add(new_enrollment)
        db.session.commit()
        flash("Enrollment successfully added!", 'success')
        return redirect(url_for('department_dashboard'))

    return render_template(
        'dashboards/dept.html',
        department=department,
        courses=courses,
        enrollments=enrollments,
        students=students,
        faculties=faculties,
        class_schedules=class_schedules  # Passing class schedules to the template
    )


@app.route('/department/logout')
def department_logout():
    session.pop('department_id', None)
    session.pop('department_name', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('hello_world'))  # 👈 Redirect to home screen
@app.route('/faculty/dashboard', methods=['GET', 'POST'])
def faculty_dashboard():
    faculty_id = session.get('faculty_id')
    if not faculty_id:
        flash('Please log in to access the faculty dashboard.', 'warning')
        return redirect(url_for('faculty_login'))

    faculty = Faculty.query.get(faculty_id)

    # ✅ Fetch distinct courses taught by this faculty through enrollments
    courses = db.session.query(Course).join(Enrollment).filter(
        Enrollment.faculty_id == faculty_id
    ).distinct().all()

    selected_course_id = request.form.get('course_id')
    selected_semester = request.form.get('semester')
    enrollments = []

    # ✅ Handle update
    if request.method == 'POST' and request.form.get('form_type') == 'update_enrollment':
        enrollment_id = int(request.form.get('enrollment_id'))
        grade = request.form.get('grade', type=float)
        total_classes = request.form.get('total_classes', type=int)
        classes_attended = request.form.get('classes_attended', type=int)

        enrollment = Enrollment.query.get(enrollment_id)
        if enrollment and enrollment.faculty_id == faculty_id:
            enrollment.grade = grade
            enrollment.total_classes = total_classes
            enrollment.classes_attended = classes_attended
            db.session.commit()
            flash("Enrollment updated successfully!", "success")
        else:
            flash("Invalid enrollment or unauthorized access.", "danger")
        return redirect(url_for('faculty_dashboard'))

    # ✅ Fetch enrollments if course and semester selected
    if selected_course_id and selected_semester:
        enrollments = Enrollment.query.join(Course).join(Student).filter(
            Enrollment.course_id == selected_course_id,
            Enrollment.semester == selected_semester,
            Enrollment.faculty_id == faculty_id
        ).all()

    return render_template(
        'dashboards/faculty_dash.html',
        faculty=faculty,
        courses=courses,
        enrollments=enrollments,
        selected_course_id=selected_course_id,
        selected_semester=selected_semester
    )
