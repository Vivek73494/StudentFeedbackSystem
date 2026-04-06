# Main Flask Application
from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_operations import DBOperations, initialize_default_users, get_all_feedback_questions, get_student_feedback, get_faculty_feedback, delete_feedback_question, get_all_feedback
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Initialize default users on startup
initialize_default_users()

# Import SOAP service after Flask app initialization
try:
    from soap_service import wsgi_app
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/soap': wsgi_app
    })
    print("SOAP service integrated successfully at /soap endpoint")
except Exception as e:
    print(f"Warning: SOAP service not available - {e}")

# HOME ROUTE
@app.route('/')
def home():
    """Home page with module selection"""
    return render_template('index.html')

# STUDENT LOGIN
@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    """Student login page and handler"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if DBOperations.validate_student(username, password):
            session['student'] = username
            flash('Student login successful!', 'success')
            return redirect('/student/dashboard')
        else:
            flash('Invalid student login', 'error')
    
    return render_template('student_login.html')

# STUDENT DASHBOARD
@app.route('/student/dashboard')
def student_dashboard():
    """Student dashboard"""
    if 'student' not in session:
        return redirect('/student/login')
    
    student = session['student']
    courses = DBOperations.get_all_courses()
    questions = get_all_feedback_questions()
    feedbacks = get_student_feedback(student)
    
    return render_template('student_dashboard.html', student=student, courses=courses, questions=questions, feedbacks=feedbacks)

# FACULTY LOGIN
@app.route('/faculty/login', methods=['GET', 'POST'])
def faculty_login():
    """Faculty login page and handler"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if DBOperations.validate_faculty(username, password):
            session['faculty'] = username
            flash('Faculty login successful!', 'success')
            return redirect('/faculty/dashboard')
        else:
            flash('Invalid faculty login', 'error')
    
    return render_template('faculty_login.html')

# FACULTY DASHBOARD
@app.route('/faculty/dashboard')
def faculty_dashboard():
    """Faculty dashboard"""
    if 'faculty' not in session:
        return redirect('/faculty/login')
    
    faculty_username = session['faculty']
    
    # Get faculty details
    from database_config import DatabaseConfig
    faculty_collection = DatabaseConfig.get_collection('faculty')
    feedback_collection = DatabaseConfig.get_collection('feedback_responses')
    
    faculty = faculty_collection.find_one({"username": faculty_username})
    
    if not faculty:
        flash('Faculty not found', 'error')
        return redirect('/faculty/login')
    
    # Get course_code from faculty
    course_code = faculty.get("course_code")
    
    # Get feedback filtered by course_code
    feedback = list(feedback_collection.find({"course_code": course_code}).sort('submitted_at', -1))
    
    return render_template('faculty_dashboard.html', feedback=feedback, faculty=faculty)

# ADMIN LOGIN
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page and handler"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if DBOperations.validate_admin(username, password):
            session['admin'] = username
            flash('Admin login successful!', 'success')
            return redirect('/admin/dashboard')
        else:
            flash('Invalid admin login', 'error')
    
    return render_template('admin_login.html')

# ADMIN DASHBOARD
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    """Admin dashboard with feedback filtering"""
    if 'admin' not in session:
        return redirect('/admin/login')
    
    questions = get_all_feedback_questions()
    courses = DBOperations.get_all_courses()
    
    # Get filter parameter
    selected_course = request.args.get('course_filter', '')
    
    # Get feedback based on filter
    if selected_course and selected_course != 'all':
        all_feedback = get_all_feedback(course_code_filter=selected_course)
    else:
        all_feedback = get_all_feedback()
    
    return render_template('admin_dashboard.html', 
                         questions=questions, 
                         all_feedback=all_feedback,
                         courses=courses,
                         selected_course=selected_course)

