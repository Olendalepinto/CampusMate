from flask import render_template, request, jsonify, redirect, url_for
import requests
import random
from flask_server import app, db
import flask_server.university
from flask_server.university.models import  Student, Course, Admin, Department, Faculty, Enrollment, ClassSchedule
from chat import chatbot_response,intents
from flask_server.university.nlp_utils import course_matcher
from sqlalchemy.exc import SQLAlchemyError

with app.app_context(): 
    db.create_all()

@app.post("/chatbot_api/")
def normal_chat():
    msg = request.get_json().get('message')
    response, tag = chatbot_response(msg)

    if tag == 'result':
        return jsonify({'response': response, 'tag': tag, 'url': 'result/'})
    if tag == 'find_sgpa':
        return jsonify({'response': response, 'tag': tag, 'url': 'find_sgpa/'})
    if tag == 'find_cgpa':
        return jsonify({'response': response, 'tag': tag, 'url': 'find_cgpa/'})     
    if tag == 'find_attendance':
        return jsonify({'response': response, 'tag': tag, 'url': 'find_attendance/'})
    if tag == 'faculty_details':
        return jsonify({'response': response, 'tag': tag, 'url': 'faculty_details/'})

    # if tag == 'greeting':
    #     # Find the intent that matches the 'greeting' tag
    #     for intent in intents['intents']:
    #         if intent['tag'] == tag:
    #             # Select a random response from the responses defined in intents.json
    #             response = random.choice(intent['responses'])
    #             return jsonify({'response': response, 'tag': tag})

    if tag == 'courses':
        course = course_matcher(msg)
        if course is not None:
            course_details = Course.query.filter_by(course_name=course).first()  # Use 'course_name' based on the model
            if course_details:
                response = f"{course_details.course_name} is a course with code {course_details.course_code} and {course_details.credits} credits."
                return jsonify({
                    'response': response,
                    'tag': tag,
                    "data": {
                        "course_name": course_details.course_name,
                        "course_code": course_details.course_code,
                        "credits": course_details.credits
                    }
                })
            else:
                response = f"Course {course} not found in the database."
        else:
            courses = Course.query.all()
            response = "Available courses:\n"
            for course in courses:
                # Using course_name and credits from the Course model
                response += f"\n{course.course_name} (Code: {course.course_code}, {course.credits} credits)"
            return jsonify({
                'response': response,
                'tag': tag
            })


    # if tag == "holidays":
    #     holiday = Holidays.query.first()
    #     if holiday:
    #         link = f"http://127.0.0.1:5000/holidays/download/{holiday.id}/"
    #         response = f"Holidays for year {holiday.year} are available below"
    #         return jsonify({
    #             'response': response,
    #             'tag': tag,
    #             "data": {
    #                 "filename": holiday.file_name,
    #                 "link": link
    #             }
    #         })
    #     else:
    #         response = "No holiday information available."
            
    if tag == 'faculty':
        try:
            data = requests.get(url='http://127.0.0.1:5000/teachers/api/')
            response = "Faculty details:\n"
            for item in data.json():
                teacher = f"{item['name']} ({item['department']})"
                response += "\n" + teacher
        except Exception as e:
            response = f"Failed to fetch faculty details. Error: {e}"

    if tag == 'admin':
        response = "Admin details are:\n"
        try:
            data = requests.get(url='http://127.0.0.1:5000/admins/api/')
            admin_list = data.json()  # Fetch JSON response
            for admin in admin_list:
                admin_details = (
                    f"Username: {admin['username']}, "
                    f"Phone: {admin['phone_number']}, "
                    f"Role: {admin['role']} "
                )
                response += admin_details + "\n"
        except Exception as e:
            response = f"Failed to fetch admin details. Error: {e}"

    if tag == 'departments':
        # Fetch all departments from the database
        departments = Department.query.all()
        if departments:
            response = "The available departments are:\n"
            for department in departments:
                response += f"- {department.department_name} (Head: {department.head_of_department})\n"
        else:
            response = "No departments found in the database."
        return jsonify({'response': response, 'tag': tag})
    

    return jsonify({'response': response, 'tag': tag})


@app.post("/chatbot_api/find_sgpa/")
def find_sgpa():
    try:
        # Get JSON input
        data = request.get_json()
        msg = data.get("message", "").strip()

        # Parse the input message to extract student_id and semester
        input_data = msg.split(",")
        if len(input_data) != 2:
            return jsonify({
                "response": "Please provide both student ID and semester in the format: 'student_id,semester'.",
                "url": ""
            })

        student_id, semester = map(int, input_data)

        # Fetch all enrollments for the student in the specified semester
        enrollments = db.session.query(Enrollment).filter_by(student_id=student_id, semester=semester).all()
        if not enrollments:
            return jsonify({
                "response": f"No courses found for semester {semester}.",
                "url": ""
            })

        # Initialize variables for grade point calculation
        total_credits = 0
        total_points = 0

        for enrollment in enrollments:
            course = db.session.query(Course).filter_by(course_id=enrollment.course_id).first()
            if course and enrollment.grade is not None:
                total_credits += course.credits
                total_points += enrollment.grade * course.credits

        if total_credits == 0:
            return jsonify({
                "response": "No valid courses with grades found for SGPA calculation.",
                "url": ""
            })

        # Calculate SGPA
        sgpa = total_points / total_credits
        return jsonify({
            "response": f"Your SGPA for semester {semester} is {sgpa:.2f}.",
            "url": ""
        })

    except ValueError:
        return jsonify({
            "response": "Invalid input format. Please use 'student_id,semester' where both are integers.",
            "url": ""
        })
    except SQLAlchemyError as db_error:
        return jsonify({
            "response": f"Database error occurred: {db_error}",
            "url": ""
        })
    except Exception as e:
        return jsonify({
            "response": f"An unexpected error occurred: {e}",
            "url": ""
        })
