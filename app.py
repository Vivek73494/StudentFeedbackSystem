import os
from datetime import datetime
from flask import Flask, jsonify, request, session, render_template, redirect, send_from_directory
from flask_cors import CORS
from bson.objectid import ObjectId

from database_config import DatabaseConfig
from db_operations import (
    DBOperations,
    initialize_default_users,
    get_all_feedback_questions,
    get_student_feedback,
    get_faculty_feedback,
    delete_feedback_question,
    get_all_feedback,
    serialize_doc
)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')

# Configure Flask-CORS for React frontend communication
CORS(
    app,
    supports_credentials=True,
    origins=r".*",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"]
)

# Initialize default users on startup
initialize_default_users()


# ==========================================================
# AUTHENTICATION HELPERS
# ==========================================================
def get_current_user():
    """Extract authenticated user from Flask session or Authorization header"""
    # 1. Check Flask session
    if 'user' in session:
        return session['user']
    
    # 2. Check Authorization Header (Bearer username:role)
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
        parts = token.split(':', 1)
        if len(parts) == 2:
            username, role = parts[0], parts[1]
            user = DBOperations.get_user(username, role)
            if user:
                user['role'] = role
                return user
            elif role == 'admin' and username.lower() == 'admin':
                return {'username': 'admin', 'role': 'admin', 'name': 'System Administrator'}
    return None


# ==========================================================
# REST API: AUTHENTICATION
# ==========================================================
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Unified user login for Student, Faculty, and Admin"""
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()
    role = str(data.get('role', '')).strip().lower()
    
    if not username or not password or not role:
        return jsonify({'error': 'Username, password, and role are required'}), 400
    
    authenticated = False
    user_info = None
    
    if role == 'student':
        student_doc = DBOperations.find_student_user(username, password)
        if student_doc:
            authenticated = True
            canonical_username = student_doc.get('username', username)
            user_info = {
                'username': canonical_username,
                'name': student_doc.get('name') or student_doc.get('student_name', canonical_username),
                'role': 'student',
                'email': student_doc.get('student_email', ''),
                'roll_number': student_doc.get('roll_number', '')
            }
            session['student'] = canonical_username
    
    elif role == 'faculty':
        faculty_doc = DBOperations.find_faculty_user(username, password)
        if faculty_doc:
            authenticated = True
            canonical_username = faculty_doc.get('username', username)
            user_info = {
                'username': canonical_username,
                'name': faculty_doc.get('name') or faculty_doc.get('faculty_name', canonical_username),
                'role': 'faculty',
                'course_name': faculty_doc.get('course_name', ''),
                'course_code': faculty_doc.get('course_code', ''),
                'department': faculty_doc.get('department', '')
            }
            session['faculty'] = canonical_username
            
    elif role == 'admin':
        admin_doc = DBOperations.find_admin_user(username, password)
        if admin_doc:
            authenticated = True
            canonical_username = admin_doc.get('username', username)
            user_info = {
                'username': canonical_username,
                'name': admin_doc.get('name', 'System Administrator'),
                'role': 'admin'
            }
            session['admin'] = canonical_username
    else:
        return jsonify({'error': f"Invalid role: '{role}'. Must be student, faculty, or admin"}), 400

    if not authenticated:
        return jsonify({'error': 'Invalid username or password'}), 401
    
    session['user'] = user_info
    # Provide simple token for decoupled clients
    token = f"{username}:{role}"
    
    return jsonify({
        'message': f"{role.capitalize()} login successful",
        'token': token,
        'user': user_info
    }), 200


@app.route('/api/auth/student/login', methods=['POST'])
def api_student_login():
    """Specific student login endpoint"""
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    return api_login_with_role(data, 'student')


@app.route('/api/auth/faculty/login', methods=['POST'])
def api_faculty_login():
    """Specific faculty login endpoint"""
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    return api_login_with_role(data, 'faculty')


@app.route('/api/auth/admin/login', methods=['POST'])
def api_admin_login():
    """Specific admin login endpoint"""
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    return api_login_with_role(data, 'admin')


def api_login_with_role(data, forced_role):
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    req_dict = {'username': username, 'password': password, 'role': forced_role}
    # Mock request body for api_login
    with app.test_request_context(json=req_dict):
        return api_login()


@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """Logout endpoint"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/auth/me', methods=['GET'])
def api_me():
    """Get currently logged-in user profile"""
    user = get_current_user()
    if user:
        return jsonify({'authenticated': True, 'user': user}), 200
    return jsonify({'authenticated': False, 'user': None}), 200


