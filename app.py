from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

# Folder where HTML files are located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_user_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    if 'username' in session:
        return redirect('/landing.html')
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = hash_password(data.get("password"))

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['username'] = username
        return jsonify({"message": "Login successful!"})
    else:
        return jsonify({"message": "Invalid username or password!"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = hash_password(data.get("password"))

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"message": "Username already exists!"}), 400

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return jsonify({"message": "User registered successfully!"})

@app.route('/landing.html')
def landing():
    if 'username' not in session:
        return redirect('/')
    return send_from_directory(BASE_DIR, 'landing.html')

@app.route('/register.html')
def register_page():
    return send_from_directory(BASE_DIR, 'register.html')

@app.route('/get-username')
def get_username():
    if 'username' in session:
        return jsonify({"username": session['username']})
    return jsonify({"username": "Guest"})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == "__main__":
    create_user_table()
    app.run(debug=True)
