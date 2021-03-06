from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from forms import LoginForm, RegisterForm, CreatePostForm, CommentForm, CatchForm, WeatherForm, SpotForm
from functools import wraps
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from flask_gravatar import Gravatar
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
from datetime import date
import requests
import arrow
import statistics
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
ckeditor = CKEditor(app)
Bootstrap(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)


#Connect to database online = os.environ.get("Database_URL") // offline = "sqlite:///lhunters.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lhunters.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


""" DatabaseClasses """


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    comment_author = relationship("User", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


class Catch(db.Model):
    __tablename__ = "catches"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(20), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    method = db.Column(db.String(20), nullable=False)


class Weather(db.Model):
    __tablename__ = "weatherdata"
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
    __tablename__ = "spots"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.String(100), nullable=False)
    spot_info = db.Column(db.String(100), nullable=False)

db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            #User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("index"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('index'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/blog')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("blog.html", all_posts=posts, current_user=current_user)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()

    return render_template("post.html", post=requested_post, form=form, current_user=current_user)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route('/catch', methods=['GET', 'POST'])
def catch():
    form = CatchForm()
    catches = Catch.query.all()
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

    return render_template('catch.html', form=form, f??nge=catches)


@app.route('/weather', methods=['GET', 'POST'])
def weather():
    tagesbeginn = arrow.utcnow().shift(hours=+1)
    tagesende = tagesbeginn.shift(hours=+48)
    API_key = '135b1dd2-8385-11ec-9a77-0242ac130002-135b1e54-8385-11ec-9a77-0242ac130002'
    response = requests.get(
        'https://api.stormglass.io/v2/weather/point',
        params={
            'lat': '54.066429',
            'lng': '10.768570',
            'params': ','.join(
                ['airTemperature', 'waterTemperature', 'windDirection', 'windSpeed', 'swellDirection', 'swellHeight',
                 'swellPeriod', 'windWaveDirection', 'currentDirection', ]),
            'start': tagesbeginn.to('UTC').timestamp(),
            'end': tagesende.to('UTC').timestamp(),
        },
        headers={
            'Authorization': API_key
        }
    )

    weather_data = response.json()

    def get_median(weather_data: dict, keyword: str, hour: int):

        list_of_data = []

        for i in weather_data["hours"]:
            list_of_data.append(weather_data["hours"][hour][keyword])

        # calculate the median
        median_of_requested_data = list_of_data[int(len(list_of_data) / 2)]

        # calculate the median of the median_of_requested_data dictionary
        median_data_list = []
        for key, value in median_of_requested_data.items():
            median_data_list.append(value)

        # calculate the median of the median_data_list list
        print(median_data_list[int(len(median_data_list) / 2)])
        return median_data_list[int(len(median_data_list) / 2)]


    def get_all_params(weather_data, parameter, hour=None):
        n = 0
        list_of_data = []
        for i in range(0, len(weather_data["hours"][n])):
            list_of_data.append(get_median(weather_data, parameter, hour=n))
            if n <= 48:
                n += 1
            else:
                break
        return list_of_data


    get_median(weather_data, keyword="windDirection", hour=0)
    air_temperature_srksdrf = (get_all_params(weather_data, "airTemperature"))
    swell_direction_srksdrf = (get_all_params(weather_data, "swellDirection"))
    swell_height_srksdrf = (get_all_params(weather_data, "swellHeight"))
    swell_period_srksdrf = (get_all_params(weather_data, "swellPeriod"))
    water_temperature_srksdrf = (get_all_params(weather_data, "waterTemperature"))
    wind_direction_srksdrf = (get_all_params(weather_data, "windDirection"))
    wind_speed_srksdrf = (get_all_params(weather_data, "windSpeed"))
    wind_wave_direction_srksdrf = (get_all_params(weather_data, "windWaveDirection"))
    current_direction_srksdrf = (get_all_params(weather_data, "currentDirection"))

    return render_template('weather.html', weather_data=weather_data, air_temperature_srksdrf=air_temperature_srksdrf, swell_direction_srksdrf=swell_direction_srksdrf, swell_height_srksdrf=swell_height_srksdrf, swell_period_srksdrf=swell_period_srksdrf, water_temperature_srksdrf=water_temperature_srksdrf, wind_direction_srksdrf=wind_direction_srksdrf, wind_speed_srksdrf=wind_speed_srksdrf, wind_wave_direction_srksdrf=wind_wave_direction_srksdrf, current_direction_srksdrf=current_direction_srksdrf)


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