@app.post("/chatbot_api/find_cgpa/")
def find_cgpa():
    try:
        # Get JSON input
        data = request.get_json()
        msg = data.get("message", "").strip()

        # Validate and parse student ID
        try:
            student_id = int(msg)
        except ValueError:
            return jsonify({
                "response": "Invalid student ID. Please enter a valid numeric student ID.",
                "url": ""
            })

        # Fetch all enrollments for the student across all semesters
        enrollments = db.session.query(Enrollment).filter_by(student_id=student_id).all()

        if not enrollments:
            return jsonify({
                "response": f"No enrollments found for student ID {student_id}.",
                "url": ""
            })

        # Initialize CGPA calculation variables
        total_credits = 0
        total_points = 0

        for enrollment in enrollments:
            course = db.session.query(Course).filter_by(course_id=enrollment.course_id).first()
            if course and enrollment.grade is not None:
                total_credits += course.credits
                total_points += enrollment.grade * course.credits

        if total_credits == 0:
            return jsonify({
                "response": "No valid graded courses found for CGPA calculation.",
                "url": ""
            })

        # Calculate CGPA
        cgpa = total_points / total_credits
        return jsonify({
            "response": f"Your CGPA is {cgpa:.2f}.",
            "url": ""
        })

    except SQLAlchemyError as db_error:
        return jsonify({
            "response": f"Database error occurred: {db_error}",
            "url": ""
        })
    except Exception as e:
        return jsonify({
            "response": f"An unexpected error occurred: {e}",
            "url": ""
        })
@app.post("/chatbot_api/find_attendance/")
def find_attendance():
    try:
        # Get JSON input
        data = request.get_json()
        msg = data.get("message", "").strip()

        # Parse the input message to extract student_id and course_id
        input_data = msg.split(",")
        if len(input_data) != 2:
            return jsonify({
                "response": "Please provide both student ID and course ID in the format: 'student_id,course_id'.",
                "url": ""
            })

        student_id, course_id = map(int, input_data)

        # Fetch the specific enrollment
        enrollment = db.session.query(Enrollment).filter_by(student_id=student_id, course_id=course_id).first()
        if not enrollment:
            return jsonify({
                "response": f"No enrollment found for student ID {student_id} in course ID {course_id}.",
                "url": ""
            })

        if enrollment.total_classes is None or enrollment.classes_attended is None or enrollment.total_classes == 0:
            return jsonify({
                "response": "Insufficient attendance data to calculate percentage.",
                "url": ""
            })

        # Calculate attendance percentage
        attendance_percentage = (enrollment.classes_attended / enrollment.total_classes) * 100

        return jsonify({
            "response": f"Your attendance for course ID {course_id} is {attendance_percentage:.2f}%.",
            "url": ""
        })

    except ValueError:
        return jsonify({
            "response": "Invalid input format. Please use 'student_id,course_id' where both are integers.",
            "url": ""
        })
    except SQLAlchemyError as db_error:
        return jsonify({
            "response": f"Database error occurred: {db_error}",
            "url": ""
        })
    except Exception as e:
        return jsonify({
            "response": f"An unexpected error occurred: {e}",
            "url": ""
        })
@app.post('/chatbot_api/faculty_details/')
def get_faculty_details():
    try:
        # Parse input JSON
        data = request.get_json()
        msg = data.get("message", "").strip()

        # Expecting format: "FirstName LastName"
        input_parts = msg.split()
        if len(input_parts) != 2:
            return jsonify({
                "response": "Please provide both first and last name in the format: 'FirstName LastName'.",
                "url": ""
            })

        first_name, last_name = map(str.strip, input_parts)

        # Case-insensitive query using ilike
        faculty = db.session.query(Faculty).filter(
            Faculty.first_name.ilike(first_name),
            Faculty.last_name.ilike(last_name)
        ).first()

        if not faculty:
            return jsonify({
                "response": f"No faculty member found with the name {first_name} {last_name}.",
                "url": ""
            })

        # Fetch department info
        department = db.session.query(Department).filter_by(department_id=faculty.department_id).first()
        response = (
            f"Name: {faculty.first_name} {faculty.last_name}\n"
            f"Email: {faculty.email}\n"
            f"Phone: {faculty.phone_number or 'N/A'}\n"
            f"Department: {department.department_name if department else 'Unknown'}"
        )

        return jsonify({
            "response": response,
            "url": ""
        })

    except Exception as e:
        return jsonify({
            "response": f"An error occurred: {e}",
            "url": ""
        })

@app.route("/admins/api/", methods=['GET'])
def fetch_admins():
    """
    Fetch all admin details from the database.
    """
    admins = Admin.query.all()
    admin_data = [{
        "id": admin.admin_id,
        "username": admin.username,
        "email": admin.email,
        "phone_number": admin.phone_number,
        "role": admin.role,
        "created_at": admin.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for admin in admins]

    return jsonify(admin_data)
