# SOAP Web Service using Spyne
from spyne import Application, rpc, ServiceBase, Unicode, Integer
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from db_operations import DBOperations
import sys
import logging

# Configure logging for Spyne
logging.basicConfig(level=logging.INFO)

class FeedbackSOAPService(ServiceBase):
    """SOAP Service for Student Feedback System"""
    
    @rpc(Unicode, Unicode, Integer, Unicode, _returns=Unicode)
    def submitFeedback(ctx, student_id, course_id, rating, comment):
        """Submit student feedback via SOAP"""
        try:
            feedback_data = {
                'student_username': student_id,
                'course_code': course_id,
                'rating': rating,
                'comments': comment
            }
            DBOperations.submit_feedback(feedback_data)
            return "Feedback submitted successfully"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @rpc(Unicode, _returns=Unicode)
    def getFacultyReport(ctx, faculty_id):
        """Get feedback report for faculty"""
        try:
            feedbacks = DBOperations.get_feedback_report()
            if not feedbacks:
                return "No feedback available"
            
            report = f"Feedback Report for Faculty: {faculty_id}\n"
            report += "=" * 50 + "\n"
            for fb in feedbacks:
                report += f"Student: {fb.get('student_username', 'N/A')}\n"
                report += f"Course: {fb.get('course_code', 'N/A')}\n"
                report += f"Rating: {fb.get('rating', 'N/A')}/5\n"
                report += f"Comments: {fb.get('comments', 'N/A')}\n"
                report += f"Date: {fb.get('submitted_at', 'N/A')}\n"
                report += "-" * 50 + "\n"
            return report
        except Exception as e:
            return f"Error: {str(e)}"
    
    @rpc(Unicode, Unicode, _returns=Unicode)
    def addCourse(ctx, course_name, course_code):
        """Add new course via SOAP"""
        try:
            course_data = {
                'course_name': course_name,
                'course_code': course_code
            }
            DBOperations.add_course(course_data)
            return f"Course '{course_name}' added successfully"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @rpc(Unicode, Unicode, _returns=Unicode)
    def addQuestion(ctx, question_text, question_type):
        """Add feedback question via SOAP"""
        try:
            question_data = {
                'question_text': question_text,
                'question_type': question_type
            }
            DBOperations.add_feedback_question(question_data)
            return f"Question added successfully"
        except Exception as e:
            return f"Error: {str(e)}"

# Create SOAP application with Python 3.12 compatible settings
soap_app = Application(
    [FeedbackSOAPService],
    tns='feedback.soap.service',
    in_protocol=Soap11(validator='soft'),
    out_protocol=Soap11()
)

# Create WSGI application
wsgi_app = WsgiApplication(soap_app)
