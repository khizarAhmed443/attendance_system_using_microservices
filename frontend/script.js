// Use the URLs from config.js
const STUDENT_API = `${API_CONFIG.STUDENT_SERVICE}/api/students`;
const LECTURE_API = `${API_CONFIG.LECTURE_SERVICE}/api/lectures`;
const ATTENDANCE_API = `${API_CONFIG.ATTENDANCE_SERVICE}/api/attendance`;

// Utility functions
function showError(message) {
    console.error('Error:', message);
    alert('Error: ' + message);
}

function showSuccess(message) {
    console.log('Success:', message);
    alert('Success: ' + message);
}

// Load all attendance records when the page loads
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('user.html')) {
        showAllAttendance();
    }
});

// Show all attendance records
async function showAllAttendance() {
    try {
        const response = await fetch(ATTENDANCE_API);
        if (!response.ok) {
            throw new Error('Failed to fetch attendance records');
        }
        const data = await response.json();
        displayAttendanceRecords(data);
    } catch (error) {
        showError(error.message);
    }
}

// Search attendance by roll number
async function searchAttendance() {
    const rollNumber = document.getElementById('searchRollNumber').value.trim();
    if (!rollNumber) {
        showAllAttendance();
        return;
    }

    try {
        const response = await fetch(`${ATTENDANCE_API}/student/${rollNumber}`);
        if (!response.ok) {
            throw new Error('Failed to fetch attendance records');
        }
        const data = await response.json();
        displayAttendanceRecords(data);
    } catch (error) {
        showError(error.message);
    }
}

// Sort attendance records
function sortAttendance() {
    const sortOrder = document.getElementById('sortOrder').value;
    const tbody = document.getElementById('attendanceTableBody');
    const rows = Array.from(tbody.getElementsByTagName('tr'));

    rows.sort((a, b) => {
        const dateA = new Date(a.getAttribute('data-date') + 'T' + a.getAttribute('data-time'));
        const dateB = new Date(b.getAttribute('data-date') + 'T' + b.getAttribute('data-time'));
        return sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
    });

    rows.forEach(row => tbody.appendChild(row));
}

// Filter attendance records by status
function filterAttendance() {
    const statusFilter = document.getElementById('statusFilter').value;
    const rows = document.getElementById('attendanceTableBody').getElementsByTagName('tr');

    Array.from(rows).forEach(row => {
        const status = row.getAttribute('data-status');
        row.style.display = statusFilter === 'all' || status === statusFilter ? '' : 'none';
    });
}

// Display attendance records in the table
function displayAttendanceRecords(records) {
    const tbody = document.getElementById('attendanceTableBody');
    tbody.innerHTML = '';

    records.forEach(record => {
        const row = document.createElement('tr');
        row.setAttribute('data-date', record.date);
        row.setAttribute('data-time', record.time);
        row.setAttribute('data-status', record.status);

        row.innerHTML = `
            <td>${record.date}</td>
            <td>${record.time}</td>
            <td>${record.subject}</td>
            <td>${record.roll_number}</td>
            <td>${record.student_name}</td>
            <td class="status-${record.status}">${record.status}</td>
        `;

        tbody.appendChild(row);
    });
}

