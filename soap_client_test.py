# SOAP Client Test Script
from zeep import Client

# SOAP endpoint URL
SOAP_URL = 'http://localhost:5000/soap?wsdl'

def test_soap_service():
    """Test SOAP web service methods"""
    
    # Create SOAP client
    client = Client(SOAP_URL)
    
    print("Testing SOAP Web Service")
    print("=" * 50)
    
    # Test 1: Add Course
    print("\n1. Testing addCourse...")
    result = client.service.addCourse('Web Development', 'CS201')
    print(f"Result: {result}")
    
    # Test 2: Add Question
    print("\n2. Testing addQuestion...")
    result = client.service.addQuestion('How was the teaching quality?', 'rating')
    print(f"Result: {result}")
    
    # Test 3: Submit Feedback
    print("\n3. Testing submitFeedback...")
    result = client.service.submitFeedback('student1', 'CS101', 5, 'Excellent course!')
    print(f"Result: {result}")
    
    # Test 4: Get Faculty Report
    print("\n4. Testing getFacultyReport...")
    result = client.service.getFacultyReport('faculty1')
    print(f"Result:\n{result}")
    
    print("\n" + "=" * 50)
    print("SOAP Service Testing Complete!")

if __name__ == '__main__':
    test_soap_service()
