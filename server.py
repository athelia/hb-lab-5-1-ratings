"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


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

    # if user email already exists, ignore
    if User.query.filter(User.email == email).first():
        pass
    else: 
        user = User(email=email, password=password)
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
        return redirect('/')
    else: 
        flash("That is not a valid email & password.")
        return redirect('/login')   


@app.route('/logout')
def logout_user():
    """Remove user from session."""

    del session['user_email']
    flash("Successfully logged out!")

    return redirect('/')


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
