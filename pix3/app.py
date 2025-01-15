from flask import Flask, render_template, redirect, url_for, request, flash , jsonify, session as s
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User, Course, Level, Chapter, Question, session, UserCourse, Score
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
score = 0

@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(int(user_id))

@app.route("/")
def home():
   # a = session.query(User).filter(User.username.in_(['will'])).all()[0]
    return render_template("home.html") #a.username

@app.route("/auth/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = session.query(User).filter_by(email=email).first()
        s['username'] = user.username
        if user and user.password == password:
            login_user(user)
            if current_user.role == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for('parcours'))
        else:
            flash('Invalid email or password')
    return render_template('login.html') #+2438139720259

@app.route("/profile")
@login_required
def profile():
    user_courses = session.query(UserCourse).filter_by(user_id = current_user.id).all()
    user_courses_ids = [user_course.id for user_course in user_courses]
    course_ids = [user_course.course_id for user_course in user_courses]
    courses = [session.query(Course).filter_by(id = course_id).first() for course_id in course_ids]
    scores = [session.query(Score).filter_by(course_user_id = user_courses_id).first() for user_courses_id in user_courses_ids]
    datas = list(zip(courses, scores))
    #if s['score']:
       # username = s["username"]
        #score = s["score"]
       # return render_template("profil.html", username = username, score = score) #str(s['score'])
    return render_template("profil.html", datas = datas , current_user = current_user) # "yoo"

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
        password = request.form['password']
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
                #condition : variable pour savoir si on deja enregistrer ou pas
                condition = session.query(UserCourse).filter_by(course_id = course.id).first()
                if not condition:
                    user_cou = UserCourse(user_id = current_user.id, course_id = course.id )
                    session.add(user_cou)
                    session.commit()
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
                        user_course = session.query(UserCourse).filter_by(user_id = current_user.id, course_id = course.id).first()
                        score = session.query(Score).filter_by(course_user_id = user_course.id).first()
                        score.score = score.score + 1
                        session.add(score)
                        session.commit()
                        s['score'] = score.score
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

def to_dict(u):
    u.pop("_sa_instance_state")
    return u

@app.route("/api/v1/parcours")
def api_parcours():
    courses = session.query(Course).all()
    courses_dict = [to_dict(course.__dict__) for course in courses]
    return jsonify(courses_dict)

@app.route("/api/v1/parcours/<int:id>")
def api_parcours_id(id):
    course = session.query(Course).filter_by(id = id).first()
    course_dict = to_dict(course.__dict__)
    return jsonify(course_dict)

if __name__ == '__main__':
    app.run(debug=True)

