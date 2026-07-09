from flask import Flask, render_template_string

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>ELibrary Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #ec489a, #db2777);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 { color: #db2777; text-align: center; }
        .books {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .book-card {
            background: #fdf2f8;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            transition: transform 0.3s;
        }
        .book-card:hover { transform: translateY(-5px); }
        button {
            background: #ec489a;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
        }
        @media (max-width: 768px) {
            .books { grid-template-columns: 1fr; }
            .container { padding: 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 ELibraryHub Test Page</h1>
        <p style="text-align: center">If you see pink styling and cards below, CSS is working!</p>
        
        <div class="books">
            <div class="book-card">
                <h3>Sample Book 1</h3>
                <p>This shows CSS is working</p>
                <button>Read Now</button>
            </div>
            <div class="book-card">
                <h3>Sample Book 2</h3>
                <p>Responsive design is active</p>
                <button>Download</button>
            </div>
        </div>
        
        <div style="margin-top: 30px; text-align: center">
            <button onclick="alert('CSS and JavaScript are working!')">Test JavaScript</button>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(debug=True, port=5000)