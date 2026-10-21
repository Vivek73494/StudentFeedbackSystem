# MongoDB Operations
from database_config import DatabaseConfig
from datetime import datetime
from bson.objectid import ObjectId

def serialize_doc(doc):
    """Recursively convert ObjectId and datetime objects to JSON-serializable types"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        result = {}
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                result[k] = str(v)
            elif isinstance(v, datetime):
                result[k] = v.isoformat()
            elif isinstance(v, (dict, list)):
                result[k] = serialize_doc(v)
            else:
                result[k] = v
        return result
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime):
        return doc.isoformat()
    return doc

class DBOperations:
    
    @staticmethod
    def add_student(student_data):
        """Add new student to database"""
        collection = DatabaseConfig.get_collection('students')
        existing = collection.find_one({'username': student_data.get('username')})
        if existing:
            raise ValueError(f"Student with username '{student_data.get('username')}' already exists")
        return collection.insert_one(student_data).inserted_id
    
    @staticmethod
    def add_faculty(faculty_data):
        """Add new faculty to database"""
        collection = DatabaseConfig.get_collection('faculty')
        existing = collection.find_one({'username': faculty_data.get('username')})
        if existing:
            raise ValueError(f"Faculty with username '{faculty_data.get('username')}' already exists")
        return collection.insert_one(faculty_data).inserted_id
    
    @staticmethod
    def add_admin(admin_data):
        """Add new admin to database"""
        collection = DatabaseConfig.get_collection('admins')
        existing = collection.find_one({'username': admin_data.get('username')})
        if existing:
            raise ValueError(f"Admin with username '{admin_data.get('username')}' already exists")
        return collection.insert_one(admin_data).inserted_id
    
    @staticmethod
    def add_course(course_data):
        """Add new course to database"""
        collection = DatabaseConfig.get_collection('courses')
        existing = collection.find_one({'course_code': course_data.get('course_code')})
        if existing:
            raise ValueError(f"Course with code '{course_data.get('course_code')}' already exists")
        return collection.insert_one(course_data).inserted_id
    
    @staticmethod
    def delete_course(course_code):
        """Delete course from database by course_code"""
        collection = DatabaseConfig.get_collection('courses')
        result = collection.delete_one({'course_code': course_code})
        return result.deleted_count > 0
    
    @staticmethod
    def add_feedback_question(question_data):
        """Add feedback question to database"""
        collection = DatabaseConfig.get_collection('feedback_questions')
        return collection.insert_one(question_data).inserted_id
    
    @staticmethod
    def submit_feedback(feedback_data):
        """Submit feedback response"""
        if 'submitted_at' not in feedback_data or not feedback_data['submitted_at']:
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
        """Get all faculty members without password"""
        collection = DatabaseConfig.get_collection('faculty')
        return serialize_doc(list(collection.find({}, {'password': 0})))
    
    @staticmethod
    def get_all_students():
        """Get all students without password"""
        collection = DatabaseConfig.get_collection('students')
        return serialize_doc(list(collection.find({}, {'password': 0})))
    
    @staticmethod
    def get_feedback_questions():
        """Get all feedback questions"""
        collection = DatabaseConfig.get_collection('feedback_questions')
        return serialize_doc(list(collection.find()))
    
    @staticmethod
    def get_feedback_report(filters=None):
        """Get feedback report with optional filters"""
        collection = DatabaseConfig.get_collection('feedback_responses')
        query = filters if filters else {}
        return serialize_doc(list(collection.find(query).sort('submitted_at', -1)))
    
    @staticmethod
    def validate_student(username, password):
        """Validate student credentials (case-insensitive username, trimmed whitespace)"""
        if not username or not password:
            return False
        import re
        collection = DatabaseConfig.get_collection('students')
        u = str(username).strip()
        p = str(password).strip()
        student = collection.find_one({
            'username': {'$regex': f'^{re.escape(u)}$', '$options': 'i'},
            'password': p
        })
        return student is not None

    @staticmethod
    def find_student_user(username, password):
        """Find student document (case-insensitive username)"""
        if not username or not password:
            return None
        import re
        collection = DatabaseConfig.get_collection('students')
        u = str(username).strip()
        p = str(password).strip()
        student = collection.find_one({
            'username': {'$regex': f'^{re.escape(u)}$', '$options': 'i'},
            'password': p
        }, {'password': 0})
        return serialize_doc(student)
    
    @staticmethod
    def validate_faculty(username, password):
        """Validate faculty credentials (case-insensitive username, trimmed whitespace)"""
        if not username or not password:
            return False
        import re
        collection = DatabaseConfig.get_collection('faculty')
        u = str(username).strip()
        p = str(password).strip()
        faculty = collection.find_one({
            'username': {'$regex': f'^{re.escape(u)}$', '$options': 'i'},
            'password': p
        })
        return faculty is not None

    @staticmethod
    def find_faculty_user(username, password):
        """Find faculty document (case-insensitive username)"""
        if not username or not password:
            return None
        import re
        collection = DatabaseConfig.get_collection('faculty')
        u = str(username).strip()
        p = str(password).strip()
        faculty = collection.find_one({
            'username': {'$regex': f'^{re.escape(u)}$', '$options': 'i'},
            'password': p
        }, {'password': 0})
        return serialize_doc(faculty)
    
    @staticmethod
    def validate_admin(username, password):
        """Validate admin credentials (case-insensitive username, trimmed whitespace)"""
        if not username or not password:
            return False
        import re
        collection = DatabaseConfig.get_collection('admins')
        u = str(username).strip()
        p = str(password).strip()
        admin = collection.find_one({
            'username': {'$regex': f'^{re.escape(u)}$', '$options': 'i'},
            'password': p
        })
        return admin is not None

    @staticmethod
    def find_admin_user(username, password):
        """Find admin document (case-insensitive username)"""
        if not username or not password:
            return None
        import re
        collection = DatabaseConfig.get_collection('admins')
        u = str(username).strip()
        p = str(password).strip()
        admin = collection.find_one({
            'username': {'$regex': f'^{re.escape(u)}$', '$options': 'i'},
            'password': p
        }, {'password': 0})
        return serialize_doc(admin)
    
    @staticmethod
    def verify_user(username, password, user_type):
        """Verify user credentials (legacy method)"""
        collection_name = 'faculty' if user_type == 'faculty' else (user_type + 's')
        collection = DatabaseConfig.get_collection(collection_name)
        user = collection.find_one({'username': username, 'password': password})
        return user is not None
    
    @staticmethod
    def get_user(username, user_type):
        """Get user details"""
        collection_name = 'faculty' if user_type == 'faculty' else (user_type + 's')
        collection = DatabaseConfig.get_collection(collection_name)
        user = collection.find_one({'username': username}, {'_id': 0, 'password': 0})
        return serialize_doc(user)

    @staticmethod
    def get_admin_stats():
        """Get summary statistics for admin dashboard"""
        db = DatabaseConfig.get_database()
        student_count = db.students.count_documents({})
        faculty_count = db.faculty.count_documents({})
        course_count = db.courses.count_documents({})
        question_count = db.feedback_questions.count_documents({})
        feedback_count = db.feedback_responses.count_documents({})
        
        # Calculate overall average rating
        feedbacks = list(db.feedback_responses.find({}, {'rating': 1}))
        ratings = []
        for fb in feedbacks:
            r = fb.get('rating')
            if r is not None:
                try:
                    ratings.append(float(r))
                except (ValueError, TypeError):
                    pass
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0

        return {
            "total_students": student_count,
            "total_faculty": faculty_count,
            "total_courses": course_count,
            "total_questions": question_count,
            "total_feedbacks": feedback_count,
            "average_rating": avg_rating
        }

    @staticmethod
    def get_faculty_report_details(faculty_username=None, course_code=None):
        """Generate comprehensive faculty feedback report replacing SOAP getFacultyReport"""
        db = DatabaseConfig.get_database()
        faculty_coll = db.faculty
        courses_coll = db.courses
        feedback_coll = db.feedback_responses

        faculty_info = None
        target_course_code = course_code

        if faculty_username:
            faculty_info = faculty_coll.find_one({'username': faculty_username}, {'_id': 0, 'password': 0})
            if faculty_info and not target_course_code:
                target_course_code = faculty_info.get('course_code')

        query = {}
        if target_course_code:
            query['course_code'] = target_course_code
        elif faculty_username:
            # If faculty found no course_code
            return {
                "faculty": faculty_info,
                "course": None,
                "total_responses": 0,
                "average_rating": 0.0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "feedbacks": []
            }

        course_info = None
        if target_course_code:
            course_info = courses_coll.find_one({'course_code': target_course_code}, {'_id': 0})
            if not faculty_info:
                faculty_info = faculty_coll.find_one({'course_code': target_course_code}, {'_id': 0, 'password': 0})

        feedbacks = list(feedback_coll.find(query).sort('submitted_at', -1))
        
        ratings = []
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for fb in feedbacks:
            r = fb.get('rating')
            if r is not None:
                try:
                    val = float(r)
                    ratings.append(val)
                    rounded_star = min(5, max(1, int(round(val))))
                    rating_distribution[rounded_star] += 1
                except (ValueError, TypeError):
                    pass

        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0

        return {
            "faculty": serialize_doc(faculty_info),
            "course": serialize_doc(course_info),
            "course_code": target_course_code,
            "total_responses": len(feedbacks),
            "average_rating": avg_rating,
            "rating_distribution": rating_distribution,
            "feedbacks": serialize_doc(feedbacks)
        }

def initialize_default_users():
    """Initialize default admin, faculty, and student users if they don't exist"""
    admin_collection = DatabaseConfig.get_collection('admins')
    faculty_collection = DatabaseConfig.get_collection('faculty')
    student_collection = DatabaseConfig.get_collection('students')
    courses_collection = DatabaseConfig.get_collection('courses')
    questions_collection = DatabaseConfig.get_collection('feedback_questions')
    
    # ADMIN
    if admin_collection.find_one({"username": "admin"}) is None:
        admin_collection.insert_one({
            "username": "admin",
            "password": "admin123",
            "name": "System Administrator",
            "role": "admin"
        })
        print("Default admin user created")
    
    # FACULTY LIST - Only insert default faculty if none exist
    if faculty_collection.count_documents({}) == 0:
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
    
    # STUDENT LIST (60 students) - Only insert if missing
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

