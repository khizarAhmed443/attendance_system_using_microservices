# Attendance Management System

A microservices-based attendance management system built with Python Flask.

## Services

1. Student Service (Port 5001)
   - Manages student information
   - Handles student registration and updates

2. Lecture Service (Port 5002)
   - Manages lecture information
   - Handles lecture scheduling and updates

3. Attendance Service (Port 5003)
   - Manages attendance records
   - Handles attendance marking and reporting

4. Class Service (Port 5004)
   - Manages class information
   - Handles class creation and updates

## Setup

1. Clone the repository
2. Install dependencies for each service:
   ```bash
   cd <service_directory>
   pip install -r requirements.txt
   ```

3. Run each service:
   ```bash
   cd <service_directory>
   python app.py
   ```

4. Access the frontend by opening `frontend/index.html` in your browser

## API Endpoints

### Student Service
- GET /api/students - Get all students
- GET /api/students/<roll_number> - Get student by roll number
- POST /api/students - Add new student
- PUT /api/students/<roll_number> - Update student

### Lecture Service
- GET /api/lectures - Get all lectures
- GET /api/lectures/<id> - Get lecture by ID
- POST /api/lectures - Add new lecture
- PUT /api/lectures/<id> - Update lecture

### Attendance Service
- GET /api/attendance - Get all attendance records
- POST /api/attendance - Mark attendance
- GET /api/attendance/report - Generate attendance report

### Class Service
- GET /api/classes - Get all classes
- GET /api/classes/<id> - Get class by ID
- POST /api/classes - Add new class
- PUT /api/classes/<id> - Update class

## Technologies Used

- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript
- Database: SQLite
- Deployment: Render 