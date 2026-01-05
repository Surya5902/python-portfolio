"""
Student Management System - Single File Build

Features
1. Student CRUD with inline edit/delete actions
2. Course CRUD with flexible description and credit tracking
3. Enrollment management that links students to courses and tracks marks
4. Auto-provisioning of templates and SQL schema on startup
5. Built-in database bootstrap that creates required tables if missing

Setup Steps
1. Install dependencies: pip install flask mysql-connector-python
2. Ensure MySQL is running and note the root password
3. Update DB_PASSWORD below to match your local credentials
4. Run python student_management_full.py
5. Open http://127.0.0.1:5000 in a browser
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from flask import Flask, render_template, request
import mysql.connector

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
SCHEMA_FILE = BASE_DIR / "setup_database.sql"

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = "student_management"

FEATURES_TEXT = """\
Key Features\n- CRUD for students, courses, enrollments\n- Auto-creation of templates & SQL schema\n- Database bootstrap with safe retries\n- Responsive HTML dashboards\n- Simple instructions printed on server start\n"""

SETUP_TEXT = """\
Setup Recap\n1. pip install flask mysql-connector-python\n2. Start MySQL and ensure credentials above are valid\n3. Run: python student_management_full.py\n4. Visit: http://127.0.0.1:5000\n"""

INDEX_HTML = """<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Student Management System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .header { background-color: #333; color: white; padding: 20px; text-align: center; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .menu { display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; }
        .menu a { background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; transition: background-color 0.3s; }
        .menu a:hover { background-color: #0056b3; }
        .welcome { text-align: center; padding: 50px 20px; }
        .welcome h1 { color: #333; margin-bottom: 20px; }
        .welcome p { color: #666; font-size: 18px; }
    </style>
</head>
<body>
    <div class=\"header\">
        <h1>Student Management System</h1>
    </div>

    <div class=\"container\">
        <div class=\"menu\">
            <a href=\"/students\">Manage Students</a>
            <a href=\"/courses\">Manage Courses</a>
            <a href=\"/enrollments\">Manage Enrollments</a>
        </div>

        <div class=\"welcome\">
            <h1>Welcome to Student Management System</h1>
            <p>Use the menu above to manage students, courses, and enrollments.</p>
        </div>
    </div>
</body>
</html>
"""

