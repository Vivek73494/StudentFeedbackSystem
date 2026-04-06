# MongoDB Operations
from database_config import DatabaseConfig
from datetime import datetime
from bson.objectid import ObjectId

class DBOperations:
    
    @staticmethod
    def add_student(student_data):
        """Add new student to database"""
        collection = DatabaseConfig.get_collection('students')
        return collection.insert_one(student_data).inserted_id
    
    @staticmethod
    def add_faculty(faculty_data):
        """Add new faculty to database"""
        collection = DatabaseConfig.get_collection('faculty')
        return collection.insert_one(faculty_data).inserted_id
    
    @staticmethod
    def add_admin(admin_data):
        """Add new admin to database"""
        collection = DatabaseConfig.get_collection('admins')
        return collection.insert_one(admin_data).inserted_id
    
    @staticmethod
    def add_course(course_data):
        """Add new course to database"""
        collection = DatabaseConfig.get_collection('courses')
        return collection.insert_one(course_data).inserted_id
    
    @staticmethod
    def add_feedback_question(question_data):
        """Add feedback question to database"""
        collection = DatabaseConfig.get_collection('feedback_questions')
        return collection.insert_one(question_data).inserted_id
    
    @staticmethod
    def submit_feedback(feedback_data):
        """Submit feedback response"""
        feedback_data['submitted_at'] = datetime.now()
        collection = DatabaseConfig.get_collection('feedback_responses')
        return collection.insert_one(feedback_data).inserted_id
    
    @staticmethod
    def get_all_courses():
        """Get all courses"""
        collection = DatabaseConfig.get_collection('courses')
        return list(collection.find({}, {'_id': 0}))
    
    @staticmethod
    def get_all_faculty():
        """Get all faculty members"""
        collection = DatabaseConfig.get_collection('faculty')
        return list(collection.find({}, {'_id': 0}))
    
    @staticmethod
    def get_feedback_questions():
        """Get all feedback questions"""
        collection = DatabaseConfig.get_collection('feedback_questions')
        return list(collection.find({}, {'_id': 0}))
    
    @staticmethod
    def get_feedback_report(filters=None):
        """Get feedback report with optional filters"""
        collection = DatabaseConfig.get_collection('feedback_responses')
        query = filters if filters else {}
        return list(collection.find(query, {'_id': 0}).sort('submitted_at', -1))
    
    @staticmethod
    def validate_student(username, password):
        """Validate student credentials"""
        collection = DatabaseConfig.get_collection('students')
        student = collection.find_one({'username': username, 'password': password})
        return student is not None
    
    @staticmethod
    def validate_faculty(username, password):
        """Validate faculty credentials"""
        collection = DatabaseConfig.get_collection('faculty')
        faculty = collection.find_one({'username': username, 'password': password})
        return faculty is not None
    
    @staticmethod
    def validate_admin(username, password):
        """Validate admin credentials"""
        collection = DatabaseConfig.get_collection('admins')
        admin = collection.find_one({'username': username, 'password': password})
        return admin is not None
    
    @staticmethod
    def verify_user(username, password, user_type):
        """Verify user credentials (legacy method)"""
        collection = DatabaseConfig.get_collection(user_type + 's')
        user = collection.find_one({'username': username, 'password': password})
        return user is not None
    
    @staticmethod
    def get_user(username, user_type):
        """Get user details"""
        collection = DatabaseConfig.get_collection(user_type + 's')
        return collection.find_one({'username': username}, {'_id': 0, 'password': 0})

