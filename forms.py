from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, validators
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, URL, Email, Length
from flask_ckeditor import CKEditorField

def one_field_required(form, field):
  # Check if any of the form fields have a value
  if form.youtube_link.data or form.text_chapter.data or form.audio_video.data or form.lecture_slides.data:
    # At least one field has a value, so return True
    return True
  else:
    # No fields have a value, so return False
    return False



class SignIn(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    email = StringField(label="Email", validators=[Email(), DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(8)])
    submit = SubmitField(label="Sign Up")

class Login(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    email = StringField(label="Email", validators=[Email(), DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(8)])
    signup = SubmitField(label="Sign Up")

class NewQuiz(FlaskForm):
    quiz_name = StringField(label="Quiz Name", validators=[DataRequired()])
    youtube_link = StringField(label="Youtube URL")
    text_chapter = TextAreaField(label="Text Input")
    audio_video = FileField(label="Audio/Video")
    lecture_slides = FileField(label="Images")

class EditQuiz(FlaskForm):
    quiz_name = StringField(label="Quiz Name", validators=[DataRequired()])

class EditQuestion(FlaskForm):
    question = TextAreaField(label="Quiz Question", validators=[DataRequired()])
    correct_answer = TextAreaField(label="Correct Answer", validators=[DataRequired()])

class ResetPassword(FlaskForm):
    new_password = PasswordField(label="Password", validators=[DataRequired(), Length(8)])

class InitPassword(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])