def get_all_feedback_questions():
    """Get all feedback questions from database"""
    collection = DatabaseConfig.get_collection('feedback_questions')
    return serialize_doc(list(collection.find()))

def get_student_feedback(student):
    """Get feedback submitted by specific student"""
    collection = DatabaseConfig.get_collection('feedback_responses')
    courses_collection = DatabaseConfig.get_collection('courses')
    faculty_collection = DatabaseConfig.get_collection('faculty')
    
    feedbacks = list(collection.find({"student_username": student}).sort('submitted_at', -1))
    
    courses = {course['course_code']: course['course_name'] for course in courses_collection.find()}
    faculty_map = {faculty['course_code']: faculty['name'] for faculty in faculty_collection.find()}
    
    for feedback in feedbacks:
        course_code = feedback.get('course_code', 'N/A')
        feedback['course_name'] = courses.get(course_code, 'Unknown')
        feedback['faculty_name'] = faculty_map.get(course_code, 'N/A')
        
    return serialize_doc(feedbacks)

def get_faculty_feedback(faculty_username):
    """Get feedback for specific faculty course"""
    faculty_collection = DatabaseConfig.get_collection('faculty')
    feedback_collection = DatabaseConfig.get_collection('feedback_responses')
    courses_collection = DatabaseConfig.get_collection('courses')
    
    faculty = faculty_collection.find_one({"username": faculty_username})
    if not faculty or "course_code" not in faculty:
        return []
    
    course_code = faculty["course_code"]
    courses = {course['course_code']: course['course_name'] for course in courses_collection.find()}
    
    feedbacks = list(feedback_collection.find({"course_code": course_code}).sort('submitted_at', -1))
    for fb in feedbacks:
        fb['course_name'] = courses.get(course_code, faculty.get('course_name', 'Unknown'))
        fb['faculty_name'] = faculty.get('name', 'N/A')
        
    return serialize_doc(feedbacks)

