import os
import sys
import unittest
from bson.objectid import ObjectId

from app import app
from database_config import DatabaseConfig
from db_operations import DBOperations

class TestSystemMigration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.db = DatabaseConfig.get_database()
        print("\n=======================================================")
        print("RUNNING COMPREHENSIVE SYSTEM MIGRATION VERIFICATION")
        print("=======================================================")

    def test_01_mongodb_connection(self):
        """1. Verify MongoDB connection and existing data collections"""
        collections = self.db.list_collection_names()
        self.assertIn('students', collections)
        self.assertIn('faculty', collections)
        self.assertIn('courses', collections)
        self.assertIn('feedback_questions', collections)
        self.assertIn('feedback_responses', collections)
        
        students_count = self.db.students.count_documents({})
        faculty_count = self.db.faculty.count_documents({})
        courses_count = self.db.courses.count_documents({})
        self.assertGreaterEqual(students_count, 60, "Students should be preserved")
        self.assertGreaterEqual(faculty_count, 7, "Faculty should be preserved")
        self.assertGreaterEqual(courses_count, 7, "Courses should be preserved")
        print(f"[PASS] test_01_mongodb_connection: {students_count} students, {faculty_count} faculty, {courses_count} courses preserved")

    def test_02_auth_endpoints(self):
        """2. Verify Student, Faculty, and Admin logins"""
        # Student login
        res = self.client.post('/api/auth/login', json={'username': 'student1', 'password': 'vvv123', 'role': 'student'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['user']['role'], 'student')
        
        # Faculty login
        res = self.client.post('/api/auth/login', json={'username': 'faculty1', 'password': 'vvv123', 'role': 'faculty'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['user']['role'], 'faculty')
        self.assertEqual(res.get_json()['user']['course_code'], 'AWT103')
        
        # Admin login
        res = self.client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin123', 'role': 'admin'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['user']['role'], 'admin')

        # Invalid login
        res = self.client.post('/api/auth/login', json={'username': 'admin', 'password': 'wrongpassword', 'role': 'admin'})
        self.assertEqual(res.status_code, 401)
        print("[PASS] test_02_auth_endpoints PASSED: Student, Faculty, Admin, and rejection of invalid credentials working")

    def test_03_courses_crud(self):
        """3. Verify Course retrieval, creation, and deletion"""
        # GET courses
        res = self.client.get('/api/courses')
        self.assertEqual(res.status_code, 200)
        courses = res.get_json()
        self.assertIsInstance(courses, list)
        self.assertGreater(len(courses), 0)

        # POST add test course
        test_code = "TEST999"
        # Cleanup first if already exists
        self.db.courses.delete_many({'course_code': test_code})
        
        res = self.client.post('/api/courses', json={'course_name': 'Test Migration Course', 'course_code': test_code})
        self.assertEqual(res.status_code, 201)
        
        # Verify in DB
        found = self.db.courses.find_one({'course_code': test_code})
        self.assertIsNotNone(found)
        
        # DELETE test course
        res = self.client.delete(f'/api/courses/{test_code}')
        self.assertEqual(res.status_code, 200)
        found_after = self.db.courses.find_one({'course_code': test_code})
        self.assertIsNone(found_after)
        print("[PASS] test_03_courses_crud PASSED: Course retrieval, creation, and deletion working")

    def test_04_questions_crud(self):
        """4. Verify Feedback Questions retrieval, creation, and deletion"""
        res = self.client.get('/api/feedback/questions')
        self.assertEqual(res.status_code, 200)
        questions = res.get_json()
        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0)

        # POST add question
        res = self.client.post('/api/feedback/questions', json={
            'question_text': 'Was the course pace appropriate?',
            'question_type': 'rating'
        })
        self.assertEqual(res.status_code, 201)
        q_id = res.get_json()['question']['_id']
        
        # DELETE question
        res = self.client.delete(f'/api/feedback/questions/{q_id}')
        self.assertEqual(res.status_code, 200)
        print("[PASS] test_04_questions_crud PASSED: Question retrieval, creation, and deletion working")

    def test_05_feedback_submission_and_retrieval(self):
        """5. Verify Feedback submission and student/faculty retrieval"""
        test_student = "student2"
        test_course = "SET101"
        
        payload = {
            'student_username': test_student,
            'course_code': test_course,
            'answers': [
                {'question': 'How would you rate the course?', 'answer': '5'},
                {'question': 'How clear were the explanations given by the teacher.', 'answer': '5'},
                {'question': 'Comments', 'answer': 'Outstanding pedagogy and classroom interaction'}
            ]
        }
        res = self.client.post('/api/feedback', json=payload)
        self.assertEqual(res.status_code, 201)
        inserted_id = res.get_json().get('id')
        self.assertIsNotNone(inserted_id)

        # Student feedback retrieval
        res = self.client.get(f'/api/student/feedback?student_username={test_student}')
        self.assertEqual(res.status_code, 200)
        s_feedbacks = res.get_json()
        self.assertTrue(any(fb['course_code'] == test_course for fb in s_feedbacks))

        # Faculty feedback retrieval
        res = self.client.get('/api/faculty/feedback?faculty_username=faculty3')
        self.assertEqual(res.status_code, 200)
        f_feedbacks = res.get_json()
        self.assertTrue(any(fb['course_code'] == test_course for fb in f_feedbacks))
        print("[PASS] test_05_feedback_submission_and_retrieval PASSED: Feedback submitted and retrieved for student & faculty")

    def test_06_faculty_report(self):
        """6. Verify Faculty Report API endpoint"""
        res = self.client.get('/api/reports/faculty?faculty_id=faculty1')
        self.assertEqual(res.status_code, 200)
        report = res.get_json()
        self.assertIn('total_responses', report)
        self.assertIn('average_rating', report)
        self.assertIn('rating_distribution', report)
        self.assertIn('formatted_report_text', report)
        self.assertIn("Feedback Report for Faculty: faculty1", report['formatted_report_text'])
        print(f"[PASS] test_06_faculty_report PASSED: avg_rating={report['average_rating']}, total_responses={report['total_responses']}")

    def test_07_admin_stats(self):
        """7. Verify Admin Statistics API"""
        res = self.client.get('/api/admin/stats')
        self.assertEqual(res.status_code, 200)
        stats = res.get_json()
        self.assertIn('total_students', stats)
        self.assertIn('total_faculty', stats)
        self.assertIn('total_courses', stats)
        self.assertIn('total_questions', stats)
        self.assertIn('total_feedbacks', stats)
        self.assertIn('average_rating', stats)
        print(f"[PASS] test_07_admin_stats PASSED: stats={stats}")

    def test_08_react_frontend_serving(self):
        """8. Verify Flask serves React build from frontend/dist"""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'<div id="root"></div>', res.data)
        self.assertIn(b'Online Student Feedback System', res.data)
        print("[PASS] test_08_react_frontend_serving PASSED: React frontend successfully served by Flask")

    def test_09_no_legacy_service_dependencies(self):
        """9. Verify no legacy service modules required by app.py"""
        with open('app.py', 'r', encoding='utf-8') as f:
            app_code = f.read()
        self.assertNotIn('spyne', app_code.lower())
        self.assertNotIn('zeep', app_code.lower())
        self.assertFalse(os.path.exists('soap_service.py'), "soap_service.py should be removed")
        self.assertFalse(os.path.exists('soap_client_test.py'), "soap_client_test.py should be removed")
        print("[PASS] test_09_no_legacy_service_dependencies PASSED: Legacy dependencies completely eliminated")

if __name__ == '__main__':
    unittest.main()
