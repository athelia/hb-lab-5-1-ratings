"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie

from sqlalchemy import asc, update


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/register', methods=['GET'])
def register_new_user():
    """Display user registration form."""

    return render_template("registration.html")


@app.route('/register', methods=['POST'])
def process_registration():
    """Register new user if email not already in db."""

    email = request.form.get('email')
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')

    # if user email already exists, ignore
    if User.query.filter(User.email == email).first():
        pass
    else: 
        user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(user)
        db.session.commit()
    # if user email does not exist, add to db

    return redirect('/')


@app.route('/login', methods=['GET'])
def display_login_page():

    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login_user():
    """User login page."""

    #query email and password in database. 
    email = request.form.get('email')
    password = request.form.get('password')


    user = User.query.filter((User.email == email),(User.password == password)).first()

    if user:
    #if matches, log in user (add user_id to flask session)
        session['user_email'] = user.email
        session['user_id'] = user.user_id
        # g.user = user
        # flash- logged in
        flash("Successfully logged in!")
        #redirect to homepage
        return redirect('/user-page')
    else: 
        flash("That is not a valid email & password.")
        return redirect('/login')   


@app.route('/logout')
def logout_user():
    """Remove user from session."""

    del session['user_email']
    del session['user_id']
    flash("Successfully logged out!")

    return redirect('/')


@app.route('/user-page')
def display_user_page():
    """Show specific information about user."""

    user = User.query.filter(User.user_id == session['user_id']).first()

    ratings = user.ratings
    # ratings = Rating.query.filter(Rating.user_id == session['user_id']).all()

    # for rating in ratings:
    #     movie = Movie.query.filter(rating.movie_id == Movie.movie_id).first()
    #     rating.movie_name = movie.title
    #     print(rating.movie.title)

    return render_template('user_page.html', 
                            user=user, 
                            # ratings=ratings,
                            )

@app.route('/movies')
def display_movie_list():
    """Display list of all movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template('movie_list.html', movies=movies)


@app.route('/<movie_id>')
def display_movie_details(movie_id):
    """Display movie deatils."""

    movie = Movie.query.filter(Movie.movie_id == movie_id).one()
    print(movie)

    return render_template('movie_details.html', movie=movie)


@app.route('/rate-movie/<movie_id>', methods=['POST'])
def add_or_update_movie_rating(movie_id):
    """Logged-in user can update or add a new rating."""

    new_rating = request.form.get('rating')

    rating = Rating.query.filter(Rating.user_id == session['user_id'], 
                                 Rating.movie_id ==  movie_id).first()

    if rating: 
        # Flask/SQLAlchemy equivalent of UPDATE
        rating.score = new_rating

        db.session.add(rating)
        db.session.commit()

        flash("Rating updated!")
    else: 
        ## Flask/SQLAlchemy equivalent of INSERT
        user_rating = Rating(score = new_rating, 
                             user_id = session['user_id'], 
                             movie_id =  movie_id
                             )
        db.session.add(user_rating)
        db.session.commit()

        flash("New rating added!")

    return redirect('/movies')

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
