from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from models import db, User

app = Flask(__name__)
app.secret_key = 'supersecrettestkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    logged_in = 'user_id' in session
    return render_template('index.html', logged_in=logged_in)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        if not all([username, password, email]):
            flash("All fields are required.")
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash("Username already taken.")
            return render_template('register.html')

        user = User(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('profile'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('profile'))
        flash("Invalid username or password.")
    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('login'))

    if request.method == 'POST':
        user.email = request.form.get('email', user.email)
        db.session.commit()
        flash("Profile updated.")
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data or not all(k in data for k in ("username", "password", "email")):
        return jsonify({"error": "Missing fields"}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already taken"}), 400
    user = User(username=data['username'], password=data['password'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    return jsonify({"message": "User registered"}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or not all(k in data for k in ("username", "password")):
        return jsonify({"error": "Missing fields"}), 400
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    session['user_id'] = user.id
    return jsonify({"message": "Logged in"}), 200

@app.route('/api/profile', methods=['GET'])
def api_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200

@app.route('/api/profile', methods=['PUT'])
def api_update_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    if 'email' in data:
        user.email = data['email']
    db.session.commit()
    return jsonify(user.to_dict()), 200

@app.route('/api/reset', methods=['POST'])
def api_reset():
    db.drop_all()
    db.create_all()
    session.clear()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, port=5000)