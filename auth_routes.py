from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
import re, random, time

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email format.')
            return redirect(url_for('auth.signup'))
        if len(password) < 8:
            flash('Password must be at least 8 characters long.')
            return redirect(url_for('auth.signup'))
        if not re.search(r"[A-Z]", password):
            flash('Password must contain at least one uppercase letter.')
            return redirect(url_for('auth.signup'))
        if not re.search(r"[a-z]", password):
            flash('Password must contain at least one lowercase letter.')
            return redirect(url_for('auth.signup'))
        if not re.search(r"[0-9]", password):
            flash('Password must contain at least one number.')
            return redirect(url_for('auth.signup'))

        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if existing_user:
            conn.close()
            flash('Email already registered')
            return redirect(url_for('auth.login'))

        hpass = generate_password_hash(password)
        conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hpass))
        conn.commit()
        conn.close()

        flash('Account created successfully')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if not email or not password:
            flash('Please enter both email and password')
            return redirect(url_for('auth.login'))
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email')
            return redirect(url_for('auth.login'))

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if not user or not check_password_hash(user['password'], password):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))

        if user['is_suspended']:
            flash('Your account has been suspended')
            return redirect(url_for('auth.login'))

        otp = str(random.randint(100000, 999999))
        session['pending_user'] = dict(user)
        session['otp'] = otp
        session['otp_time'] = time.time()

        print(f"OTP for {email}: {otp}")

        flash('A 6-digit verification code has been sent check terminal')
        return redirect(url_for('auth.verify_otp'))

    return render_template('login.html')


@auth.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_code = request.form['otp'].strip()
        otp = session.get('otp')
        otp_time = session.get('otp_time')

        if not otp or not otp_time:
            flash('No OTP generated')
            return redirect(url_for('auth.login'))

        if time.time() - otp_time > 120:
            flash('OTP expired')
            session.pop('otp', None)
            session.pop('otp_time', None)
            return redirect(url_for('auth.login'))

        if entered_code == otp:
            user = session.pop('pending_user', None)
            session.pop('otp', None)
            session.pop('otp_time', None)

            if user:
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['is_admin'] = user['is_admin']
                session['is_seller'] = user['is_seller']
                session['is_suspended'] = user['is_suspended']
                flash('Login successful')
                return redirect(url_for('index'))
        else:
            flash('Incorrect code')
            return redirect(url_for('auth.verify_otp'))

    return render_template('verify_otp.html')


@auth.route('/logout')
def logout():
    session.clear()
    flash('You have logged out successfully')
    return redirect(url_for('auth.login'))


@auth.route('/upgrade_to_seller', methods=['POST'])
def uptoseller():
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    conn.execute('UPDATE users SET is_seller = 1 WHERE id = ?', (session['user_id'],))
    conn.commit()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    session['is_seller'] = user['is_seller']
    session['is_admin'] = user['is_admin']
    session['is_suspended'] = user['is_suspended']
    flash('You are now a seller')
    return redirect(url_for('index'))


@auth.route('/revert_to_customer', methods=['POST'])
def revtocustomer():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))
    conn = get_db_connection()
    conn.execute('UPDATE users SET is_seller = 0 WHERE id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    session['is_seller'] = 0
    flash('You have reverted to a normal customer account')
    return redirect(url_for('index'))