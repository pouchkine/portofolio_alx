from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User, Course, Level, Chapter, Question, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
score = 0

@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(int(user_id))

def basic_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def check_auth(username, password):
    user = session.query(User).filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return True
    return False

def authenticate():
    return jsonify({"message": "Authentication required"}), 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}

@app.route("/")
def home():
    a = session.query(User).filter(User.username.in_(['will'])).all()[0]
    return render_template("home.html") #a.username

@app.route("/auth/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = session.query(User).filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('parcours'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route("/auth/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/auth/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        new_user = User(username=username, email=email, password=password, role=role)
        session.add(new_user)
        try:
            session.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            session.rollback()
            flash(f'Error: {e}')
    return render_template('register.html')

@app.route("/parcours")
@login_required
def parcours():
    courses = session.query(Course).all()
    print(len(courses))
    return render_template('courses.html', courses=courses)

@app.route("/parcours/<langage>")
@login_required
def langs(langage):
    course = session.query(Course).filter_by(title=langage).first()
    if course:
        levels = session.query(Level).filter_by(course_id=course.id).all()
        return render_template('levels.html', course=course, levels=levels)
    return "Course not found"

@app.route("/parcours/<langage>/<level>")
@login_required
def level(langage, level):
    course = session.query(Course).filter_by(title=langage).first()
    if course:
        level_obj = session.query(Level).filter_by(course_id=course.id, difficulte=level).first()
        if level_obj:
            chapters = session.query(Chapter).filter_by(level_id=level_obj.id).all()
            return render_template('chapters.html', course=course, level=level_obj, chapters=chapters)
    return "Level not found"

@app.route("/parcours/<langage>/<level>/<title>")
@login_required
def chapter(langage, level, title):
    course = session.query(Course).filter_by(title=langage).first()
    if course:
        level_obj = session.query(Level).filter_by(course_id=course.id, difficulte=level).first()
        if level_obj:
            chapter = session.query(Chapter).filter_by(level_id=level_obj.id, title = title).first()
            print(chapter)
            if chapter:
                return render_template('lecon.html', course=course, level=level_obj, chapter = chapter)
    return "Level not found"

@app.route("/parcours/<langage>/<level>/<title>/<int:rang>", methods=['GET', 'POST'])
@login_required
def qcm(langage, level, title, rang):
    validation_result = None
    course = session.query(Course).filter_by(title=langage).first()
    if course:
        level_obj = session.query(Level).filter_by(course_id=course.id, difficulte=level).first()
        if level_obj:
            chapter = session.query(Chapter).filter_by(level_id=level_obj.id, title = title).first()
            print(chapter)
            if chapter:
                q = session.query(Question).filter_by(chapter_id=chapter.id, rang = rang).first()
                if request.method == "POST":
                    selected_answer = request.form.get('selected_answer')
                    print("vous avez selectionner", selected_answer)
                    if selected_answer == q.correct_answer:
                        validation_result = True
                        score = 1
                        render_template('qcm.html', course=course, level=level_obj, chapter = chapter , q = q, validation_result = validation_result)
                return render_template('qcm.html', course=course, level=level_obj, chapter = chapter , q = q, validation_result = validation_result)
    return "Level not found"

@app.route("/admin")
@login_required
def admin():
    users = session.query(User).all()
    return render_template('admin.html', users=users)

@app.route("/admin/add_level", methods = ["POST"])
@login_required
def add_level():
    title = request.form.get("title")
    description = request.form.get("description")
    teacher_id = request.form.get("teacher_id")
    course = Course(title= title,description=description,teacher_id=teacher_id)
    return redirect(url_for("admin"))

@app.route("/admin/add_course", methods = ["POST"])
@login_required
def add_course():
    title = request.form.get("title")
    description = request.form.get("description")
    teacher_id = request.form.get("teacher_id")
    course = Course(title= title,description=description,teacher_id=teacher_id)
    session.add(course)
    session.commit()
    return redirect(url_for("admin"))

@app.route("/admin/add_chapter", methods = ["POST"])
@login_required
def add_chapter():
    title = request.form.get("title")
    description = request.form.get("description")
    teacher_id = request.form.get("teacher_id")
    course = Course(title= title,description=description,teacher_id=teacher_id)
    return redirect(url_for("admin"))

@app.route("/admin/add_qcm", methods = ["POST"])
@login_required
def add_qcm():
    title = request.form.get("title")
    description = request.form.get("description")
    teacher_id = request.form.get("teacher_id")
    course = Course(title= title,description=description,teacher_id=teacher_id)
    return redirect(url_for("admin"))

# API Routes with Basic Authentication
@app.route("/api/courses", methods=['GET'])
@basic_auth_required
def api_courses():
    courses = session.query(Course).all()
    return jsonify([course.to_dict() for course in courses])

@app.route("/api/courses/<int:course_id>", methods=['GET'])
@basic_auth_required
def api_course(course_id):
    course = session.query(Course).get(course_id)
    if course:
        return jsonify(course.to_dict())
    return jsonify({"message": "Course not found"}), 404

@app.route("/api/levels/<int:course_id>", methods=['GET'])
@basic_auth_required
def api_levels(course_id):
    levels = session.query(Level).filter_by(course_id=course_id).all()
    return jsonify([level.to_dict() for level in levels])

@app.route("/api/chapters/<int:level_id>", methods=['GET'])
@basic_auth_required
def api_chapters(level_id):
    chapters = session.query(Chapter).filter_by(level_id=level_id).all()
    return jsonify([chapter.to_dict() for chapter in chapters])

@app.route("/api/questions/<int:chapter_id>", methods=['GET'])
@basic_auth_required
def api_questions(chapter_id):
    questions = session.query(Question).filter_by(chapter_id=chapter_id).all()
    return jsonify([question.to_dict() for question in questions])

if __name__ == '__main__':
    app.run(debug=True)