# FORM SUBMISSION ROUTES
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    """Submit student feedback"""
    if 'student' not in session:
        return redirect('/student/login')
    
    student = session['student']
    course_code = request.form.get('course_code')
    questions = get_all_feedback_questions()
    
    # Validate course selection
    if not course_code:
        flash('Please select a course', 'error')
        return redirect('/student/dashboard')
    
    # Collect all answers and rating values
    answers = []
    rating_values = []
    
    for i, question in enumerate(questions):
        answer = request.form.get(f"answer_{i+1}")
        if answer:
            question_text = question.get("question_text", question.get("question", ""))
            
            # Check if this is a rating question
            if question.get("question_type") == 'rating':
                rating_values.append(float(answer))
            
            answers.append({
                "question": question_text,
                "answer": answer
            })
    
    # Validate that we have answers and at least one rating
    if not answers or not rating_values:
        flash('Please answer all questions', 'error')
        return redirect('/student/dashboard')
    
    # Calculate average rating with one decimal place
    average_rating = round(sum(rating_values) / len(rating_values), 1)
    
    # Save feedback with proper structure
    feedback_data = {
        "student_username": student,
        "course_code": course_code,
        "rating": average_rating,
        "answers": answers,
        "submitted_at": datetime.now()
    }
    
    from database_config import DatabaseConfig
    collection = DatabaseConfig.get_collection('feedback_responses')
    collection.insert_one(feedback_data)
    
    flash('Feedback submitted successfully!', 'success')
    return redirect('/student/dashboard')

@app.route('/add_course', methods=['POST'])
def add_course():
    """Add new course"""
    if 'admin' not in session:
        return redirect('/admin/login')
    course_data = {
        'course_name': request.form.get('course_name'),
        'course_code': request.form.get('course_code')
    }
    DBOperations.add_course(course_data)
    flash('Course added successfully!', 'success')
    return redirect('/admin/dashboard')

@app.route('/add_faculty', methods=['POST'])
def add_faculty_route():
    """Add new faculty"""
    if 'admin' not in session:
        return redirect('/admin/login')
    faculty_data = {
        'username': request.form.get('username'),
        'password': request.form.get('password'),
        'faculty_name': request.form.get('faculty_name'),
        'faculty_email': request.form.get('faculty_email'),
        'department': request.form.get('department')
    }
    DBOperations.add_faculty(faculty_data)
    flash('Faculty added successfully!', 'success')
    return redirect('/admin/dashboard')

@app.route('/add_student', methods=['POST'])
def add_student():
    """Add new student"""
    if 'admin' not in session:
        return redirect('/admin/login')
    student_data = {
        'username': request.form.get('username'),
        'password': request.form.get('password'),
        'student_name': request.form.get('student_name'),
        'student_email': request.form.get('student_email'),
        'roll_number': request.form.get('roll_number')
    }
    DBOperations.add_student(student_data)
    flash('Student added successfully!', 'success')
    return redirect('/admin/dashboard')

@app.route('/add_question', methods=['POST'])
def add_question():
    """Add feedback question"""
    if 'admin' not in session:
        return redirect('/admin/login')
    question_data = {
        'question_text': request.form.get('question_text'),
        'question_type': request.form.get('question_type')
    }
    DBOperations.add_feedback_question(question_data)
    flash('Feedback question added successfully!', 'success')
    return redirect('/admin/dashboard')

@app.route('/admin/delete_question/<question_id>', methods=['POST'])
def delete_question(question_id):
    """Delete feedback question"""
    if 'admin' not in session:
        return redirect('/admin/login')
    
    success = delete_feedback_question(question_id)
    
    if success:
        flash('Question deleted successfully!', 'success')
    else:
        flash('Question deletion failed!', 'error')
    
    return redirect('/admin/dashboard')

# LOGOUT ROUTE
@app.route('/logout')
def logout():
    """Logout handler"""
    session.clear()
    return redirect('/')

# DATABASE INITIALIZATION
@app.route('/init_db')
def init_db():
    """Initialize database with sample data"""
    DBOperations.add_admin({'username': 'admin', 'password': 'admin123', 'name': 'Admin User'})
    DBOperations.add_student({'username': 'student1', 'password': 'student123', 'student_name': 'John Doe', 'student_email': 'john@example.com', 'roll_number': 'S001'})
    DBOperations.add_faculty({'username': 'faculty1', 'password': 'faculty123', 'faculty_name': 'Dr. Smith', 'faculty_email': 'smith@example.com', 'department': 'Computer Science'})
    DBOperations.add_course({'course_name': 'Data Structures', 'course_code': 'CS101'})
    DBOperations.add_feedback_question({'question_text': 'How would you rate the course?', 'question_type': 'rating'})
    return 'Database initialized with sample data!'

if __name__ == '__main__':
    app.run(debug=True)
