import sqlalchemy.types
from flask import Flask, render_template, request, url_for, redirect, flash, abort
from main import MainQuiz
import jinja2
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import time
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import SignIn, Login, NewQuiz, EditQuiz, EditQuestion, ResetPassword, InitPassword
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import random
from pdf_extractor import DocExtract
import threading
from flask import current_app
from reset_password import reset_user_password
import requests
from transcribe import YouTubeToMP3
import os
from notify_client import notify_user




app = Flask(__name__)


app.config["STRIPE_PUBLIC_KEY"] = "pk_live_uXasa2a0UpZgokhvwR5mGdIR"

app.config["STRIPE_SECRET_KEY"] = "sk_live_nNPUKCUL7Y6AFk66ktgOvlVo"

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///quizz.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
SITE_KEY = "6Lfo_uYlAAAAAI1Rb43yoD4brIQiq3UscQfcpzen"
SECRET_GOOGLE_KEY = "6Lfo_uYlAAAAAENxgawogQmNVDh-xxkP5n-rtiM3"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


Bootstrap(app)

SUPPORTED_FORMATS = ["pdf", 'docx', "PDF", "DOCX"]
SUPPORTED_VIDEO_FORMATS = ["mp3", "MP3", "mp4", "MP4", 'm4a', "M4A", "wav", "WAV", "mov", "MOV"]


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    quizzes = db.relationship("QuizNames", backref="creator")
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    api_key = db.Column(db.String(1000), nullable=False)
    token = db.Column(db.String())

class QuizNames(db.Model, UserMixin):
    __tablename__ = "quiz_names"
    id = db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quiz_questions = db.relationship("QuizQuestion", backref="quiz_name", cascade='all, delete')
    processed = db.Column(db.Integer, nullable=False)
    public = db.Column(db.String(), nullable=False)
    question_amount = db.Column(db.Integer)
    func_prog = db.Column(db.Integer)

class QuizQuestion(db.Model, UserMixin):
    __tablename__ = "quizquestion"
    id = db.Column(db.Integer, primary_key=True)
    formatted_quiz = db.Column(db.String(10000), unique=False, nullable=False)
    multiple_answers = db.Column(db.String(), unique=False, nullable=False)
    correct_answer = db.Column(db.String(), unique=False, nullable=False)
    quiz_owner = db.Column(db.Integer, db.ForeignKey('quiz_names.id'))



with app.app_context():
    db.create_all()


def percentage_calculator(num1, num2):
    percentage = (num1 / num2) * 100
    return int(percentage)

@app.route("/thanks")
def thanks():
    return render_template("thanks.html")

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/admin")
@login_required
def admin():
    if current_user.email == "ratwemlow@gmail.com":
        with app.app_context():
            users = db.session.query(Users).all()
            quizzes = db.session.query(QuizNames).all()
            return render_template("admin.html", users=users, quizzes=quizzes)
    else:
        return abort(401)

@app.route("/explore", methods=["GET", "POST"])
def explore():
    results = []
    search_term = ""
    with app.app_context():
        if request.method == "POST":
            print(request.form.get("searchterm"))
            search_term = request.form.get("searchterm")
            results = []
            for name in db.session.query(QuizNames).filter_by(public="Public"):
                if search_term.lower() in name.quiz_name.lower():
                    results.append(name)
            for i in results:
                if search_term.lower() == i.quiz_name.lower():
                    item = results.pop(results.index(i))
                    results.insert(0, item)
            print(db.session.query(QuizNames).filter_by(public="Public").order_by(QuizNames.id.desc()).all())
            return render_template("explore.html", quizzes=db.session.query(QuizNames).filter_by(public="Public").order_by(QuizNames.id.desc()).all(),
                               int=int, current_user=current_user, users=Users, db=db, app=app, results=results, search=search_term, score=0)

        return render_template("explore.html", quizzes=db.session.query(QuizNames).filter_by(public="Public").order_by(QuizNames.id.desc()).all(),
                               int=int, current_user=current_user, users=Users, db=db, app=app, results=results, search=search_term, score=0)


