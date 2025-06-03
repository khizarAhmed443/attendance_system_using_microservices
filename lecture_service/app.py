from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["https://strong-medovik-58a65d.netlify.app", "http://localhost:3000"]}})

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lectures.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Lecture Model
class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, nullable=False)  # Added class_id field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
            'date': self.date,
            'time': self.time,
            'subject': self.subject,
            'class_id': self.class_id,
            'class_name': class_name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# Create tables
with app.app_context():
    db.drop_all()  # Drop existing tables
    db.create_all()  # Create new tables with updated schema
    print("Database initialized at:", os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lectures.db'))

@app.route('/api/lectures', methods=['GET'])
def get_lectures():
    lectures = Lecture.query.all()
    return jsonify([lecture.to_dict() for lecture in lectures])

@app.route('/api/lectures', methods=['POST'])
def create_lecture():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['date', 'time', 'subject', 'class_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    lecture = Lecture(
        date=data['date'],
        time=data['time'],
        subject=data['subject'],
        class_id=data['class_id']
    )
    
    db.session.add(lecture)
    db.session.commit()
    
    return jsonify(lecture.to_dict()), 201

@app.route('/api/lectures/<int:lecture_id>', methods=['GET'])
def get_lecture(lecture_id):
    lecture = Lecture.query.get_or_404(lecture_id)
    return jsonify(lecture.to_dict())

@app.route('/api/lectures/<int:lecture_id>', methods=['PUT'])
def update_lecture(lecture_id):
    lecture = Lecture.query.get_or_404(lecture_id)
    data = request.get_json()
    
    if 'date' in data:
        lecture.date = data['date']
    if 'time' in data:
        lecture.time = data['time']
    if 'subject' in data:
        lecture.subject = data['subject']
    if 'class_id' in data:
        lecture.class_id = data['class_id']
    
    db.session.commit()
    return jsonify(lecture.to_dict())

@app.route('/api/lectures/<int:lecture_id>', methods=['DELETE'])
def delete_lecture(lecture_id):
    lecture = Lecture.query.get_or_404(lecture_id)
    db.session.delete(lecture)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(port=5002, debug=True) 