@app.route('/api/auth/register', methods=['POST'])
def api_register_student():
    """Student registration endpoint"""
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip() or data.get('student_name', '').strip()
    email = data.get('student_email', '').strip() or data.get('email', '').strip()
    roll_number = data.get('roll_number', '').strip()
    
    if not username or not password or not name:
        return jsonify({'error': 'Username, password, and name are required'}), 400
    
    student_data = {
        'username': username,
        'password': password,
        'name': name,
        'student_email': email,
        'roll_number': roll_number,
        'registered_at': datetime.now()
    }
    
    try:
        DBOperations.add_student(student_data)
        return jsonify({'message': 'Student registered successfully', 'username': username}), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 409
    except Exception as e:
        return jsonify({'error': f"Failed to register student: {str(e)}"}), 500


# ==========================================================
# REST API: COURSES
# ==========================================================
@app.route('/api/courses', methods=['GET'])
def api_get_courses():
    """Retrieve all available courses"""
    courses = DBOperations.get_all_courses()
    return jsonify(courses), 200


@app.route('/api/courses', methods=['POST'])
def api_add_course():
    """Add a new course (Admin operation)"""
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    course_name = data.get('course_name', '').strip()
    course_code = data.get('course_code', '').strip().upper()
    
    if not course_name or not course_code:
        return jsonify({'error': 'Both course_name and course_code are required'}), 400
    
    course_data = {
        'course_name': course_name,
        'course_code': course_code
    }
    
    try:
        DBOperations.add_course(course_data)
        return jsonify({
            'message': f"Course '{course_name}' ({course_code}) added successfully",
            'course': serialize_doc(course_data)
        }), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 409
    except Exception as e:
        return jsonify({'error': f"Failed to add course: {str(e)}"}), 500


@app.route('/api/courses/<course_code>', methods=['DELETE'])
def api_delete_course(course_code):
    """Delete a course by course_code (Admin operation)"""
    if not course_code:
        return jsonify({'error': 'Course code is required'}), 400
    
    deleted = DBOperations.delete_course(course_code)
    if deleted:
        return jsonify({'message': f"Course '{course_code}' deleted successfully"}), 200
    return jsonify({'error': f"Course '{course_code}' not found"}), 404


# ==========================================================
# REST API: FEEDBACK QUESTIONS
# ==========================================================
@app.route('/api/feedback/questions', methods=['GET'])
@app.route('/api/questions', methods=['GET'])
def api_get_questions():
    """Retrieve all feedback questions"""
    questions = get_all_feedback_questions()
    return jsonify(questions), 200


@app.route('/api/feedback/questions', methods=['POST'])
@app.route('/api/questions', methods=['POST'])
def api_add_question():
    """Add a feedback question (Admin operation)"""
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    question_text = data.get('question_text', '').strip()
    question_type = data.get('question_type', '').strip().lower()
    
    if not question_text:
        return jsonify({'error': 'Question text is required'}), 400
    if question_type not in ['rating', 'text']:
        return jsonify({'error': "Question type must be either 'rating' or 'text'"}), 400
    
    question_data = {
        'question_text': question_text,
        'question_type': question_type
    }
    
    try:
        inserted_id = DBOperations.add_feedback_question(question_data)
        return jsonify({
            'message': 'Feedback question added successfully',
            'question': {
                '_id': str(inserted_id),
                'question_text': question_text,
                'question_type': question_type
            }
        }), 201
    except Exception as e:
        return jsonify({'error': f"Failed to add question: {str(e)}"}), 500


@app.route('/api/feedback/questions/<question_id>', methods=['DELETE'])
@app.route('/api/questions/<question_id>', methods=['DELETE'])
def api_delete_question(question_id):
    """Delete feedback question by _id (Admin operation)"""
    if not question_id:
        return jsonify({'error': 'Question ID is required'}), 400
    
    success = delete_feedback_question(question_id)
    if success:
        return jsonify({'message': 'Question deleted successfully'}), 200
    return jsonify({'error': 'Question not found or invalid ID'}), 404