@app.route("/delete/<id>")
@login_required
def delete(id):
    with app.app_context():
        quiz = QuizNames.query.get(id)
        db.session.delete(quiz)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route("/edit/title/<id>/", methods=["POST", "GET"])
@login_required
def edit_quiz_title(id):
    quiz_name = QuizNames.query.get(id).quiz_name
    form = EditQuiz(quiz_name=quiz_name)
    if request.method == "POST":
        with app.app_context():
            new_title = form.quiz_name.data
            public = form.share.data
            print(public)
            QuizNames.query.get(id).quiz_name = new_title
            if public != None:
                QuizNames.query.get(id).public = public
            db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_quiz_title.html', id=id, form=form, quiz_name=quiz_name)

@app.route("/edit/question/<id>/<index>/<score>", methods=["POST", "GET"])
@login_required
def edit_quiz_question(id, index, score):
    quiz_info = QuizQuestion.query.get(id)
    print(quiz_info.correct_answer)

    form = EditQuestion(question=quiz_info.formatted_quiz, correct_answer=quiz_info.correct_answer)
    if request.method == "POST" and form.validate_on_submit():
        with app.app_context():
            new_question = form.question.data
            QuizQuestion.query.get(id).formatted_quiz = new_question
            db.session.commit()
            new_answer = form.correct_answer.data
            QuizQuestion.query.get(id).correct_answer = new_answer
            db.session.commit()
        id = db.session.query(QuizQuestion).get(id).quiz_owner
        return redirect(url_for('main_quiz', index=index, id=id, score=score))


    return render_template("edit_quiz_question.html", form=form, quiz_info=quiz_info, index=index, id=id, score=score)

@app.route("/startreset", methods=["POST", "GET"])
def init_reset():
    with app.app_context():
        print(request.method)
        form = InitPassword()
        if request.method == "POST":

            print(form.validate_on_submit())
            email = form.email.data
            print(Users.query.filter_by(email=email).first())
            if Users.query.filter_by(email=email).first() != None:

                token = str(random.randint(134658, 45986928743654876438756836834756)) + email.split("@")[0]
                print(token)
                threading.Thread(target=reset_user_password, kwargs={"receiving_email": email,
                                                                     "link": url_for("reset_password",
                                                                                     token=token, email=email)}).start()
                Users.query.filter_by(email=email).first().token = token
                db.session.commit()
                return render_template("init_reset_sent.html", form=form)
            flash("Email Doesn't Exist")
            return redirect(url_for("signup"))
        return render_template("init_reset.html", form=form)

@app.route("/reset-password<token>/<email>", methods=["POST", "GET"])
def reset_password(token, email):
    form = ResetPassword()
    with app.app_context():
        if request.method == "POST":
            Users.query.filter_by(email=email).first().password = generate_password_hash(password=form.new_password.data, salt_length=8)
            db.session.commit()
            return redirect(url_for("login"))
        print(request.method)
        return render_template("reset_password.html", token=token, email=email, form=form)





@app.route("/dashboard")
def dashboard():
    if current_user.is_authenticated:
        all_questions = current_user.quizzes
        if all_questions != []:
            temporary_list = []
            earliest_quiz = 0
            for i in all_questions:
                if i.id > earliest_quiz:
                    earliest_quiz = i.id
                    temporary_list.insert(0, i)
            all_questions = temporary_list

        return render_template('dashboard.html', quiz=all_questions, int=int)
    else:
        return redirect(url_for("login"))




