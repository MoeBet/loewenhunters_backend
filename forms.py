from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.fields.html5 import DecimalRangeField, DateField, TimeField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField



"""Forms"""


class CatchForm(FlaskForm):
    date = DateField('Datum', validators=[DataRequired()])
    time = TimeField('Uhrzeit', validators=[DataRequired()])
    location = StringField('Ort', validators=[DataRequired()])
    species = StringField('Spezies', validators=[DataRequired()])
    size = StringField('Länge', validators=[DataRequired()])
    method = StringField('Methode', validators=[DataRequired()])
    submit = SubmitField('Senden')


class WeatherForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    longitude = DecimalRangeField('Longitude', validators=[DataRequired()])
    latitude = DecimalRangeField('Latitude', validators=[DataRequired()])
    air_temperature = DecimalRangeField('Air Temperature', validators=[DataRequired()])
    water_temperature = DecimalRangeField('Water Temperature', validators=[DataRequired()])
    wind_speed = DecimalRangeField('Wind Speed', validators=[DataRequired()])
    wind_direction = StringField('Wind Direction', validators=[DataRequired()])
    swell_height = DecimalRangeField('Swell Height', validators=[DataRequired()])
    swell_period = DecimalRangeField('Swell Period', validators=[DataRequired()])
    swell_direction = StringField('Swell Direction', validators=[DataRequired()])
    current_direction = StringField('Current Direction', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SpotForm(FlaskForm):
    date = DateField('Datum', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    longitude = StringField('Longitude', validators=[DataRequired()])
    latitude = StringField('Latitude', validators=[DataRequired()])
    spot_info = StringField('Informationen zum Spot', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")