// Admin panel functions
if (window.location.pathname.includes('admin.html')) {
    // Load lectures for attendance marking
    async function loadLectures() {
        try {
            const response = await fetch(LECTURE_API);
            if (!response.ok) {
                throw new Error('Failed to fetch lectures');
            }
            const lectures = await response.json();
            const select = document.getElementById('lectureSelect');
            select.innerHTML = '<option value="">Select Lecture</option>';
            lectures.forEach(lecture => {
                select.innerHTML += `
                    <option value="${lecture.id}">
                        ${lecture.date} ${lecture.time} - ${lecture.subject}
                    </option>
                `;
            });
            // Populate report filter for lectures
            populateReportFilter('lecture', lectures);
        } catch (error) {
            showError(error.message);
        }
    }

    // Load students for attendance marking
    async function loadStudents() {
        try {
            const response = await fetch(STUDENT_API);
            if (!response.ok) {
                throw new Error('Failed to fetch students');
            }
            const students = await response.json();
            const studentList = document.getElementById('studentList');
            studentList.innerHTML = '';
            students.forEach(student => {
                studentList.innerHTML += `
                    <div class="student-item">
                        <input type="checkbox" id="student_${student.roll_number}" 
                               value="${student.roll_number}" name="students">
                        <label for="student_${student.roll_number}">
                            ${student.name} (${student.roll_number})
                        </label>
                    </div>
                `;
            });
            // Populate report filter for students
            populateReportFilter('student', students);
        } catch (error) {
            showError(error.message);
        }
    }

    // Populate report filter based on type
    function populateReportFilter(type, data) {
        const filterSelect = document.getElementById('reportFilter');
        const filterLabel = document.getElementById('reportFilterLabel');
        
        // Update the label text based on type
        filterLabel.textContent = type === 'lecture' ? 'Select Lecture:' : 'Select Student:';
        
        filterSelect.innerHTML = '<option value="">Select ' + (type === 'lecture' ? 'Lecture' : 'Student') + '</option>';
        
        if (type === 'lecture') {
            data.forEach(lecture => {
                filterSelect.innerHTML += `
                    <option value="${lecture.id}">
                        ${lecture.date} ${lecture.time} - ${lecture.subject}
                    </option>
                `;
            });
        } else {
            data.forEach(student => {
                filterSelect.innerHTML += `
                    <option value="${student.roll_number}">
                        ${student.name} (${student.roll_number})
                    </option>
                `;
            });
        }
    }

    // Handle report type change
    document.getElementById('reportType').addEventListener('change', async function(e) {
        const type = e.target.value;
        try {
            if (type === 'lecture') {
                const response = await fetch(LECTURE_API);
                if (!response.ok) throw new Error('Failed to fetch lectures');
                const lectures = await response.json();
                populateReportFilter('lecture', lectures);
            } else {
                const response = await fetch(STUDENT_API);
                if (!response.ok) throw new Error('Failed to fetch students');
                const students = await response.json();
                populateReportFilter('student', students);
            }
        } catch (error) {
            showError(error.message);
        }
    });

    // Generate attendance report
    window.generateReport = async function generateReport() {
        const type = document.getElementById('reportType').value;
        const filter = document.getElementById('reportFilter').value;
        const resultDiv = document.getElementById('reportResult');

        if (!filter) {
            showError('Please select a ' + (type === 'lecture' ? 'lecture' : 'student'));
            return;
        }

        try {
            let url = ATTENDANCE_API;
            if (type === 'lecture') {
                url += `/lecture/${filter}`;
            } else {
                url += `/student/${filter}`;
            }

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Failed to fetch attendance report');
            }

            const records = await response.json();
            
            // Create report table
            let html = `
                <table class="attendance-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Subject</th>
                            <th>Roll Number</th>
                            <th>Student Name</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            records.forEach(record => {
                html += `
                    <tr>
                        <td>${record.date}</td>
                        <td>${record.time}</td>
                        <td>${record.subject}</td>
                        <td>${record.roll_number}</td>
                        <td>${record.student_name}</td>
                        <td class="status-${record.status}">${record.status}</td>
                    </tr>
                `;
            });

            html += `
                    </tbody>
                </table>
            `;

            resultDiv.innerHTML = html;
        } catch (error) {
            showError(error.message);
        }
    }

    // Handle lecture form submission
    document.getElementById('lectureForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = {
            date: document.getElementById('lectureDate').value,
            time: document.getElementById('lectureTime').value,
            subject: document.getElementById('lectureSubject').value
        };

        try {
            const response = await fetch(LECTURE_API, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to create lecture');
            }

            showSuccess('Lecture created successfully');
            this.reset();
            loadLectures();
        } catch (error) {
            showError(error.message);
        }
    });

    // Handle student form submission
    document.getElementById('studentForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = {
            roll_number: document.getElementById('rollNumber').value,
            name: document.getElementById('studentName').value,
            class_name: document.getElementById('className').value,
            email: document.getElementById('studentEmail').value,
            phone: document.getElementById('studentPhone').value,
            address: document.getElementById('studentAddress').value
        };

        try {
            const response = await fetch(STUDENT_API, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to add student');
            }

            showSuccess('Student added successfully');
            this.reset();
            loadStudents();
        } catch (error) {
            showError(error.message);
        }
    });

    // Handle attendance form submission
    document.getElementById('attendanceForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const lectureId = document.getElementById('lectureSelect').value;
        const selectedStudents = Array.from(document.querySelectorAll('input[name="students"]:checked'))
            .map(checkbox => checkbox.value);

        if (!lectureId || selectedStudents.length === 0) {
            showError('Please select a lecture and at least one student');
            return;
        }

        try {
            console.log('Marking attendance for lecture:', lectureId);
            console.log('Selected students:', selectedStudents);

            // First, mark all selected students as present
            const attendancePromises = selectedStudents.map(rollNumber => {
                const data = {
                    lecture_id: parseInt(lectureId),
                    roll_number: rollNumber,
                    status: 'present'
                };
                console.log('Sending attendance data:', data);
                
                return fetch(ATTENDANCE_API, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                }).then(async response => {
                    if (!response.ok) {
                        const errorData = await response.json();
                        console.error('Attendance API Error:', {
                            status: response.status,
                            statusText: response.statusText,
                            error: errorData
                        });
                        throw new Error(errorData.error || 'Failed to mark attendance');
                    }
                    return response;
                });
            });

            // Then, mark all unselected students as absent
            const allStudents = Array.from(document.querySelectorAll('input[name="students"]'))
                .map(checkbox => checkbox.value);
            const unselectedStudents = allStudents.filter(roll => !selectedStudents.includes(roll));
            
            console.log('Unselected students:', unselectedStudents);
            
            const absentPromises = unselectedStudents.map(rollNumber => {
                const data = {
                    lecture_id: parseInt(lectureId),
                    roll_number: rollNumber,
                    status: 'absent'
                };
                console.log('Sending absence data:', data);
                
                return fetch(ATTENDANCE_API, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                }).then(async response => {
                    if (!response.ok) {
                        const errorData = await response.json();
                        console.error('Attendance API Error:', {
                            status: response.status,
                            statusText: response.statusText,
                            error: errorData
                        });
                        throw new Error(errorData.error || 'Failed to mark absence');
                    }
                    return response;
                });
            });

            // Wait for all requests to complete
            const results = await Promise.all([...attendancePromises, ...absentPromises]);
            console.log('All attendance records processed successfully');
            
            showSuccess('Attendance marked successfully');
            this.reset();
        } catch (error) {
            console.error('Attendance Error:', {
                message: error.message,
                stack: error.stack
            });
            showError(error.message);
        }
    });

    // Load initial data
    loadLectures();
    loadStudents();
} 