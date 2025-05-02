from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booking.db'
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__ = "User"

    user_id = db.Column('User ID', db.String(50), primary_key=True)  # String ID based on email
    first_name = db.Column('First Name', db.String(50), nullable=False)
    last_name = db.Column('Last Name', db.String(50), nullable=False)
    email = db.Column('Email', db.String(100), unique=True, nullable=False)
    role = db.Column('Role', db.String(20), nullable=False)
    password = db.Column('Password', db.String(255), nullable=False)  # Store hashed password in production

    def __repr__(self):
        return f"<User {self.email}>"
    def get_id(self):
        return self.user_id


class Room(db.Model):
    __tablename__ = 'Room'
    room_code = db.Column('Room Code', db.String, primary_key=True)
    capacity = db.Column('Capacity', db.Integer, nullable=False)
    room_type = db.Column('Room Type', db.String, nullable=False)
    student_bookable = db.Column('Student Bookable', db.Integer, nullable=False)
    room_loc = db.Column('Room Loc', db.String, nullable=False)

class Booking(db.Model):
    __tablename__ = 'Booking'
    booking_id = db.Column('Booking ID', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column('User ID', db.String, db.ForeignKey('User.User ID'))
    room_code = db.Column('Room Code ', db.String, db.ForeignKey('Room.Room Code'))
    date = db.Column('Date', db.Integer, nullable=False)
    start_time = db.Column('Start Time', db.Integer, nullable=False)
    end_time = db.Column('End  Time', db.Integer, nullable=False)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        user_id = request.form['user_id']
        room_code = request.form['room_code']
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        new_booking = Booking(user_id=user_id, room_code=room_code, date=date, start_time=start_time, end_time=end_time)
        db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('bookingcon.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
