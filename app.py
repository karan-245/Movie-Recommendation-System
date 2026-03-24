from flask import Flask, render_template, request, redirect, url_for
from models import db, User
from recommender import MovieRecommender

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"  # 🔑 required for session

# ---------------- DATABASE ---------------- #
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

# ---------------- LOGIN MANAGER ---------------- #
login_manager = LoginManager()
login_manager.init_app(app)

# ⭐ IMPORTANT FIX (prevents Unauthorized error)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- LOAD MODEL ---------------- #
model = MovieRecommender(r"C:\Users\karan bhosale\Downloads\movie_dataset.csv")


# ---------------- AUTH ROUTES ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error="User already exists")

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ---------------- MAIN ROUTES ---------------- #

@app.route('/')
@login_required
def home():
    titles = model.get_titles()[:20]
    return render_template('index.html', titles=titles)


@app.route('/recommend', methods=['POST'])
@login_required
def recommend():
    movie = request.form['movie']
    results = model.recommend(movie)

    return render_template('result.html', movie=movie, results=results)


@app.route('/dashboard')
@login_required
def dashboard():
    import pandas as pd

    df = pd.read_csv("movie_dataset.csv")

    # 🔥 FIX: Handle multiple genres properly
    df['genres'] = df['genres'].fillna('')

    all_genres = []
    for g in df['genres']:
        all_genres.extend(g.split())

    # Count genres
    from collections import Counter
    genre_count = Counter(all_genres).most_common(5)

    labels = [g[0] for g in genre_count]
    values = [g[1] for g in genre_count]

    return render_template(
        'dashboard.html',
        labels=labels,
        values=values
    )


# ---------------- INIT DB ---------------- #
with app.app_context():
    db.create_all()


# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)
