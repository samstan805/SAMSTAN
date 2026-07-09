# app.py
import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
@app.route('/test-css')
def test_css():
    return '<link rel="stylesheet" href="{{ url_for("static", filename="css/style.css") }}"><h1>CSS Test</h1><p>If you see styling, CSS works!</p>'  
app.secret_key = 'your_secret_key_here_change_in_production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt', 'epub'}
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        profile_pic TEXT DEFAULT 'default.png',
        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        description TEXT,
        category TEXT DEFAULT 'General',
        uploaded_by INTEGER,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        download_count INTEGER DEFAULT 0,
        view_count INTEGER DEFAULT 0,
        FOREIGN KEY (uploaded_by) REFERENCES users (id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (book_id) REFERENCES books (id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        book_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute("SELECT * FROM users")
    if not c.fetchone():
        default_password = generate_password_hash("admin123")
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                  ("Admin User", "admin@elib.com", default_password, "Admin"))
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                  ("Sarah Johnson", "librarian@elib.com", generate_password_hash("lib123"), "Librarian"))
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                  ("Mike Chen", "student@elib.com", generate_password_hash("student123"), "Student"))
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                  ("Emma Watson", "emma@elib.com", generate_password_hash("reader123"), "Student"))
    conn.commit()
    
    c.execute("SELECT COUNT(*) FROM books")
    if c.fetchone()[0] == 0:
        sample_books = [
            ("The Great Gatsby", "F. Scott Fitzgerald", "sample.pdf", "pdf", "A classic novel set in the Jazz Age", "Fiction"),
            ("Python Programming", "John Doe", "sample2.pdf", "pdf", "Learn Python from scratch", "Technology"),
            ("Design Patterns", "Eric Gamma", "sample3.pdf", "pdf", "Elements of Reusable Object-Oriented Software", "Programming"),
            ("The Art of War", "Sun Tzu", "sample4.txt", "txt", "Ancient Chinese military treatise", "Philosophy")
        ]
        for book in sample_books:
            c.execute("INSERT INTO books (title, author, filename, file_type, description, category) VALUES (?,?,?,?,?,?)", book)
    conn.commit()
    conn.close()

init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                flash('Access denied! Insufficient permissions.', 'error')
                return redirect(url_for('dashboard_redirect'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND role = ?", (email, role))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['role'] = user[4]
            session['email'] = user[2]
            flash(f'Welcome back, {user[1]}!', 'success')
            return redirect(url_for('dashboard_redirect'))
        else:
            flash('Invalid email, password, or role combination!', 'error')
            return render_template('login.html', recovery_email=email)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        hashed_password = generate_password_hash(password)
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                      (name, email, hashed_password, role))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()
        if user:
            flash(f'Password reset link sent to {email}! Check your inbox.', 'success')
        else:
            flash('Email not found! Please register first.', 'error')
        return render_template('forgot_password.html', submitted=True)
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard_redirect')
def dashboard_redirect():
    role = session.get('role')
    if role == 'Admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'Librarian':
        return redirect(url_for('librarian_dashboard'))
    elif role == 'Student':
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
@role_required('Admin')
def admin_dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books ORDER BY id DESC")
    books = c.fetchall()
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM books")
    book_count = c.fetchone()[0]
    c.execute("SELECT SUM(download_count) FROM books")
    total_downloads = c.fetchone()[0] or 0
    c.execute("SELECT category, COUNT(*) FROM books GROUP BY category")
    categories = c.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', books=books, user_count=user_count, 
                         book_count=book_count, total_downloads=total_downloads, categories=categories)

@app.route('/librarian')
@login_required
@role_required('Librarian')
def librarian_dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books ORDER BY id DESC")
    books = c.fetchall()
    c.execute("SELECT category, COUNT(*) FROM books GROUP BY category")
    categories = c.fetchall()
    conn.close()
    return render_template('librarian_dashboard.html', books=books, categories=categories)

@app.route('/student')
@login_required
@role_required('Student')
def student_dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books ORDER BY id DESC")
    books = c.fetchall()
    c.execute("SELECT book_id FROM favorites WHERE user_id = ?", (session['user_id'],))
    favorites = [row[0] for row in c.fetchall()]
    conn.close()
    return render_template('student_dashboard.html', books=books, favorites=favorites)

