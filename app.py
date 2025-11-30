from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from auth_routes import auth
from admin_routes import admin
from reviews_routes import reviews
from db import get_db_connection, close_db_connection

app = Flask(__name__)
app.secret_key = "a3f9d7c1b2e4f8a9c0d1e2f3a4b5c6d7"

csrf = CSRFProtect(app)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE= False 
)

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(reviews, url_prefix='')

@app.teardown_appcontext
def teardown_db(exception):
    close_db_connection()

@app.after_request
def addsechead(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net; "
        "style-src 'self' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none';"
    )
    return response

@app.route('/')
def index():
    conn = get_db_connection()
    try:
        products = conn.execute('SELECT * FROM products').fetchall()
    finally:
        conn.close()
    return render_template('index.html', products=products)

@app.errorhandler(400)
def csrferr(e):
    return "possible CSRF token issue.", 400

if __name__ == '__main__':
    app.run(debug=False)