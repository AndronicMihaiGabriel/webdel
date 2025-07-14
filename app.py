from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from database import get_connection
from api import api
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from flask import render_template, redirect, url_for, flash

app = Flask(__name__)
app.register_blueprint(api)
app.secret_key = 'secret_ceva'
bcrypt = Bcrypt(app)
CORS(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, rol):
        self.id = id
        self.username = username
        self.rol = rol

    def get_id(self):
        return self.id


@app.route('/login_web', methods=['GET', 'POST'])
def login_web():

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
    
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                'SELECT * FROM userweb WHERE username = %s', (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
    
            if user and bcrypt.check_password_hash(user['password'], password):
                user_obj = User(user['id'], user['username'], user['rol'])
                login_user(user_obj)
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error="Login greșit")
    


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username, rol=current_user.rol)


@login_manager.user_loader
def load_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM userweb WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['rol'])
    return None


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    rol = data.get('role', 'user')

    if rol not in ['admin', 'user']:
        return jsonify({'error': 'Rolul trebuie să fie "admin" sau "user".'}), 400
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO userweb (username, email, password, rol) VALUES (%s, %s, %s,%s)', (username, email, password, rol))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if not username or not password:
        return jsonify({'error': 'Username și parola sunt obligatorii!'}), 400
    try:
        cursor.execute(
            'SELECT id, username, password, rol FROM userweb WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['username'], user['rol'])
            login_user(user_obj)
            return jsonify({'message': 'Login successful', 'rol': user['rol']}), 200
        else:
            return jsonify({'error': 'Nume sau Parola gresite'}), 401
    finally:
        cursor.close()
        conn.close()


@app.route('/', methods=['GET'])
def me():
    if 'user_id' in session:
        return jsonify({'user_id': session['user_id'], 'rol': session['rol']}), 200
    else:
        return jsonify({'error': 'Not logged in'}), 401


@app.route('/hello')
def hello():
    return "<h1>API Flask funcționează!</h1>"


if __name__ == '__main__':
    app.run(debug=True)
