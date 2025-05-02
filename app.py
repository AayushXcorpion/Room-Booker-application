import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Booking, Room
from datetime import datetime
from sqlalchemy import and_, or_
import time

#from werkzeug.security import generate_password_hash, check_password_hash

folderPath = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.abspath("templates"))  
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + folderPath + "/Roombooker.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for session management

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect unauthorized users to login page



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def home():
    if current_user.is_authenticated:
            return redirect(url_for('profile'))  # Redirect logged-in users to their profile page
    return render_template('login.html') 

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        role = request.form.get("role")
        password = request.form.get("password")  

        
        user_id = email.split("@")[0]

       
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists. Please log in or use a different email.", "danger")
            return redirect(url_for("signup"))

        # Create new user
        new_user = User(
            user_id=user_id,  
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=role,
            password=password  
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))  # Redirect to profile if already logged in
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:  # Check password (can be hashed later)
            login_user(user)
            return redirect(url_for('profile'))  # Redirect to profile after login
        else:
            flash("Invalid credentials. Please try again.", "error")
            return render_template('login.html')

    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))

@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', current_time=int(time.time()))



@app.route("/bookings")
@login_required
def bookings():
    bookings = Booking.query.all()
    return render_template("bookings.html", bookings=bookings)

@app.route("/rooms")
@login_required
def rooms():
    rooms = Room.query.all()
    return render_template("rooms.html", rooms=rooms)

@app.route("/users")
@login_required
def users():
    users = User.query.all()
    return render_template("users.html", users=users)



@app.route("/add_booking", methods=["GET", "POST"])
@login_required
def add_booking():
    if request.method == "POST":
        room_code = request.form["room_code"]
        date = request.form["date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]

        # Convert date and time to check constraints
        booking_date = datetime.strptime(date, "%Y-%m-%d")
        weekday = booking_date.weekday()  # Monday = 0, Sunday = 6
        start_time_obj = datetime.strptime(start_time, "%H:%M").time()
        end_time_obj = datetime.strptime(end_time, "%H:%M").time()
        opening_time = datetime.strptime("08:30", "%H:%M").time()
        closing_time = datetime.strptime("15:00", "%H:%M").time()

        # Validation rules
        if weekday in [5, 6]:  # No bookings on weekends
            flash("Rooms cannot be booked on weekends!", "danger")
            return redirect(url_for("add_booking"))

        if start_time_obj < opening_time or end_time_obj > closing_time:
            flash("Bookings can only be made between 8:30 AM and 3:00 PM!", "danger")
            return redirect(url_for("add_booking"))

        if end_time_obj <= start_time_obj:
            flash("End time must be later than start time!", "danger")
            return redirect(url_for("add_booking"))

        # Check for overlapping bookings in the same room
        existing_booking = Booking.query.filter(
            Booking.room_code == room_code,
            Booking.date == date,
            or_(
                and_(Booking.start_time <= start_time, Booking.end_time > start_time),
                and_(Booking.start_time < end_time, Booking.end_time >= end_time),
                and_(Booking.start_time >= start_time, Booking.end_time <= end_time)
            )
        ).first()

        if existing_booking:
            flash("This room is already booked during the selected time! Please check the bookings.", "danger")
            return redirect(url_for("add_booking"))

        # Create new booking
        new_booking = Booking(
            user_id=current_user.user_id,
            room_code=room_code,
            date=date,
            start_time=start_time,
            end_time=end_time
        )

        db.session.add(new_booking)
        db.session.commit()

        flash("Booking created successfully!", "success")
        return redirect(url_for("bookings"))

    # Get available rooms based on user role
    if current_user.role == "Student":
        rooms = Room.query.filter_by(student_bookable=1).all()
    else:
        rooms = Room.query.all()

    return render_template("add_booking.html", rooms=rooms)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