@app.route('/upload_book', methods=['POST'])
@login_required
@role_required('Admin', 'Librarian')
def upload_book():
    title = request.form['title']
    author = request.form['author']
    description = request.form.get('description', '')
    category = request.form.get('category', 'General')
    
    if 'file' not in request.files:
        flash('No file selected!', 'error')
        return redirect(url_for('admin_dashboard' if session['role'] == 'Admin' else 'librarian_dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('admin_dashboard' if session['role'] == 'Admin' else 'librarian_dashboard'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_type = filename.rsplit('.', 1)[1].lower()
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO books (title, author, filename, file_type, description, category, uploaded_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (title, author, filename, file_type, description, category, session['user_id']))
        conn.commit()
        conn.close()
        flash('Book uploaded successfully!', 'success')
    else:
        flash('Invalid file type! Allowed: PDF, DOCX, TXT, EPUB', 'error')
    
    return redirect(url_for('admin_dashboard' if session['role'] == 'Admin' else 'librarian_dashboard'))

@app.route('/read_book/<int:book_id>')
@login_required
def read_book(book_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = c.fetchone()
    if not book:
        flash('Book not found!', 'error')
        return redirect(url_for('dashboard_redirect'))
    
    # Increment view count
    c.execute("UPDATE books SET view_count = view_count + 1 WHERE id = ?", (book_id,))
    c.execute("INSERT INTO activity_logs (user_id, action, book_id) VALUES (?, ?, ?)",
              (session['user_id'], 'view', book_id))
    conn.commit()
    conn.close()
    
    file_url = url_for('static', filename=f'uploads/{book[3]}')
    return render_template('reader.html', book=book, file_url=file_url)

@app.route('/download/<int:book_id>')
@login_required
def download_file(book_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT filename FROM books WHERE id = ?", (book_id,))
    book = c.fetchone()
    if book:
        c.execute("UPDATE books SET download_count = download_count + 1 WHERE id = ?", (book_id,))
        c.execute("INSERT INTO activity_logs (user_id, action, book_id) VALUES (?, ?, ?)",
                  (session['user_id'], 'download', book_id))
        conn.commit()
        conn.close()
        return send_from_directory(app.config['UPLOAD_FOLDER'], book[0], as_attachment=True)
    conn.close()
    flash('Book not found!', 'error')
    return redirect(url_for('dashboard_redirect'))

@app.route('/favorite/<int:book_id>')
@login_required
def toggle_favorite(book_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM favorites WHERE user_id = ? AND book_id = ?", (session['user_id'], book_id))
    favorite = c.fetchone()
    
    if favorite:
        c.execute("DELETE FROM favorites WHERE user_id = ? AND book_id = ?", (session['user_id'], book_id))
        flash('Removed from favorites!', 'info')
    else:
        c.execute("INSERT INTO favorites (user_id, book_id) VALUES (?, ?)", (session['user_id'], book_id))
        flash('Added to favorites!', 'success')
    
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('dashboard_redirect'))

@app.route('/my_favorites')
@login_required
@role_required('Student')
def my_favorites():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""SELECT b.* FROM books b 
                 JOIN favorites f ON b.id = f.book_id 
                 WHERE f.user_id = ? ORDER BY b.title""", (session['user_id'],))
    books = c.fetchall()
    conn.close()
    return render_template('student_dashboard.html', books=books, favorites=[b[0] for b in books], show_favorites=True)

@app.route('/search_books', methods=['GET'])
@login_required
def search_books():
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if category:
        c.execute("SELECT * FROM books WHERE (title LIKE ? OR author LIKE ?) AND category = ? ORDER BY id DESC",
                  (f'%{query}%', f'%{query}%', category))
    else:
        c.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY id DESC",
                  (f'%{query}%', f'%{query}%'))
    
    books = c.fetchall()
    conn.close()
    
    role = session.get('role')
    if role == 'Admin':
        return render_template('admin_dashboard.html', books=books, search_query=query, selected_category=category)
    elif role == 'Librarian':
        return render_template('librarian_dashboard.html', books=books, search_query=query, selected_category=category)
    else:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT book_id FROM favorites WHERE user_id = ?", (session['user_id'],))
        favorites = [row[0] for row in c.fetchall()]
        conn.close()
        return render_template('student_dashboard.html', books=books, favorites=favorites, search_query=query, selected_category=category)

@app.route('/manage_users')
@login_required
@role_required('Admin')
def manage_users():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, name, email, role, join_date FROM users")
    users = c.fetchall()
    conn.close()
    return render_template('manage_users.html', users=users)

@app.route('/delete_user/<int:user_id>')
@login_required
@role_required('Admin')
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('manage_users'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/delete_book/<int:book_id>')
@login_required
@role_required('Admin', 'Librarian')
def delete_book(book_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT filename FROM books WHERE id = ?", (book_id,))
    book = c.fetchone()
    if book:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], book[0])
        if os.path.exists(file_path):
            os.remove(file_path)
        c.execute("DELETE FROM books WHERE id = ?", (book_id,))
        c.execute("DELETE FROM favorites WHERE book_id = ?", (book_id,))
        conn.commit()
        flash('Book deleted successfully!', 'success')
    conn.close()
    return redirect(url_for('admin_dashboard' if session['role'] == 'Admin' else 'librarian_dashboard'))

@app.route('/statistics')
@login_required
@role_required('Admin')
def statistics():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM books")
    total_books = c.fetchone()[0]
    c.execute("SELECT SUM(download_count) FROM books")
    total_downloads = c.fetchone()[0] or 0
    c.execute("SELECT SUM(view_count) FROM books")
    total_views = c.fetchone()[0] or 0
    c.execute("SELECT name, download_count FROM books ORDER BY download_count DESC LIMIT 5")
    popular_books = c.fetchall()
    conn.close()
    return jsonify({
        'total_users': total_users,
        'total_books': total_books,
        'total_downloads': total_downloads,
        'total_views': total_views,
        'popular_books': [{'title': b[0], 'downloads': b[1]} for b in popular_books]
    })

@app.route('/recommendations')
@login_required
@role_required('Student')
def recommendations():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Simple recommendation: popular books that user hasn't favorited
    c.execute("""SELECT b.*, b.download_count FROM books b 
                 WHERE b.id NOT IN (SELECT book_id FROM favorites WHERE user_id = ?)
                 ORDER BY b.download_count DESC LIMIT 6""", (session['user_id'],))
    recommendations = c.fetchall()
    conn.close()
    return render_template('student_dashboard.html', books=recommendations, favorites=[], recommendations_mode=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)