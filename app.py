from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Decorator to ensure the user is logged in
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        # Fetch the hashed password from the database
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hash_password(password))).fetchone()
        conn.close()
        if user:
            session['username'] = user['username']
            session['user'] = user['username']  # Assuming 'username' is the displayed name
            return redirect(url_for('after_login'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/after-login')
@login_required
def after_login():
    user_name = session.get('user')
    return render_template('after_login.html', user=user_name)

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    session.pop('user', None)
    return redirect(url_for('login'))

# Account route to change username and password
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user_name = session.get('username')
    if request.method == 'POST':
        new_username = request.form['new_username']
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (user_name,)).fetchone()

        # Check if the current password is correct
        if user and hash_password(current_password) == user['password']:
            # Check if new password and confirm password match
            if new_password == confirm_password:
                # Update username and password in the database
                conn.execute('UPDATE users SET username = ?, password = ? WHERE username = ?', 
                             (new_username, hash_password(new_password), user_name))
                conn.commit()
                conn.close()

                # Update session variables
                session['username'] = new_username

                flash('Account details updated successfully!', 'success')
                return redirect(url_for('account'))
            else:
                flash('New passwords do not match!', 'error')
        else:
            flash('Current password is incorrect!', 'error')
        conn.close()
    return render_template('account.html', username=user_name)

# Programs route (example page)
@app.route('/programs')
@login_required
def programs():
    return render_template('programs.html')

# Contact route (example page)
@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

# Google Drive page link (example)
@app.route('/drive')
@login_required
def drive():
    return redirect("https://drive.google.com/drive/folders/YOUR_FOLDER_ID", code=302)

if __name__ == '__main__':
    app.run(debug=True)
