# Lincoln College - Course Management System
A professional, responsive Student Portal and Course Catalog built with Flask and SQLAlchemy.

## Project Overview
This platform serves as a digital bridge between Lincoln College students and the academic curriculum. It allows for dynamic course discovery based on academic year levels and provides a secure enrollment system.

### Key Features
* **User Authentication:** Secure Login/Register with password hashing.
* **Role-Based Access:** Automatic Admin assignment for the first registered user.
* **Year-Based Filtering:** View courses specifically for Year 1, 2, 3, or 4.
* **Student Dashboard:** Track enrolled courses in a personalized portal.
* **Admin CRUD:** Full control over adding, editing, and deleting courses/modules.
* **Responsive Design:** Optimized for Desktop, Tablet, and Mobile.

## Tech Stack
* **Backend:** Python / Flask
* **Database:** SQLite / Flask-SQLAlchemy
* **Frontend:** HTML5, CSS3 (Bootstrap 5), Jinja2
* **Auth:** Flask-Login / Werkzeug

## Project Structure
```text
├── app.py              # Main Application & Routes
├── college.db          # SQLite Database
├── static/
│   ├── css/            # Custom Styles
│   └── js/             # UI Interactivity
└── templates/          # Jinja2 HTML Templates