@app.route("/signup", methods=["POST", "GET"])
def signup():
    form = SignIn()
    with app.app_context():
        if request.method == "POST":
            parameters = {
                "secret": SECRET_GOOGLE_KEY,
                "response": request.form["g-recaptcha-response"],
            }
            print(parameters)
            chosen_email = Users.query.filter_by(email=form.email.data).first()
            print(chosen_email)
            if chosen_email == None:
                password = generate_password_hash(password=form.password.data, salt_length=8)
                new_user = Users(name=form.name.data,
                                email=form.email.data,
                                password=password,
                                 api_key=form.api_key.data)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)

                return redirect(url_for('dashboard'))
            else:
                flash("Email already exists")
                return redirect(url_for('login'))

    return render_template("signup.html", form=form, site_key=SITE_KEY)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = Login()
    with app.app_context():
        if request.method == "POST":
            user_email = Users.query.filter_by(email=form.email.data).first()
            if user_email != None:
                if check_password_hash(pwhash=user_email.password, password=form.password.data):
                    login_user(user_email)
                    return redirect(url_for('dashboard'))
                else:
                    flash("Incorrect Password")
                    return redirect(url_for('login'))
            else:
                flash("Email doesn't exist")
                return redirect(url_for('signup'))
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def generate_quiz(lecture_slides, chapter, quiz_name, path, user, share, youtube_link, audio_video, email, name, url, quiz_length, api_key):
    with app.app_context():
        new_quiz_name = QuizNames(quiz_name=quiz_name,
                                  user_id=user, processed=0, public=share, func_prog=1)
        db.session.add(new_quiz_name)
        db.session.commit()


        if lecture_slides != "":
            print("got Lectures")
            if lecture_slides.split(".")[1] == "pdf":
                lecture = DocExtract()
                main_quiz = MainQuiz(api_key=api_key, quiz_length=quiz_length)
                main_quiz.paragraph(lecture.pdf_to_string(path=path))
                db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first().func_prog = 10
                db.session.commit()

            elif lecture_slides.split(".")[1] == "docx":
                lecture = DocExtract()
                main_quiz = MainQuiz(api_key=api_key, quiz_length=quiz_length)
                main_quiz.paragraph(lecture.docx_to_string(path=path))
                db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first().func_prog = 10
                db.session.commit()


        elif youtube_link != "":
            words = YouTubeToMP3()
            words.convert(youtube_link)
            main_quiz = MainQuiz(api_key=api_key, quiz_length=quiz_length)
            db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first().func_prog = 10
            db.session.commit()
            main_quiz.paragraph(words.transcribe(words.path, api_key=api_key))
            os.remove(words.path)


        elif audio_video != "":
            words = YouTubeToMP3()
            main_quiz = MainQuiz(api_key=api_key, quiz_length=quiz_length)
            db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first().func_prog = 10
            db.session.commit()
            main_quiz.paragraph(words.transcribe(path, api_key=api_key))
            os.remove(path)

        elif chapter != "":
            print("got Chapters")
            main_quiz = MainQuiz(api_key=api_key, quiz_length=quiz_length)
            main_quiz.paragraph(chapter)

        formatted_quiz = main_quiz.format_quiz(db, QuizNames, new_quiz_name, app)
        if formatted_quiz != "FAILED":
            multiple_questions = []
            correct_answer = []
            index = 0
            completed = True
            print(formatted_quiz)
            for i in list(formatted_quiz):
                try:
                    multiple_questions.append(main_quiz.multiple_answers(formatted_quiz[i]))
                    correct_answer.append(formatted_quiz[i])
                    new_quiz = QuizQuestion(quiz_owner=new_quiz_name.id,
                                            formatted_quiz=i,
                                            multiple_answers="@ ".join(multiple_questions[list(formatted_quiz).index(i)]),
                                            correct_answer=correct_answer[list(formatted_quiz).index(i)]
                                            )
                    db.session.add(new_quiz)
                    db.session.commit()
                except:
                    print("MULTIPLE CHOICE API ISSUE")
                    completed = False
                    break
            db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first().func_prog = 95
            db.session.commit()

            if completed == True:
                quiz_length = len(db.session.query(QuizQuestion).filter_by(quiz_owner=new_quiz_name.id).all())

                db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first().processed = 1
                db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first().question_amount = quiz_length
                db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first().func_prog = 100
                db.session.commit()
                notify_user(receiving_email=email, name=name, link=url, quiz_name=quiz_name)
                print(new_quiz_name.processed)
                return "Done!"
            else:
                item = db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first()
                db.session.delete(item)
                db.session.commit()
                print("FAILED")
        else:
            item = db.session.query(QuizNames).filter_by(id=new_quiz_name.id).first()
            db.session.delete(item)
            db.session.commit()
            return "QUIZ FAILED"



