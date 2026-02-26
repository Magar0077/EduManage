import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Professional Secret Key for Lincoln College
app.config['SECRET_KEY'] = 'lincoln_college_final_master_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///college.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELS ---

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    instructor = db.Column(db.String(100))
    year = db.Column(db.Integer, default=1) # Supports years 1-4
    description = db.Column(db.Text)
    modules = db.relationship('Module', backref='course', lazy=True, cascade="all, delete-orphan")

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    # Changed to 'course_rel' or 'course' to avoid conflicts with backrefs
    course = db.relationship('Course', backref='course_enrollments')



@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- PUBLIC ROUTES ---

@app.route('/')
def index():
    year_filter = request.args.get('year', type=int)
    courses = Course.query.filter_by(year=year_filter).all() if year_filter else Course.query.all()
    return render_template('index.html', courses=courses, current_year=year_filter)

@app.route('/course/<int:course_id>')
def course_view(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_view.html', course=course)

# --- NEW ENROLLMENT ROUTE ---

@app.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):
    # Check if course exists
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    
    if existing_enrollment:
        flash(f"You are already enrolled in {course.title}.", "info")
    else:
        new_enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
        db.session.add(new_enrollment)
        db.session.commit()
        flash(f"Successfully enrolled in {course.title}!", "success")
    
    return redirect(url_for('dashboard'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash(f"Thank you {request.form.get('name')}. Lincoln Admissions will contact you soon!", "success")
        return redirect(url_for('index'))
    return render_template('contact.html')

# --- AUTH ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        role = 'admin' if User.query.count() == 0 else 'student'
        new_user = User(username=request.form['username'], email=request.form['email'], password=hashed_pw, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Welcome to Lincoln College!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials.", "danger")
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Pass 'user' to the template to match your current dashboard.html
    return render_template('dashboard.html', user=current_user)

# --- ADMIN ROUTES ---

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin.html', courses=Course.query.all())

@app.route('/admin/add', methods=['POST'])
@login_required
def add_course():
    if current_user.role == 'admin':
        new_c = Course(
            title=request.form['title'], 
            code=request.form['code'],
            instructor=request.form['instructor'], 
            year=int(request.form['year']),
            description=request.form['description']
        )
        db.session.add(new_c)
        db.session.commit()
        flash("Course added to catalog.", "success")
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit/<int:id>', methods=['POST'])
@login_required
def edit_course(id):
    if current_user.role == 'admin':
        course = Course.query.get_or_404(id)
        course.title = request.form['title']
        course.code = request.form['code']
        course.instructor = request.form['instructor']
        course.year = int(request.form['year'])
        course.description = request.form['description']
        db.session.commit()
        flash("Lincoln Catalog Updated.", "info")
    return redirect(url_for('admin_panel'))

@app.route('/admin/add_module/<int:course_id>', methods=['POST'])
@login_required
def add_module(course_id):
    if current_user.role == 'admin':
        new_m = Module(title=request.form['module_title'], course_id=course_id)
        db.session.add(new_m)
        db.session.commit()
        flash("Chapter added to curriculum.", "success")
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete/<int:id>')
@login_required
def delete_course(id):
    if current_user.role == 'admin':
        course = Course.query.get_or_404(id)
        db.session.delete(course)
        db.session.commit()
        flash("Course removed from catalog.", "warning")
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)