STUDENTS_HTML = """<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Manage Students</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .header { background-color: #333; color: white; padding: 20px; text-align: center; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .form-section { background-color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-row { display: flex; gap: 20px; margin-bottom: 15px; }
        .form-group { flex: 1; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .form-actions { text-align: center; margin-top: 20px; }
        .btn { background-color: #007bff; color: white; padding: 10px 30px; border: none; border-radius: 4px; cursor: pointer; margin: 0 10px; }
        .btn:hover { background-color: #0056b3; }
        .btn-secondary { background-color: #6c757d; }
        .btn-secondary:hover { background-color: #545b62; }
        .btn-danger { background-color: #dc3545; }
        .btn-danger:hover { background-color: #c82333; }
        .table-section { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: bold; }
        tr:hover { background-color: #f5f5f5; }
        .actions { white-space: nowrap; }
        .actions button { margin-right: 5px; padding: 5px 10px; border: none; border-radius: 3px; cursor: pointer; }
        .edit-btn { background-color: #ffc107; color: #212529; }
        .delete-btn { background-color: #dc3545; color: white; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #007bff; text-decoration: none; }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class=\"header\">
        <h1>Manage Students</h1>
    </div>

    <div class=\"container\">
        <a href=\"/\" class=\"back-link\">← Back to Dashboard</a>

        <div class=\"form-section\">
            <h2>Add/Edit Student</h2>
            <form method=\"POST\">
                <input type=\"hidden\" name=\"student_id\" id=\"student_id\">
                <div class=\"form-row\">
                    <div class=\"form-group\">
                        <label for=\"name\">Name:</label>
                        <input type=\"text\" name=\"name\" id=\"name\" required>
                    </div>
                    <div class=\"form-group\">
                        <label for=\"age\">Age:</label>
                        <input type=\"number\" name=\"age\" id=\"age\">
                    </div>
                    <div class=\"form-group\">
                        <label for=\"gender\">Gender:</label>
                        <select name=\"gender\" id=\"gender\" required>
                            <option value=\"\">Select Gender</option>
                            <option value=\"Male\">Male</option>
                            <option value=\"Female\">Female</option>
                            <option value=\"Other\">Other</option>
                        </select>
                    </div>
                </div>
                <div class=\"form-row\">
                    <div class=\"form-group\">
                        <label for=\"department\">Department:</label>
                        <input type=\"text\" name=\"department\" id=\"department\">
                    </div>
                    <div class=\"form-group\">
                        <label for=\"email\">Email:</label>
                        <input type=\"email\" name=\"email\" id=\"email\">
                    </div>
                    <div class=\"form-group\">
                        <label for=\"phone\">Phone:</label>
                        <input type=\"text\" name=\"phone\" id=\"phone\">
                    </div>
                </div>
                <div class=\"form-actions\">
                    <button type=\"submit\" name=\"action\" value=\"Add\" class=\"btn\">Add Student</button>
                    <button type=\"submit\" name=\"action\" value=\"Update\" class=\"btn btn-secondary\" style=\"display:none;\" id=\"update-btn\">Update Student</button>
                    <button type=\"button\" class=\"btn btn-danger\" onclick=\"clearForm()\">Clear</button>
                </div>
            </form>
        </div>

        <div class=\"table-section\">
            <h2>Students List</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Age</th>
                        <th>Gender</th>
                        <th>Department</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td>{{ student.student_id }}</td>
                        <td>{{ student.name }}</td>
                        <td>{{ student.age }}</td>
                        <td>{{ student.gender }}</td>
                        <td>{{ student.department }}</td>
                        <td>{{ student.email }}</td>
                        <td>{{ student.phone }}</td>
                        <td class=\"actions\">
                            <button class=\"edit-btn\" onclick=\"editStudent({{ student.student_id }}, '{{ student.name }}', {{ student.age }}, '{{ student.gender }}', '{{ student.department }}', '{{ student.email }}', '{{ student.phone }}')\">Edit</button>
                            <button class=\"delete-btn\" onclick=\"deleteStudent({{ student.student_id }})\">Delete</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function clearForm() {
            document.getElementById('student_id').value = '';
            document.getElementById('name').value = '';
            document.getElementById('age').value = '';
            document.getElementById('gender').value = '';
            document.getElementById('department').value = '';
            document.getElementById('email').value = '';
            document.getElementById('phone').value = '';
            document.getElementById('update-btn').style.display = 'none';
        }

        function editStudent(id, name, age, gender, department, email, phone) {
            document.getElementById('student_id').value = id;
            document.getElementById('name').value = name;
            document.getElementById('age').value = age;
            document.getElementById('gender').value = gender;
            document.getElementById('department').value = department;
            document.getElementById('email').value = email;
            document.getElementById('phone').value = phone;
            document.getElementById('update-btn').style.display = 'inline-block';
            window.scrollTo(0, 0);
        }

        function deleteStudent(id) {
            if (confirm('Are you sure you want to delete this student?')) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.innerHTML = `
                    <input type="hidden" name="action" value="Delete">
                    <input type="hidden" name="student_id" value="${id}">
                `;
                document.body.appendChild(form);
                form.submit();
            }
        }
    </script>
</body>
</html>
"""