@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    form = NewQuiz()

    user = current_user.id
    with app.app_context():
        if request.method == "POST":

            if form.validate_on_submit():
                if form.question_amount.data < 1:
                    quiz_length = 1
                else:
                    quiz_length = form.question_amount.data
                quiz_name = form.quiz_name.data

                chapter = form.text_chapter.data
                youtube_link = form.youtube_link.data
                path = ""
                lecture_slides = request.files["lecture-slides"]
                audio_video = request.files["audio_video"]

                print(chapter)
                print(lecture_slides.filename)
                share = form.share.data

                if lecture_slides.filename != "":
                    if lecture_slides.filename.split(".")[1] in SUPPORTED_FORMATS:
                        print("got Lectures")
                        file_name = f'{lecture_slides.filename.split(".")[0]}{(str(random.randint(1, 100000000)))}.{lecture_slides.filename.split(".")[1]}'
                        print(file_name)
                        path = f"./media/{file_name}"
                        lecture_slides.save(path)
                        threading.Thread(target=generate_quiz, kwargs={"lecture_slides": lecture_slides.filename,
                                                                       "chapter": chapter,
                                                                       "quiz_name": quiz_name,
                                                                       "path": path,
                                                                       "user": user,
                                                                       "share": share,
                                                                       "youtube_link": youtube_link,
                                                                       "audio_video": audio_video.filename,
                                                                       "email": current_user.email,
                                                                       "name": current_user.name,
                                                                       "url": url_for("dashboard"),
                                                                       "quiz_length": quiz_length,
                                                                       "api_key": current_user.api_key}).start()
                    else:
                        flash("Unrecognized File Type")
                        return redirect(url_for('quiz'))

                elif youtube_link != "":
                    print("Got Youtube Link")

                    threading.Thread(target=generate_quiz, kwargs={"lecture_slides": lecture_slides.filename,
                                                                   "chapter": chapter,
                                                                   "quiz_name": quiz_name,
                                                                   "path": path,
                                                                   "user": user,
                                                                   "share": share,
                                                                   "youtube_link": youtube_link,
                                                                   "audio_video": audio_video.filename,
                                                                   "email": current_user.email,
                                                                   "name": current_user.name,
                                                                   "url": url_for("dashboard"),
                                                                   "quiz_length": quiz_length,
                                                                    "api_key": current_user.api_key}).start()


                elif audio_video.filename != "":
                    if audio_video.filename.split(".")[1] in SUPPORTED_VIDEO_FORMATS:
                        print("Got Audio/Video")
                        file_name = f'{audio_video.filename.split(".")[0]}{(str(random.randint(1, 100000000)))}.{audio_video.filename.split(".")[1]}'
                        print(file_name)
                        path = f"./media/{file_name}"
                        audio_video.save(path)
                        threading.Thread(target=generate_quiz, kwargs={"lecture_slides": lecture_slides.filename,
                                                                       "chapter": chapter,
                                                                       "quiz_name": quiz_name,
                                                                       "path": path,
                                                                       "user": user,
                                                                       "share": share,
                                                                       "youtube_link": youtube_link,
                                                                       "audio_video": audio_video.filename,
                                                                       "email": current_user.email,
                                                                       "name": current_user.name,
                                                                       "url": url_for("dashboard"),
                                                                       "quiz_length": quiz_length,
                                                                       "api_key": current_user.api_key}).start()
                    else:
                        flash("Unrecognized File Type")
                        return redirect(url_for('quiz'))


                elif chapter != "":
                    print("got Chapters")
                    threading.Thread(target=generate_quiz, kwargs={"lecture_slides": lecture_slides.filename,
                                                                   "chapter": chapter,
                                                                   "quiz_name": quiz_name,
                                                                   "path": path,
                                                                   "user": user,
                                                                   "share": share,
                                                                   "youtube_link": youtube_link,
                                                                   "audio_video": audio_video.filename,
                                                                   "email": current_user.email,
                                                                   "name": current_user.name,
                                                                   "url": url_for("dashboard"),
                                                                   "quiz_length": quiz_length,
                                                                    "api_key": current_user.api_key}).start()

                return render_template("quiz_is_being_generated.html")

            else:
                flash("You must enter one the required field below")
                return redirect(url_for('quiz'))
        else:

            all_questions = db.session.query(QuizQuestion).all()
            return render_template("create_quiz.html", quiz_database=all_questions, int=int, print=print, len=len, form=form)