def initialize_default_users():
    """Initialize default admin, faculty, and student users if they don't exist"""
    
    admin_collection = DatabaseConfig.get_collection('admins')
    faculty_collection = DatabaseConfig.get_collection('faculty')
    student_collection = DatabaseConfig.get_collection('students')
    
    # ADMIN
    if admin_collection.find_one({"username": "admin"}) is None:
        admin_collection.insert_one({
            "username": "admin",
            "password": "admin123",
            "name": "System Administrator",
            "role": "admin"
        })
        print("Default admin user created")
    
    # FACULTY LIST - Remove old and add new with standardized course codes
    # Clear existing faculty data
    faculty_collection.delete_many({})
    
    faculty_list = [
        {"username":"faculty1","password":"vvv123","name":"Dr.Mangala Shetty","course_name":"AWT","course_code":"AWT103"},
        {"username":"faculty2","password":"vvv123","name":"Dr.Anantha Murthy","course_name":"JAVA","course_code":"JAVA102"},
        {"username":"faculty3","password":"vvv123","name":"Dr.Spoorthy B Shetty","course_name":"SET","course_code":"SET101"},
        {"username":"faculty4","password":"vvv123","name":"Dr.Surendra Shetty","course_name":"DWDM","course_code":"DWDM104"},
        {"username":"faculty5","password":"vvv123","name":"Ms.Rakshitha P","course_name":"DJANGO","course_code":"DJANGO105"},
        {"username":"faculty6","password":"vvv123","name":"Ms.Ashwini K M","course_name":"RUBY","course_code":"RUBY106"},
        {"username":"faculty7","password":"vvv123","name":"Dr.Rashmi Hegde","course_name":"PCS","course_code":"PCS107"}
    ]
    
    faculty_collection.insert_many(faculty_list)
    print(f"Faculty users initialized: {len(faculty_list)} faculty members")
    
    # STUDENT LIST (60 students)
    student_names = [
        "Vivek","Viola","Yashika","Sinchana","Sowbhagya","Rahul","Amit","Priya","Neha","Arjun",
        "Pooja","Kiran","Sneha","Varun","Riya","Anjali","Nikhil","Shreya","Abhishek","Divya",
        "Harsha","Keerthi","Rohit","Bhavana","Sanjay","Megha","Ajay","Kavya","Manoj","Reshma",
        "Vinay","Aishwarya","Girish","Nandini","Praveen","Swathi","Tejas","Pallavi","Rakesh","Shruti",
        "Karthik","Chaitra","Santosh","Pavitra","Uday","Sahana","Akash","Preethi","Mahesh","Rashmi",
        "Lokesh","Deepika","Ganesh","Sangeetha","Ramesh","Kusuma","Jagadish","Renuka","Prakash","Bhavya"
    ]
    
    for i, name in enumerate(student_names, start=1):
        username = f"student{i}"
        if student_collection.find_one({"username": username}) is None:
            student_collection.insert_one({
                "username": username,
                "password": "vvv123",
                "name": name
            })
    
    print(f"Student users initialized: {len(student_names)} students")

def get_all_feedback_questions():
    """Get all feedback questions from database"""
    collection = DatabaseConfig.get_collection('feedback_questions')
    questions = list(collection.find())
    return questions

def get_student_feedback(student):
    """Get feedback submitted by specific student"""
    collection = DatabaseConfig.get_collection('feedback_responses')
    return list(collection.find({"student_username": student}, {"_id": 0}))

def get_faculty_feedback(faculty_username):
    """Get feedback for specific faculty course"""
    from database_config import DatabaseConfig
    faculty_collection = DatabaseConfig.get_collection('faculty')
    feedback_collection = DatabaseConfig.get_collection('feedback_responses')
    
    # Get faculty details to find their course_code
    faculty = faculty_collection.find_one({"username": faculty_username})
    if not faculty or "course_code" not in faculty:
        return []
    
    course_code = faculty["course_code"]
    
    # Get feedback for this course_code only
    return list(feedback_collection.find({"course_code": course_code}, {"_id": 0}).sort('submitted_at', -1))

def save_feedback(feedback_list):
    """Save multiple feedback responses to database"""
    collection = DatabaseConfig.get_collection('feedback_responses')
    for feedback in feedback_list:
        collection.insert_one(feedback)

def delete_feedback_question(question_id):
    """Delete feedback question from database using _id"""
    collection = DatabaseConfig.get_collection('feedback_questions')
    result = collection.delete_one({"_id": ObjectId(question_id)})
    return result.deleted_count > 0

def get_all_feedback(course_code_filter=None):
    """Get all feedback submissions from database with optional course filter"""
    feedback_collection = DatabaseConfig.get_collection('feedback_responses')
    courses_collection = DatabaseConfig.get_collection('courses')
    faculty_collection = DatabaseConfig.get_collection('faculty')
    
    # Build query based on filter
    query = {}
    if course_code_filter:
        query['course_code'] = course_code_filter
    
    # Get feedback sorted by submission date (newest first)
    all_feedback = list(feedback_collection.find(query).sort('submitted_at', -1))
    
    # Get all courses to map course_code to course_name
    courses = {course['course_code']: course['course_name'] for course in courses_collection.find()}
    
    # Get all faculty to map course_code to faculty_name
    faculty_map = {faculty['course_code']: faculty['name'] for faculty in faculty_collection.find()}
    
    # Enrich feedback with course names and faculty names
    for feedback in all_feedback:
        course_code = feedback.get('course_code', 'N/A')
        feedback['course_name'] = courses.get(course_code, 'Unknown')
        feedback['faculty_name'] = faculty_map.get(course_code, 'N/A')
    
    return all_feedback