def save_feedback(feedback_list):
    """Save multiple feedback responses to database"""
    collection = DatabaseConfig.get_collection('feedback_responses')
    for feedback in feedback_list:
        if 'submitted_at' not in feedback:
            feedback['submitted_at'] = datetime.now()
        collection.insert_one(feedback)

def delete_feedback_question(question_id):
    """Delete feedback question from database using _id"""
    collection = DatabaseConfig.get_collection('feedback_questions')
    try:
        result = collection.delete_one({"_id": ObjectId(question_id)})
        return result.deleted_count > 0
    except Exception:
        return False

def get_all_feedback(course_code_filter=None):
    """Get all feedback submissions from database with optional course filter"""
    feedback_collection = DatabaseConfig.get_collection('feedback_responses')
    courses_collection = DatabaseConfig.get_collection('courses')
    faculty_collection = DatabaseConfig.get_collection('faculty')
    
    query = {}
    if course_code_filter and course_code_filter != 'all':
        query['course_code'] = course_code_filter
    
    all_feedback = list(feedback_collection.find(query).sort('submitted_at', -1))
    
    courses = {course['course_code']: course['course_name'] for course in courses_collection.find()}
    faculty_map = {faculty['course_code']: faculty['name'] for faculty in faculty_collection.find()}
    
    for feedback in all_feedback:
        course_code = feedback.get('course_code', 'N/A')
        feedback['course_name'] = courses.get(course_code, 'Unknown')
        feedback['faculty_name'] = faculty_map.get(course_code, 'N/A')
    
    return serialize_doc(all_feedback)
