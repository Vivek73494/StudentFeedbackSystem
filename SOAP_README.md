# SOAP Web Service Documentation

## SOAP Endpoint
- **URL**: `http://localhost:5000/soap`
- **WSDL**: `http://localhost:5000/soap?wsdl`

## SOAP Methods

### 1. submitFeedback
Submit student feedback to the system.

**Parameters:**
- `student_id` (string): Student username
- `course_id` (string): Course code
- `rating` (integer): Rating from 1-5
- `comment` (string): Feedback comment

**Returns:** Success/Error message

### 2. getFacultyReport
Get feedback report for faculty.

**Parameters:**
- `faculty_id` (string): Faculty username

**Returns:** Formatted feedback report

### 3. addCourse
Add a new course to the system.

**Parameters:**
- `course_name` (string): Name of the course
- `course_code` (string): Course code

**Returns:** Success/Error message

### 4. addQuestion
Add a feedback question.

**Parameters:**
- `question_text` (string): Question text
- `question_type` (string): Type (rating/text)

**Returns:** Success/Error message

## Testing SOAP Service

### Using Python (zeep library):
```bash
pip install zeep
python soap_client_test.py
```

### Using SoapUI:
1. Create new SOAP project
2. Enter WSDL URL: `http://localhost:5000/soap?wsdl`
3. Test methods with sample data

### Using curl:
```bash
curl -X POST http://localhost:5000/soap \
  -H "Content-Type: text/xml" \
  -d '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
          <submitFeedback>
            <student_id>student1</student_id>
            <course_id>CS101</course_id>
            <rating>5</rating>
            <comment>Great course!</comment>
          </submitFeedback>
        </soap:Body>
      </soap:Envelope>'
```

## MongoDB Integration
All SOAP methods are connected to MongoDB through `db_operations.py`:
- Feedback stored in `feedback_responses` collection
- Courses stored in `courses` collection
- Questions stored in `feedback_questions` collection