@app.route("/main_quiz/<id>/<index>/<score>")
def main_quiz(index, id, score):
    all_questions = QuizQuestion.query.filter_by(quiz_owner=id).all()
    quiz_owner = QuizNames.query.get(id)
    if quiz_owner.public == "Public":
        print(type(index))
        if int(index) == 0:
            score = 0
        else:
            score = score
        print(all_questions)
        with app.app_context():
            answers = all_questions
            print(answers)
            for i in answers:
                randomised = i.multiple_answers.split("@ ")
                randomised.append(i.correct_answer)
                random.shuffle(randomised)

                i.multiple_answers = "@ ".join(randomised)
                db.session.commit()

        return render_template("quiz.html", quiz_database=all_questions, index=index, int=int, print=print, len=len,
                               id=id, current_user=current_user, quiz_owner=quiz_owner, score=score)

    elif quiz_owner.public == "Private":
        if current_user.is_authenticated:
            if quiz_owner.user_id == current_user.id:
                print(type(index))
                if int(index) == 0:
                    score = 0
                else:
                    score = score
                print(all_questions)
                with app.app_context():
                    answers = all_questions
                    print(answers)
                    for i in answers:
                        randomised = i.multiple_answers.split("@ ")
                        randomised.append(i.correct_answer)
                        random.shuffle(randomised)

                        i.multiple_answers = "@ ".join(randomised)
                        db.session.commit()

                return render_template("quiz.html", quiz_database=all_questions, index=index, int=int, print=print, len=len,
                                       id=id, current_user=current_user, quiz_owner=quiz_owner, score=score)
            else:
                return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))


@app.route("/verify/<user>/<id>/<index>/<quiz_owner>/<quiz_user>/<score>", methods=["GET", "POST"])
def verify(user, index, id, quiz_owner, quiz_user, score):

    if quiz_owner == "Public":
        all_questions = QuizQuestion.query.filter_by(quiz_owner=id).all()


        if user.replace(":", "").replace("\n", "").replace(".", "").strip() == all_questions[int(index)].correct_answer.replace(":", "").replace("\n", "").replace(".", "").strip():
            score = int(score) + 1
            return render_template("correct.html", correct_answer=all_questions[int(index)].correct_answer, index=index,
                                   int=int, quiz=all_questions, len=len, id=id, score=score)
        else:

            return render_template("incorrect.html", correct_answer=all_questions[int(index)].correct_answer, index=index,
                                   int=int, quiz=all_questions, len=len, id=id, score=score)
    elif quiz_owner == "Private":
        print(current_user.id)
        print(score)
        if current_user.id == int(quiz_user):
            all_questions = QuizQuestion.query.filter_by(quiz_owner=id).all()
            print(all_questions)

            if user.replace(":", "").replace("\n", "").replace(".", "").strip() == all_questions[
                int(index)].correct_answer.replace(":", "").replace("\n", "").replace(".", "").strip():
                score = int(score) + 1
                return render_template("correct.html", correct_answer=all_questions[int(index)].correct_answer,
                                       index=index,
                                       int=int, quiz=all_questions, len=len, id=id, score=score)
            else:

                return render_template("incorrect.html", correct_answer=all_questions[int(index)].correct_answer,
                                       index=index,
                                       int=int, quiz=all_questions, len=len, id=id, score=score)
        else:
            return redirect(url_for("login"))

@app.route("/result/<score>/<quiz>/<index>/<id>")
def result(score, quiz, index, id):

    return render_template("result.html", int=int, score=score, quiz=quiz, percentage_calculator=percentage_calculator, index=index, id=id)






if __name__ == "__main__":
    app.run(debug=True, port=5050)