COURSES_HTML = """<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Manage Courses</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .header { background-color: #333; color: white; padding: 20px; text-align: center; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .form-section { background-color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-row { display: flex; gap: 20px; margin-bottom: 15px; }
        .form-group { flex: 1; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .form-group textarea { height: 100px; resize: vertical; }
        .form-actions { text-align: center; margin-top: 20px; }
        .btn { background-color: #007bff; color: white; padding: 10px 30px; border: none; border-radius: 4px; cursor: pointer; margin: 0 10px; }
        .btn:hover { background-color: #0056b3; }
        .btn-secondary { background-color: #6c757d; }
        .btn-secondary:hover { background-color: #545b62; }
        .btn-danger { background-color: #dc3545; }
        .btn-danger:hover { background-color: #c82333; }
        .table-section { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: bold; }
        tr:hover { background-color: #f5f5f5; }
        .actions { white-space: nowrap; }
        .actions button { margin-right: 5px; padding: 5px 10px; border: none; border-radius: 3px; cursor: pointer; }
        .edit-btn { background-color: #ffc107; color: #212529; }
        .delete-btn { background-color: #dc3545; color: white; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #007bff; text-decoration: none; }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class=\"header\">
        <h1>Manage Courses</h1>
    </div>

    <div class=\"container\">
        <a href=\"/\" class=\"back-link\">← Back to Dashboard</a>

        <div class=\"form-section\">
            <h2>Add/Edit Course</h2>
            <form method=\"POST\">
                <input type=\"hidden\" name=\"course_id\" id=\"course_id\">
                <div class=\"form-row\">
                    <div class=\"form-group\">
                        <label for=\"course_name\">Course Name:</label>
                        <input type=\"text\" name=\"course_name\" id=\"course_name\" required>
                    </div>
                    <div class=\"form-group\">
                        <label for=\"credits\">Credits:</label>
                        <input type=\"number\" name=\"credits\" id=\"credits\" required>
                    </div>
                    <div class=\"form-group\">
                        <label for=\"department\">Department:</label>
                        <input type=\"text\" name=\"department\" id=\"department\">
                    </div>
                </div>
                <div class=\"form-row\">
                    <div class=\"form-group\">
                        <label for=\"description\">Description:</label>
                        <textarea name=\"description\" id=\"description\"></textarea>
                    </div>
                </div>
                <div class=\"form-actions\">
                    <button type=\"submit\" name=\"action\" value=\"Add\" class=\"btn\">Add Course</button>
                    <button type=\"submit\" name=\"action\" value=\"Update\" class=\"btn btn-secondary\" style=\"display:none;\" id=\"update-btn\">Update Course</button>
                    <button type=\"button\" class=\"btn btn-danger\" onclick=\"clearForm()\">Clear</button>
                </div>
            </form>
        </div>

        <div class=\"table-section\">
            <h2>Courses List</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Course Name</th>
                        <th>Credits</th>
                        <th>Department</th>
                        <th>Description</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for course in courses %}
                    <tr>
                        <td>{{ course.course_id }}</td>
                        <td>{{ course.course_name }}</td>
                        <td>{{ course.credits }}</td>
                        <td>{{ course.department }}</td>
                        <td>{{ course.description }}</td>
                        <td class=\"actions\">
                            <button class=\"edit-btn\" onclick=\"editCourse({{ course.course_id }}, '{{ course.course_name }}', {{ course.credits }}, '{{ course.department }}', '{{ course.description }}')\">Edit</button>
                            <button class=\"delete-btn\" onclick=\"deleteCourse({{ course.course_id }})\">Delete</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function clearForm() {
            document.getElementById('course_id').value = '';
            document.getElementById('course_name').value = '';
            document.getElementById('credits').value = '';
            document.getElementById('department').value = '';
            document.getElementById('description').value = '';
            document.getElementById('update-btn').style.display = 'none';
        }

        function editCourse(id, name, credits, department, description) {
            document.getElementById('course_id').value = id;
            document.getElementById('course_name').value = name;
            document.getElementById('credits').value = credits;
            document.getElementById('department').value = department;
            document.getElementById('description').value = description;
            document.getElementById('update-btn').style.display = 'inline-block';
            window.scrollTo(0, 0);
        }

        function deleteCourse(id) {
            if (confirm('Are you sure you want to delete this course?')) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.innerHTML = `
                    <input type="hidden" name="action" value="Delete">
                    <input type="hidden" name="course_id" value="${id}">
                `;
                document.body.appendChild(form);
                form.submit();
            }
        }
    </script>
</body>
</html>
"""

