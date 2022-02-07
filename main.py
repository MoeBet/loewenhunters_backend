from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import DecimalRangeField, DateField, TimeField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


""" DatabaseClasses """


class Catch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(20), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    method = db.Column(db.String(20), nullable=False)


class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.String(100), nullable=False)
    air_temperature = db.Column(db.Integer, nullable=False)
    water_temperature = db.Column(db.Integer, nullable=False)
    wind_speed = db.Column(db.Integer, nullable=False)
    wind_direction = db.Column(db.String(20), nullable=False)
    swell_height = db.Column(db.Integer, nullable=False)
    swell_period = db.Column(db.Integer, nullable=False)
    swell_direction = db.Column(db.String(20), nullable=False)
    current_direction = db.Column(db.String(20), nullable=False)


class Spot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.String(100), nullable=False)
    spot_info = db.Column(db.String(100), nullable=False)

db.create_all()


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

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/catch', methods=['GET', 'POST'])
def catch():
    form = CatchForm()
    if request.method == 'POST':
        new_catch = Catch(
            date=request.form['date'],
            time=request.form['time'],
            location=request.form['location'],
            species=request.form['species'],
            size=request.form['size'],
            method=request.form['method']
    )
        db.session.add(new_catch)
        db.session.commit()
        return redirect(url_for('catch'))

    return render_template('catch.html', form=form)


@app.route('/weather', methods=['GET', 'POST'])
def weather():
    return render_template('weather.html')


@app.route('/spots', methods=['GET', 'POST'])
def spots():
    form = SpotForm()
    if request.method == 'POST':
        new_spot = Spot(
            date=request.form['date'],
            name=request.form['name'],
            longitude=request.form['longitude'],
            latitude=request.form['latitude'],
            spot_info=request.form['spot_info']
        )
        db.session.add(new_spot)
        db.session.commit()
        return redirect(url_for('spots'))

    return render_template('spots.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)