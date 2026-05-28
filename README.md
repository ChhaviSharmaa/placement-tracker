# Placement Management System

A web-based Placement Management System built using Flask, MySQL, Bootstrap, and Python. The system helps manage student placement records, track placement status, and maintain student information through an easy-to-use dashboard.

## Features

* User Login Authentication
* Dashboard Analytics
* Add New Students
* View Student Records
* Edit Student Details
* Delete Student Records
* Placement Status Tracking
* Session Management
* Responsive Bootstrap Interface

## Tech Stack

* Python
* Flask
* MySQL
* HTML
* Bootstrap
* Chart.js
* Git & GitHub



## Project Structure

```text
placement-management-system/
│
├── app.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── index.html
│   ├── students.html
│   ├── add_student.html
│   └── edit_student.html
│
├── screenshots/
│   ├── login.png
│   └── add-student.png
│
├── README.md
└── .gitignore
```

## Database Tables

### users

| Column   | Type         |
| -------- | ------------ |
| id       | INT          |
| username | VARCHAR(100) |
| password | VARCHAR(100) |

### students

| Column  | Type         |
| ------- | ------------ |
| id      | INT          |
| name    | VARCHAR(100) |
| branch  | VARCHAR(50)  |
| company | VARCHAR(100) |
| status  | VARCHAR(50)  |

## Installation

### Clone Repository

```bash
git clone https://github.com/ChhaviSharmaa/placement-tracker.git
```

### Install Dependencies

```bash
pip install flask mysql-connector-python
```

### Run Application

```bash
python app.py
```

### Open in Browser

```text
http://127.0.0.1:5000/login
```

## Key Functionalities

* Authentication System
* Student Record Management
* Dashboard Analytics
* Placement Tracking
* CRUD Operations
* MySQL Database Integration

## Future Enhancements

* Search and Filter Students
* Export Data to Excel
* Placement Reports
* Company Management Module
* Cloud Deployment
* Advanced Dashboard Analytics

## Author

**Chhavi Sharma**

GitHub:
https://github.com/ChhaviSharmaa/placement-tracker
# placement-tracker
A web-based Placement Management System with student tracking, authentication, CRUD operations, and dashboard analytics using Flask and MySQL
