from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": ["https://comfy-lokum-190901.netlify.app", "http://localhost:3000"]}})

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Student Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, nullable=False)  # Foreign key to class
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        # Fetch class name from class service
        class_name = ''
        try:
            resp = requests.get(f'https://class-service-kacm.onrender.com/api/classes/{self.class_id}')
            if resp.status_code == 200:
                class_name = resp.json().get('name', '')
        except Exception:
            pass
        return {
            'id': self.id,
            'roll_number': self.roll_number,
            'name': self.name,
            'class_id': self.class_id,
            'class_name': class_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address
        }

# Create database tables
with app.app_context():
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()
    
    required_fields = ['roll_number', 'name', 'class_id', 'email', 'phone', 'address']
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        student = Student(
            roll_number=data['roll_number'],
            name=data['name'],
            class_id=data['class_id'],
            email=data['email'],
            phone=data['phone'],
            address=data['address']
        )
        db.session.add(student)
        db.session.commit()
        return jsonify(student.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        students = Student.query.all()
        return jsonify([student.to_dict() for student in students])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<roll_number>', methods=['GET'])
def get_student(roll_number):
    student = Student.query.filter_by(roll_number=roll_number).first()
    if student:
        return jsonify(student.to_dict())
    return jsonify({'error': 'Student not found'}), 404

@app.route('/api/students/<roll_number>', methods=['DELETE'])
def delete_student(roll_number):
    student = Student.query.filter_by(roll_number=roll_number).first()
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'message': 'Student deleted successfully'})
    return jsonify({'error': 'Student not found'}), 404

@app.route('/api/students/<roll_number>', methods=['PUT'])
def update_student(roll_number):
    student = Student.query.filter_by(roll_number=roll_number).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.get_json()
    try:
        if 'name' in data:
            student.name = data['name']
        if 'class_id' in data:
            student.class_id = data['class_id']
        if 'email' in data:
            student.email = data['email']
        if 'phone' in data:
            student.phone = data['phone']
        if 'address' in data:
            student.address = data['address']
        
        db.session.commit()
        return jsonify(student.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5001, debug=True) 