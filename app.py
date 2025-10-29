from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "train123"  # session secret key

# ✅ Database connection helper
def get_db_connection():
    return mysql.connector.connect(
        host="0o0atm.h.filess.io",
        user="train-travelling _lastsource",
        password="af2e5acf9e136c2e2d9c60d8f66a34f6dcb4b8d4",
        database="train-travelling _lastsource",
        port="3307"
    )


# 🟢 Home / Login Page
@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('base'))
        else:
            flash('Invalid Username or Password!', 'danger')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        exist = cursor.fetchone()

        if exist:
            flash('Username already exists!', 'warning')
        else:
            cursor.execute("INSERT INTO users (fullname, username, password) VALUES (%s, %s, %s)",
                           (fullname, username, password))
            conn.commit()
            flash('Signup successful! Please login.', 'success')
            conn.close()
            return redirect(url_for('login'))
        conn.close()
    return render_template('signup.html')


# 🟢 Base Page — Search Trains
@app.route('/base', methods=['GET', 'POST'])
def base():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        from_station = request.form['from_station']
        to_station = request.form['to_station']
        date = request.form['date']
        time = request.form['time']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM trains 
            WHERE LOWER(from_station)=LOWER(%s) AND LOWER(to_station)=LOWER(%s)
        """, (from_station, to_station))
        trains = cursor.fetchall()
        conn.close()

        return render_template('train.html', trains=trains, date=date, time=time)
        
    return render_template('base.html', username=session['username'])


# 🟢 Ticket Form Page
@app.route('/ticket/<int:train_id>', methods=['GET', 'POST'])
def ticket(train_id):
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        email = request.form['email']
        phone = request.form['phone']
        class_type = request.form['class_type']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            INSERT INTO bookings (user_id, train_id, name, age, gender, email, phone, class_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], train_id, name, age, gender, email, phone, class_type))
        conn.commit()
        conn.close()

        flash('Ticket booked successfully!', 'success')
        return redirect(url_for('book', train_id=train_id))
        
    return render_template('ticket.html', train_id=train_id)


# 🟢 Booking Confirmation
@app.route('/book/<int:train_id>')
def book(train_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM trains WHERE id=%s", (train_id,))
    train = cursor.fetchone()
    cursor.execute("SELECT * FROM bookings WHERE train_id=%s AND user_id=%s ORDER BY id DESC LIMIT 1",
                   (train_id, session['user_id']))
    booking = cursor.fetchone()
    conn.close()
    return render_template('book.html', booking=booking, train=train)


# 🟢 Update Booking
@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        class_type = request.form['class_type']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET class_type=%s WHERE id=%s", (class_type, booking_id))
        conn.commit()
        conn.close()

        flash('Booking updated successfully!', 'info')

    return render_template('update.html')


# 🟢 Cancel Booking
@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bookings WHERE id=%s", (booking_id,))
        conn.commit()
        conn.close()
        flash('Booking cancelled successfully!', 'danger')
    return render_template('cancel.html')


# 🟢 Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