# ==========================================================
# REST API: FEEDBACK SUBMISSION AND RETRIEVAL
# ==========================================================
@app.route('/api/feedback', methods=['POST'])
def api_submit_feedback():
    """
    Submit student feedback response.
    Accepts modern JSON answers array or direct rating/comment payload.
    """
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    # Extract student username (from body or current session)
    student_username = data.get('student_username') or data.get('student_id') or session.get('student')
    if not student_username:
        user = get_current_user()
        if user and user.get('role') == 'student':
            student_username = user.get('username')
            
    if not student_username:
        return jsonify({'error': 'Student username is required'}), 400
    
    course_code = data.get('course_code') or data.get('course_id')
    if not course_code:
        return jsonify({'error': 'Course selection (course_code) is required'}), 400
    
    # Process answers
    answers = data.get('answers')
    rating = data.get('rating')
    comment = data.get('comment') or data.get('comments')
    
    rating_values = []
    
    # If structured answers array provided
    if answers and isinstance(answers, list):
        formatted_answers = []
        for ans in answers:
            q_text = ans.get('question', '').strip()
            q_val = str(ans.get('answer', '')).strip()
            if not q_val:
                continue
            
            # Check if answer is numeric rating
            try:
                numeric_val = float(q_val)
                if 1 <= numeric_val <= 5:
                    rating_values.append(numeric_val)
            except ValueError:
                pass
            
            formatted_answers.append({
                'question': q_text,
                'answer': q_val
            })
            
        if not formatted_answers:
            return jsonify({'error': 'Please provide answers to the feedback questions'}), 400
        
        # If rating was not explicitly set, compute average from rating answers
        if rating is None or rating == '':
            if rating_values:
                rating = round(sum(rating_values) / len(rating_values), 1)
            else:
                rating = 5.0
        else:
            try:
                rating = round(float(rating), 1)
            except ValueError:
                rating = 5.0
                
        feedback_data = {
            'student_username': student_username,
            'course_code': course_code,
            'rating': rating,
            'answers': formatted_answers,
            'submitted_at': datetime.now()
        }
    else:
        # Fallback for simple direct rating & comment payload
        try:
            rating_num = float(rating) if rating is not None else 5.0
        except ValueError:
            rating_num = 5.0
            
        ans_list = []
        if comment:
            ans_list.append({'question': 'Comments', 'answer': comment})
        ans_list.append({'question': 'Overall Rating', 'answer': str(rating_num)})
        
        feedback_data = {
            'student_username': student_username,
            'course_code': course_code,
            'rating': rating_num,
            'comments': comment or '',
            'answers': ans_list,
            'submitted_at': datetime.now()
        }
    
    try:
        db = DatabaseConfig.get_database()
        inserted = db.feedback_responses.insert_one(feedback_data)
        return jsonify({
            'message': 'Feedback submitted successfully',
            'id': str(inserted.inserted_id),
            'rating': feedback_data['rating']
        }), 201
    except Exception as e:
        return jsonify({'error': f"Failed to submit feedback: {str(e)}"}), 500


@app.route('/api/feedback', methods=['GET'])
def api_get_feedback():
    """
    Retrieve feedback submissions with optional filtering:
    - ?course_code=... or ?course_filter=...
    - ?student_username=...
    """
    course_filter = request.args.get('course_code') or request.args.get('course_filter')
    student_filter = request.args.get('student_username')
    
    if student_filter:
        feedbacks = get_student_feedback(student_filter)
        return jsonify(feedbacks), 200
        
    feedbacks = get_all_feedback(course_code_filter=course_filter)
    return jsonify(feedbacks), 200


@app.route('/api/student/feedback', methods=['GET'])
def api_get_student_feedback():
    """Retrieve feedback submitted by student"""
    student_username = request.args.get('student_username') or session.get('student')
    if not student_username:
        user = get_current_user()
        if user and user.get('role') == 'student':
            student_username = user.get('username')
            
    if not student_username:
        return jsonify({'error': 'Student username is required'}), 400
        
    feedbacks = get_student_feedback(student_username)
    return jsonify(feedbacks), 200


@app.route('/api/faculty/feedback', methods=['GET'])
def api_get_faculty_feedback():
    """Retrieve feedback for faculty member's course"""
    faculty_username = request.args.get('faculty_username') or session.get('faculty')
    if not faculty_username:
        user = get_current_user()
        if user and user.get('role') == 'faculty':
            faculty_username = user.get('username')
            
    if not faculty_username:
        return jsonify({'error': 'Faculty username is required'}), 400
        
    feedbacks = get_faculty_feedback(faculty_username)
    return jsonify(feedbacks), 200