ENROLLMENTS_HTML = """<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Manage Enrollments</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .header { background-color: #333; color: white; padding: 20px; text-align: center; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .form-section { background-color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-row { display: flex; gap: 20px; margin-bottom: 15px; }
        .form-group { flex: 1; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .form-actions { text-align: center; margin-top: 20px; }
        .btn { background-color: #007bff; color: white; padding: 10px 30px; border: none; border-radius: 4px; cursor: pointer; margin: 0 10px; }
        .btn:hover { background-color: #0056b3; }
        .btn-secondary { background-color: #6c757d; }
        .btn-secondary:hover { background-color: #545b62; }
        .btn-danger { background-color: #dc3545; }
        .btn-danger:hover { background-color: #c82333; }
        .table-section { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: bold; }
        tr:hover { background-color: #f5f5f5; }
        .actions { white-space: nowrap; }
        .actions button { margin-right: 5px; padding: 5px 10px; border: none; border-radius: 3px; cursor: pointer; }
        .edit-btn { background-color: #ffc107; color: #212529; }
        .delete-btn { background-color: #dc3545; color: white; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #007bff; text-decoration: none; }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class=\"header\">
        <h1>Manage Enrollments</h1>
    </div>

    <div class=\"container\">
        <a href=\"/\" class=\"back-link\">← Back to Dashboard</a>

        <div class=\"form-section\">
            <h2>Add/Edit Enrollment</h2>
            <form method=\"POST\">
                <input type=\"hidden\" name=\"enroll_id\" id=\"enroll_id\">
                <div class=\"form-row\">
                    <div class=\"form-group\">
                        <label for=\"student_id\">Student:</label>
                        <select name=\"student_id\" id=\"student_id\" required>
                            <option value=\"\">Select Student</option>
                            {% for student in students %}
                            <option value=\"{{ student.student_id }}\">{{ student.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class=\"form-group\">
                        <label for=\"course_id\">Course:</label>
                        <select name=\"course_id\" id=\"course_id\" required>
                            <option value=\"\">Select Course</option>
                            {% for course in courses %}
                            <option value=\"{{ course.course_id }}\">{{ course.course_name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class=\"form-group\">
                        <label for=\"marks\">Marks:</label>
                        <input type=\"number\" name=\"marks\" id=\"marks\" min=\"0\" max=\"100\">
                    </div>
                </div>
                <div class=\"form-actions\">
                    <button type=\"submit\" name=\"action\" value=\"Add\" class=\"btn\">Add Enrollment</button>
                    <button type=\"submit\" name=\"action\" value=\"Update\" class=\"btn btn-secondary\" style=\"display:none;\" id=\"update-btn\">Update Enrollment</button>
                    <button type=\"button\" class=\"btn btn-danger\" onclick=\"clearForm()\">Clear</button>
                </div>
            </form>
        </div>

        <div class=\"table-section\">
            <h2>Enrollments List</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Student Name</th>
                        <th>Course Name</th>
                        <th>Marks</th>
                        <th>Enrolled On</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for enrollment in enrollments %}
                    <tr>
                        <td>{{ enrollment.enroll_id }}</td>
                        <td>{{ enrollment.student_name }}</td>
                        <td>{{ enrollment.course_name }}</td>
                        <td>{{ enrollment.marks }}</td>
                        <td>{{ enrollment.enrolled_on }}
                        </td>
                        <td class=\"actions\">
                            <button class=\"edit-btn\" onclick=\"editEnrollment({{ enrollment.enroll_id }}, '{{ enrollment.marks }}')\">Edit</button>
                            <button class=\"delete-btn\" onclick=\"deleteEnrollment({{ enrollment.enroll_id }})\">Delete</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function clearForm() {
            document.getElementById('enroll_id').value = '';
            document.getElementById('student_id').value = '';
            document.getElementById('course_id').value = '';
            document.getElementById('marks').value = '';
            document.getElementById('update-btn').style.display = 'none';
        }

        function editEnrollment(id, marks) {
            document.getElementById('enroll_id').value = id;
            document.getElementById('marks').value = marks;
            document.getElementById('update-btn').style.display = 'inline-block';
            window.scrollTo(0, 0);
        }

        function deleteEnrollment(id) {
            if (confirm('Are you sure you want to delete this enrollment?')) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.innerHTML = `
                    <input type="hidden" name="action" value="Delete">
                    <input type="hidden" name="enroll_id" value="${id}">
                `;
                document.body.appendChild(form);
                form.submit();
            }
        }
    </script>
</body>
</html>
"""

SQL_SCHEMA = """CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

CREATE TABLE IF NOT EXISTS student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    department VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS course (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    credits INT NOT NULL DEFAULT 0,
    department VARCHAR(100),
    description TEXT
);

CREATE TABLE IF NOT EXISTS enrollment (
    enroll_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    marks INT,
    enrolled_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE
);
"""

def ensure_assets() -> None:
    TEMPLATES_DIR.mkdir(exist_ok=True)
    files: Dict[str, str] = {
        "index.html": INDEX_HTML,
        "students.html": STUDENTS_HTML,
        "courses.html": COURSES_HTML,
        "enrollments.html": ENROLLMENTS_HTML,
    }
    for name, content in files.items():
        target = TEMPLATES_DIR / name
        target.write_text(content, encoding="utf-8")
    SCHEMA_FILE.write_text(SQL_SCHEMA, encoding="utf-8")


def get_connection():
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        auth_plugin="mysql_native_password",
    )
    return conn


def create_database_if_needed() -> None:
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        auth_plugin="mysql_native_password",
    )
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    connection.commit()
    cursor.close()
    connection.close()


