from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
import os
import bcrypt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )

# --- REGISTRATION ROUTE ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    errors = []
    if request.method == 'GET':
        return render_template('register.html', errors=errors)

    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name.strip():
            errors.append("Name is required")
        if not email.strip():
            errors.append("Email is required")
        if not password:
            errors.append("Password is required")
        if not confirm_password:
            errors.append("Confirm password is required")
        if password and confirm_password and password != confirm_password:
            errors.append("Passwords do not match")

        if errors:
            return render_template('register.html', errors=errors)

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
                (email, name, password_hash)
            )
            connection.commit()
            
            cursor.execute("SELECT user_id, name FROM users WHERE email = %s", (email,))
            new_user = cursor.fetchone()
            session['user_id'] = new_user['user_id']
            session['name'] = new_user['name']
            
            return redirect(url_for('index'))

        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062:
                errors.append("Email Already Exists")
                return render_template('register.html', errors=errors)
            else:
                return "Database error"
        finally:
            connection.close()

# --- LOGIN ROUTE ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    errors = []
    if request.method == 'GET':
        return render_template('login.html', errors=errors)

    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')

        if not email.strip():
            errors.append("Email is required")
        if not password:
            errors.append("Password is required")
        
        if errors:
            return render_template('login.html', errors=errors)

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, name, password_hash FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        connection.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            return redirect(url_for('index'))
        else:
            errors.append("Invalid email or password")
            return render_template('login.html', errors=errors)

# --- LOGOUT ROUTE ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- HOME PAGE / TO-DO LIST ---
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Get all to-dos for this user, newest first
    cursor.execute("SELECT todo_id, title, is_done, created_at FROM todos WHERE user_id = %s ORDER BY todo_id DESC", (user_id,))
    todos = cursor.fetchall()
    connection.close()
    
    return render_template('index.html', name=session['name'], todos=todos, error=None)

# --- ADD TO-DO ---
@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    title = request.form.get('title', '').strip()
    if not title:
        # If empty, go back to list (we should pass an error, but keeping it simple for now)
        return redirect(url_for('index'))
    if len(title) > 200:
        # Too long
        return redirect(url_for('index'))

    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO todos (user_id, title) VALUES (%s, %s)", (user_id, title))
    connection.commit()
    connection.close()
    
    return redirect(url_for('index'))

# --- EDIT TO-DO TITLE ---
@app.route('/edit/<int:todo_id>', methods=['POST'])
def edit(todo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    title = request.form.get('title', '').strip()
    if not title or len(title) > 200:
        return redirect(url_for('index'))

    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor()
    # IMPORTANT: AND user_id = %s prevents users from editing other people's tasks
    cursor.execute("UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s", (title, todo_id, user_id))
    connection.commit()
    connection.close()
    
    return redirect(url_for('index'))

# --- MARK DONE / NOT DONE ---
@app.route('/done/<int:todo_id>', methods=['POST'])
def done(todo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Find the current status
    cursor.execute("SELECT is_done FROM todos WHERE todo_id = %s AND user_id = %s", (todo_id, user_id))
    todo = cursor.fetchone()
    
    if todo:
        # Toggle the status: if 1 make it 0, if 0 make it 1
        new_status = 0 if todo['is_done'] == 1 else 1
        cursor.execute("UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s", (new_status, todo_id, user_id))
        connection.commit()
        
    connection.close()
    return redirect(url_for('index'))

# --- DELETE TO-DO ---
@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete(todo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor()
    # IMPORTANT: AND user_id = %s prevents users from deleting other people's tasks
    cursor.execute("DELETE FROM todos WHERE todo_id = %s AND user_id = %s", (todo_id, user_id))
    connection.commit()
    connection.close()
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)