# ==========================================================
# REST API: REPORTS (REPLACES SOAP getFacultyReport)
# ==========================================================
@app.route('/api/reports/faculty', methods=['GET'])
def api_faculty_report():
    """
    Faculty feedback report endpoint replacing SOAP getFacultyReport.
    Supports query parameters: ?faculty_id=... or ?course_code=...
    """
    faculty_id = request.args.get('faculty_id') or request.args.get('faculty_username')
    course_code = request.args.get('course_code')
    
    if not faculty_id and not course_code:
        # Check current logged-in faculty
        if 'faculty' in session:
            faculty_id = session['faculty']
        else:
            user = get_current_user()
            if user and user.get('role') == 'faculty':
                faculty_id = user.get('username')
    
    report_data = DBOperations.get_faculty_report_details(
        faculty_username=faculty_id,
        course_code=course_code
    )
    
    # Build formatted text summary report
    target_id = faculty_id or course_code or 'All'
    text_report = f"Feedback Report for Faculty: {target_id}\n"
    text_report += "=" * 50 + "\n"
    if not report_data['feedbacks']:
        text_report += "No feedback available\n"
    else:
        for fb in report_data['feedbacks']:
            text_report += f"Student: {fb.get('student_username', 'N/A')}\n"
            text_report += f"Course: {fb.get('course_code', 'N/A')}\n"
            text_report += f"Rating: {fb.get('rating', 'N/A')}/5\n"
            comment = fb.get('comments')
            if not comment and fb.get('answers'):
                for ans in fb.get('answers'):
                    if 'rating' not in ans.get('question', '').lower():
                        comment = ans.get('answer')
                        break
            text_report += f"Comments: {comment or 'N/A'}\n"
            text_report += f"Date: {fb.get('submitted_at', 'N/A')}\n"
            text_report += "-" * 50 + "\n"
            
    report_data['formatted_report_text'] = text_report
    report_data['soap_compatible_text'] = text_report
    return jsonify(report_data), 200


# ==========================================================
# REST API: ADMIN ENTITY MANAGEMENT & STATS
# ==========================================================
@app.route('/api/admin/stats', methods=['GET'])
def api_admin_stats():
    """Summary metrics for admin dashboard"""
    stats = DBOperations.get_admin_stats()
    return jsonify(stats), 200


@app.route('/api/faculty', methods=['GET'])
def api_get_faculty():
    """List all faculty members"""
    faculty_list = DBOperations.get_all_faculty()
    return jsonify(faculty_list), 200


@app.route('/api/faculty', methods=['POST'])
def api_add_faculty():
    """Add a new faculty member (Admin operation)"""
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    name = data.get('faculty_name', '').strip() or data.get('name', '').strip()
    course_code = data.get('course_code', '').strip().upper()
    course_name = data.get('course_name', '').strip()
    email = data.get('faculty_email', '').strip()
    department = data.get('department', '').strip()
    
    if not username or not password or not name:
        return jsonify({'error': 'Username, password, and faculty name are required'}), 400
    
    faculty_data = {
        'username': username,
        'password': password,
        'name': name,
        'faculty_name': name,
        'course_code': course_code,
        'course_name': course_name,
        'faculty_email': email,
        'department': department
    }
    
    try:
        DBOperations.add_faculty(faculty_data)
        return jsonify({
            'message': f"Faculty member '{name}' added successfully",
            'username': username
        }), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 409
    except Exception as e:
        return jsonify({'error': f"Failed to add faculty: {str(e)}"}), 500


@app.route('/api/students', methods=['GET'])
def api_get_students():
    """List all students (Admin operation)"""
    students_list = DBOperations.get_all_students()
    return jsonify(students_list), 200


@app.route('/api/students', methods=['POST'])
def api_add_student():
    """Add a new student (Admin operation)"""
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    name = data.get('student_name', '').strip() or data.get('name', '').strip()
    email = data.get('student_email', '').strip()
    roll_number = data.get('roll_number', '').strip()
    
    if not username or not password or not name:
        return jsonify({'error': 'Username, password, and name are required'}), 400
    
    student_data = {
        'username': username,
        'password': password,
        'name': name,
        'student_name': name,
        'student_email': email,
        'roll_number': roll_number
    }
    
    try:
        DBOperations.add_student(student_data)
        return jsonify({
            'message': f"Student '{name}' added successfully",
            'username': username
        }), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 409
    except Exception as e:
        return jsonify({'error': f"Failed to add student: {str(e)}"}), 500


# ==========================================================
# ERROR HANDLERS (RETURN JSON)
# ==========================================================
@app.errorhandler(400)
def handle_bad_request(e):
    return jsonify({'error': 'Bad Request', 'message': str(e)}), 400

@app.errorhandler(401)
def handle_unauthorized(e):
    return jsonify({'error': 'Unauthorized', 'message': str(e)}), 401

@app.errorhandler(404)
def handle_not_found(e):
    # If API route, return JSON; otherwise fallback
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found', 'path': request.path}), 404
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def handle_internal_error(e):
    return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500


# ==========================================================
# ==========================================================
# FRONTEND SERVING
# ==========================================================
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React frontend build or fallback to template"""
    dist_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')
    if os.path.exists(dist_dir):
        file_path = os.path.join(dist_dir, path)
        if path != "" and os.path.exists(file_path):
            return send_from_directory(dist_dir, path)
        else:
            return send_from_directory(dist_dir, 'index.html')
    # Fallback to legacy index.html
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
