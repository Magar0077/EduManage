from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'heritage_college_2026_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///college.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student') # Roles: admin, student
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    category = db.Column(db.String(50)) # e.g., IT, Business, Arts
    description = db.Column(db.Text)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---
@app.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    courses = Course.query.filter(Course.title.contains(query) | Course.code.contains(query)).all()
    return render_template('index.html', courses=courses, query=query)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Server-side validation
        if User.query.filter_by(username=request.form['username']).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        
        hashed_pw = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        role = 'admin' if User.query.count() == 0 else 'student'
        new_user = User(username=request.form['username'], email=request.form['email'], password=hashed_pw, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):
    if not Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first():
        db.session.add(Enrollment(user_id=current_user.id, course_id=course_id))
        db.session.commit()
        flash('Enrollment Successful!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Unauthorized Access.', 'danger')
        return redirect(url_for('index'))
    return render_template('admin.html', courses=Course.query.all())

@app.route('/admin/add', methods=['POST'])
@login_required
def add_course():
    if current_user.role == 'admin':
        new_c = Course(title=request.form['title'], code=request.form['code'], category=request.form['category'], description=request.form['description'])
        db.session.add(new_c)
        db.session.commit()
        flash('Course added to catalog.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete/<int:id>')
@login_required
def delete_course(id):
    if current_user.role == 'admin':
        db.session.delete(Course.query.get(id))
        db.session.commit()
        flash('Course removed.', 'warning')
    return redirect(url_for('admin_panel'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Thank you! Your inquiry has been sent to the Admissions Office.', 'success')
        return redirect(url_for('index'))
    return render_template('contact.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Seed data if empty
        if Course.query.count() == 0:
            db.session.bulk_save_objects([
                Course(code="BIT6113", title="Data Communication And Network", category="BIT", description="Network fundamentals."),
                Course(code="BIT6083", title="Object Oriented Programming", category="BIT", description="Programming with Java/C++."),
                Course(code="BIT6063", title="Discrete Mathematics", category="BIT", description="Mathematical logic.")
            ])
            db.session.commit()
    app.run(debug=True)