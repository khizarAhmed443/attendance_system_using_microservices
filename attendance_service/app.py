from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS to allow all methods
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://comfy-lokum-190901.netlify.app", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Service URLs
STUDENT_SERVICE_URL = os.getenv('STUDENT_SERVICE_URL', 'https://student-service-8gyd.onrender.com')
LECTURE_SERVICE_URL = os.getenv('LECTURE_SERVICE_URL', 'https://lecture-service.onrender.com')
CLASS_SERVICE_URL = os.getenv('CLASS_SERVICE_URL', 'https://class-service-kacm.onrender.com')

db = SQLAlchemy(app)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, nullable=False)
    roll_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        # Fetch lecture details
        lecture_details = {}
        try:
            resp = requests.get(f'{LECTURE_SERVICE_URL}/api/lectures/{self.lecture_id}')
            if resp.status_code == 200:
                lecture_details = resp.json()
        except Exception:
            pass

        # Fetch student details
        student_details = {}
        try:
            resp = requests.get(f'{STUDENT_SERVICE_URL}/api/students/{self.roll_number}')
            if resp.status_code == 200:
                student_details = resp.json()
        except Exception:
            pass

        # Fetch class details
        class_name = ''
        if lecture_details and 'class_id' in lecture_details:
            try:
                resp = requests.get(f'{CLASS_SERVICE_URL}/api/classes/{lecture_details["class_id"]}')
                if resp.status_code == 200:
                    class_name = resp.json().get('name', '')
            except Exception:
                pass

        return {
            'id': self.id,
            'lecture_id': self.lecture_id,
            'roll_number': self.roll_number,
            'status': self.status,
            'date': lecture_details.get('date', ''),
            'time': lecture_details.get('time', ''),
            'subject': lecture_details.get('subject', ''),
            'class_name': class_name,
            'student_name': student_details.get('name', ''),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# Create tables
with app.app_context():
    db.create_all()
    print("Database initialized at:", os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attendance.db'))

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    # Get query parameters
    class_id = request.args.get('class_id')
    subject = request.args.get('subject')
    roll_number = request.args.get('roll_number')

    # Start with all records
    query = Attendance.query

    # Apply filters if provided
    if class_id or subject:
        # Get lecture IDs that match the filters
        lecture_ids = []
        try:
            lecture_url = f'{LECTURE_SERVICE_URL}/api/lectures'
            if class_id:
                lecture_url += f'?class_id={class_id}'
            resp = requests.get(lecture_url)
            if resp.status_code == 200:
                lectures = resp.json()
                if subject:
                    lectures = [l for l in lectures if l['subject'] == subject]
                lecture_ids = [l['id'] for l in lectures]
        except Exception as e:
            print(f"Error fetching lectures: {str(e)}")
            return jsonify([])

        if lecture_ids:
            query = query.filter(Attendance.lecture_id.in_(lecture_ids))
        else:
            return jsonify([])

    if roll_number:
        query = query.filter(Attendance.roll_number == roll_number)

    # Get filtered records
    records = query.all()
    print(f"Found {len(records)} attendance records")  # Debug print
    
    # Convert records to dictionary and print for debugging
    records_dict = [record.to_dict() for record in records]
    print(f"Records: {records_dict}")  # Debug print
    
    return jsonify(records_dict)

@app.route('/api/attendance', methods=['POST'])
def create_attendance():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['lecture_id', 'roll_number', 'status']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if student exists
    try:
        resp = requests.get(f'{STUDENT_SERVICE_URL}/api/students/{data["roll_number"]}')
        if resp.status_code != 200:
            return jsonify({'error': 'Student not found'}), 404
    except Exception:
        return jsonify({'error': 'Error verifying student'}), 500
    
    # Check if lecture exists
    try:
        resp = requests.get(f'{LECTURE_SERVICE_URL}/api/lectures/{data["lecture_id"]}')
        if resp.status_code != 200:
            return jsonify({'error': 'Lecture not found'}), 404
    except Exception:
        return jsonify({'error': 'Error verifying lecture'}), 500
    
    # Check if attendance record already exists
    existing_record = Attendance.query.filter_by(
        lecture_id=data['lecture_id'],
        roll_number=data['roll_number']
    ).first()
    
    if existing_record:
        # Update existing record
        existing_record.status = data['status']
        existing_record.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(existing_record.to_dict())
    
    # Create new record
    attendance = Attendance(
        lecture_id=data['lecture_id'],
        roll_number=data['roll_number'],
        status=data['status']
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    return jsonify(attendance.to_dict()), 201

@app.route('/api/attendance/<int:id>', methods=['DELETE'])
def delete_attendance(id):
    try:
        record = Attendance.query.get(id)
        if not record:
            return jsonify({'error': 'Attendance record not found'}), 404
        
        db.session.delete(record)
        db.session.commit()
        return jsonify({'message': 'Attendance record deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5003))
    app.run(host='0.0.0.0', port=port) 