def create_tables() -> None:
    create_database_if_needed()
    conn = get_connection()
    cursor = conn.cursor()
    statements = [
        """CREATE TABLE IF NOT EXISTS student (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT,
                gender ENUM('Male', 'Female', 'Other') NOT NULL,
                department VARCHAR(100),
                email VARCHAR(150) UNIQUE,
                phone VARCHAR(20)
            )""",
        """CREATE TABLE IF NOT EXISTS course (
                course_id INT AUTO_INCREMENT PRIMARY KEY,
                course_name VARCHAR(150) NOT NULL,
                credits INT NOT NULL DEFAULT 0,
                department VARCHAR(100),
                description TEXT
            )""",
        """CREATE TABLE IF NOT EXISTS enrollment (
                enroll_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                course_id INT NOT NULL,
                marks INT,
                enrolled_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE
            )""",
    ]
    for stmt in statements:
        cursor.execute(stmt)
    conn.commit()
    cursor.close()
    conn.close()


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/students", methods=["GET", "POST"])
def students():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        action = request.form["action"]
        if action == "Add":
            cursor.execute(
                """
                INSERT INTO student (name, age, gender, department, email, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    request.form["name"],
                    request.form.get("age"),
                    request.form["gender"],
                    request.form.get("department"),
                    request.form.get("email"),
                    request.form.get("phone"),
                ),
            )
        elif action == "Update":
            cursor.execute(
                """
                UPDATE student
                SET name=%s, age=%s, gender=%s, department=%s, email=%s, phone=%s
                WHERE student_id=%s
                """,
                (
                    request.form["name"],
                    request.form.get("age"),
                    request.form["gender"],
                    request.form.get("department"),
                    request.form.get("email"),
                    request.form.get("phone"),
                    request.form["student_id"],
                ),
            )
        elif action == "Delete":
            cursor.execute(
                "DELETE FROM student WHERE student_id=%s",
                (request.form["student_id"],),
            )
        conn.commit()
    cursor.execute("SELECT * FROM student")
    students_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("students.html", students=students_data)


@app.route("/courses", methods=["GET", "POST"])
def courses():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        action = request.form["action"]
        if action == "Add":
            cursor.execute(
                """
                INSERT INTO course (course_name, credits, department, description)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    request.form["course_name"],
                    request.form.get("credits", 0),
                    request.form.get("department"),
                    request.form.get("description"),
                ),
            )
        elif action == "Update":
            cursor.execute(
                """
                UPDATE course
                SET course_name=%s, credits=%s, department=%s, description=%s
                WHERE course_id=%s
                """,
                (
                    request.form["course_name"],
                    request.form.get("credits", 0),
                    request.form.get("department"),
                    request.form.get("description"),
                    request.form["course_id"],
                ),
            )
        elif action == "Delete":
            cursor.execute(
                "DELETE FROM course WHERE course_id=%s",
                (request.form["course_id"],),
            )
        conn.commit()
    cursor.execute("SELECT * FROM course")
    courses_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("courses.html", courses=courses_data)


@app.route("/enrollments", methods=["GET", "POST"])
def enrollments():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM student")
    students_list = cursor.fetchall()
    cursor.execute("SELECT * FROM course")
    courses_list = cursor.fetchall()
    if request.method == "POST":
        action = request.form["action"]
        if action == "Add":
            cursor.execute(
                """
                INSERT INTO enrollment (student_id, course_id, marks, enrolled_on)
                VALUES (%s, %s, %s, NOW())
                """,
                (
                    request.form["student_id"],
                    request.form["course_id"],
                    request.form.get("marks"),
                ),
            )
        elif action == "Update":
            cursor.execute(
                """
                UPDATE enrollment
                SET marks=%s
                WHERE enroll_id=%s
                """,
                (
                    request.form.get("marks"),
                    request.form["enroll_id"],
                ),
            )
        elif action == "Delete":
            cursor.execute(
                "DELETE FROM enrollment WHERE enroll_id=%s",
                (request.form["enroll_id"],),
            )
        conn.commit()
    cursor.execute(
        """
        SELECT e.enroll_id, s.name AS student_name, c.course_name, e.marks, e.enrolled_on
        FROM enrollment e
        JOIN student s ON e.student_id = s.student_id
        JOIN course c ON e.course_id = c.course_id
        """
    )
    enrollments_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template(
        "enrollments.html",
        enrollments=enrollments_data,
        students=students_list,
        courses=courses_list,
    )


def print_summary() -> None:
    banner = "=" * 40
    print(banner)
    print(FEATURES_TEXT)
    print(SETUP_TEXT)
    print("Templates + SQL written to:", TEMPLATES_DIR)
    print("Schema file:", SCHEMA_FILE)
    print(banner)


if __name__ == "__main__":
    ensure_assets()
    create_tables()
    print_summary()
    app.run(debug=True)
