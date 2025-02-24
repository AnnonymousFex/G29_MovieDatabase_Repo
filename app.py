import os
from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer  # Import the serializer
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import random
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Allow OAuth to work without HTTPS (Only for local development)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize the serializer
serializer = URLSafeTimedSerializer(app.secret_key)  # Initialize the serializer

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# List of background images stored in the "static" folder
background_images = [
    "bg1.jpg",
    "bg2.jpg",
    "bg3.jpg",
    "bg4.jpg",
    "bg5.jpg",
    "bg6.jpg",
    "bg7.jpg",
    "bg8.jpg"
]

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

# OMDB API key

# Define the Rating model
class Rating(db.Model):
    __tablename__ = "ratings"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_title = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __init__(self, movie_title, rating):
        self.movie_title = movie_title
        self.rating = rating

    def __repr__(self):
        return f"Rating: {self.movie_title}, {self.rating}"

# Create tables if they don't exist
with app.app_context():
    db.create_all()

class User(db.Model, UserMixin):  # Inherit from UserMixin
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)  # Ensure nullable=True

with app.app_context():
    db.create_all()

class MovieVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_title = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<MovieVisit {self.movie_title} by User {self.user_id}>"



# Create the table
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Google OAuth Setup
google_bp = make_google_blueprint(
    client_id= GOOGLE_CLIENT_ID,
    client_secret= GOOGLE_CLIENT_SECRET,
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_to="google_auth"
)
app.register_blueprint(google_bp, url_prefix="/login")

# Facebook OAuth Setup
facebook_bp = make_facebook_blueprint(
    client_id="YOUR_FACEBOOK_CLIENT_ID",
    client_secret="YOUR_FACEBOOK_CLIENT_SECRET",
    scope=["email"],
    redirect_to="facebook_auth"
)
app.register_blueprint(facebook_bp, url_prefix="/login")

@app.route("/")
def home():
    movie_titles = [
        "Squid Game", "Better Call Saul", "The Dark Knight", "Parasite",
        "Rick And Morty", "Forrest Gump", "The Silence of the Lambs", "Star Wars: Episode V - The Empire Strikes",
        "Prison Break", "The Prestige", "Game of Thrones"
    ]

    anime_titles = [
        "Attack on Titan", "Death Note", "Fullmetal Alchemist", "Naruto"
        , "Vinland Saga" , "Mob Psycho 100" , "Bleach" , "Hunter X Hunter" 
        ,"One Piece" , "Parasyte The Maxim" , "Spy x Family" , "Black Clover"
        ,"Chainsawman"
    ]

    movie_titles_2 = [
        "Inception", "The Matrix", "Interstellar", "The Avengers",
        "The Lord of the Rings: The Fellowship of the Ring", "Fight Club",
        "The Social Network", "The Grand Budapest Hotel", "Mad Max: Fury Road",
        "The Revenant", "The Wolf of Wall Street"
    ]
    popular_interest = [
        "Avengers" , "The Conjuring" , "Free Guy", "Dragon Ball" , "Spider Mna into the spider verse" , "Attack On Titan"
        ,"Pokemon" , "Cobra Kai" , "Narcos" ,"Alice In Borderland" ,"Money Heist" , "Stranger Things"

    ]

    explore_streaming = ["Extraction" ,"To All the Boys I've Loved Before" , "The Gray Man" ,"The Power of the Dog"
     ,"Luca" , "Shang-Chi and the Legend of the Ten Rings" , "Avatar: The Way of Water" , "Black Panther: Wakanda Forever"
     "Sound of Metal" ,"Coming 2 America" , "The Big Sick" , "The Batman" , "King Richard" , "Wednesday"

    ]

    def fetch_movie_data(title):
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
        response = requests.get(url).json()
        if response["Response"] == "True":
            return {
                "Title": response.get("Title"),
                "Year": response.get("Year"),
                "imdbRating": response.get("imdbRating"),
                "Poster": response.get("Poster"),
                "Genre": response.get("Genre"),
                "Director": response.get("Director"),
                "Actors": response.get("Actors"),
                "Runtime": response.get("Runtime"),
                "BoxOffice": response.get("BoxOffice", "N/A"),
                "RottenTomatoes": next(
                    (rating["Value"] for rating in response.get("Ratings", []) if rating["Source"] == "Rotten Tomatoes"), 
                    "N/A"
                )
            }
        return None

    movies = [fetch_movie_data(title) for title in movie_titles if fetch_movie_data(title)]
    anime = [fetch_movie_data(title) for title in anime_titles if fetch_movie_data(title)]
    movies_2 = [fetch_movie_data(title) for title in movie_titles_2 if fetch_movie_data(title)]
    popular = [fetch_movie_data(title) for title in popular_interest if fetch_movie_data(title)]
    streaming = [fetch_movie_data(title) for title in explore_streaming if fetch_movie_data(title)]

    return render_template("home.html", movies=movies, movies_2=movies_2 , popular_interest = popular , anime_titles = anime , explore_streaming = streaming)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'videos'), filename)

@app.route("/search")
def search():
    query = request.args.get("q")  # Get the search query from the URL parameters
    if not query:
        return jsonify([])  # Return empty if no query is provided

    # Fetch data from OMDB API
    url = f"http://www.omdbapi.com/?s={query}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()

    if response.get("Response") == "True":
        results = response.get("Search", [])
        return jsonify(results)  # Return the search results as JSON
    else:
        return jsonify([])  # Return empty if no results are found

@app.route("/movie/<title>")
@login_required
def movie_details(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()

    if response["Response"] == "True":
        movie = {
            "Title": response.get("Title"),
            "Year": response.get("Year"),
            "imdbRating": response.get("imdbRating"),
            "Poster": response.get("Poster"),
            "Genre": response.get("Genre"),
            "Director": response.get("Director"),
            "Actors": response.get("Actors"),
            "Runtime": response.get("Runtime"),
            "BoxOffice": response.get("BoxOffice", "N/A"),
            "RottenTomatoes": next(
                (rating["Value"] for rating in response.get("Ratings", []) if rating["Source"] == "Rotten Tomatoes"),
                "N/A"
            ),
            "Plot": response.get("Plot"),
            "Language": response.get("Language"),
            "Country": response.get("Country"),
            "Awards": response.get("Awards"),
            "imdbID": response.get("imdbID")
        }

        # Log the visit in the database
        movie_visit = MovieVisit(user_id=current_user.id, movie_title=title)
        db.session.add(movie_visit)
        db.session.commit()

        # Fetch average rating from the database
        avg_rating = db.session.query(db.func.avg(Rating.rating)).filter(Rating.movie_title == title).scalar()
        average_rating = round(avg_rating, 1) if avg_rating else None

        return render_template("movie_details.html", movie=movie, average_rating=average_rating)

    else:
        return "Movie not found", 404


@app.route("/rate_movie/<title>", methods=["POST"])
def rate_movie(title):
    rating = request.form.get("rating", type=int)

    if rating is None or rating < 0 or rating > 10:
        logging.error("Invalid rating submitted.")
        return "Invalid rating", 400

    # Save the rating to the database
    new_rating = Rating(movie_title=title, rating=rating)
    db.session.add(new_rating)
    try:
        db.session.commit()
        return redirect(url_for('movie_details', title=title))
    except Exception as e:
        logging.error(f"Error while rating movie: {e}")
        db.session.rollback()
        return "An error occurred while saving your rating.", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    selected_bg = random.choice(background_images)  # Pick a random image

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)  # Use Flask-Login to log in the user
            return redirect(url_for('home'))  # Redirect to home page
        else:
            logging.error("Invalid credentials or user not found.")
            return "Invalid credentials or user not found. Please sign up.", 401
    
    return render_template('login.html', bg_image=selected_bg)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    selected_bg = random.choice(background_images)  # Select a random image
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            logging.error("Passwords do not match!")
            return "Passwords do not match!", 400

        hashed_password = generate_password_hash(password)
        
        if User.query.filter_by(email=email).first():
            logging.error("User   already exists!")
            return "User   already exists!", 400

        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        try:
            db.session.commit()
            login_user(new_user)  # Log in the user after signup
            return redirect(url_for('home'))  # Redirect to home page
        except Exception as e:
            logging.error(f"Error during signup: {e}")
            db.session.rollback()
            return "An error occurred. Please try again.", 500
    
    return render_template('signup.html', bg_image=selected_bg)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    selected_bg = random.choice(background_images)  # Pick a random image

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = serializer.dumps(email, salt='password-reset')
            reset_url = url_for('reset_password', token=token, _external=True)
            return f'<p>Click the link to reset your password: <a href="{reset_url}">{reset_url}</a></p>'
        else:
            logging.error("Email not found!")
            return "Email not found!", 400
    
    return render_template('forgot_password.html', bg_image=selected_bg)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    selected_bg = random.choice(background_images)  # Select a random background image
    
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except:
        logging.error("The reset link is invalid or has expired.")
        return "The reset link is invalid or has expired.", 400
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            logging.error("Passwords do not match!")
            return "Passwords do not match!", 400
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(new_password)
            try:
                db.session.commit()
                return redirect(url_for('login'))
            except Exception as e:
                logging.error(f"Error during password reset: {e}")
                db.session.rollback()
                return "An error occurred. Please try again.", 500
        else:
            logging.error("User   not found!")
            return "User   not found!", 400
    
    return render_template('reset_password.html', token=token, bg_image=selected_bg)

@app.route('/google_auth')
def google_auth():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        user_info = resp.json()
        email = user_info.get("email")
        name = user_info.get("name")

        if email:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Create a new user if they don't exist
                default_password = generate_password_hash("defaultpassword123")
                new_user = User(name=name, email=email, password=default_password)
                db.session.add(new_user)
                try:
                    db.session.commit()
                    user = new_user  # Set user to the newly created user
                except Exception as e:
                    logging.error(f"Error during Google OAuth: {e}")
                    db.session.rollback()
                    return "An error occurred. Please try again.", 500
            
            # Log in the user
            login_user(user)  # Use Flask-Login to log in the user
            return redirect(url_for('home')) 

    return "Google login failed", 400

@app.route('/facebook_auth')
def facebook_auth():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))

    resp = facebook.get("/me?fields=id,name,email")
    if resp.ok:
        user_info = resp.json()
        email = user_info.get("email")
        name = user_info.get("name")

        if email:
            user = User.query.filter_by(email=email).first()
            
            if not user:
                default_password = generate_password_hash("defaultpassword123")
                new_user = User(name=name, email=email, password=default_password)
                db.session.add(new_user)
                try:
                    db.session.commit()
                except Exception as e:
                    logging.error(f"Error during Facebook OAuth: {e}")
                    db.session.rollback()
                    return "An error occurred. Please try again.", 500
            
            login_user(user)  # Use Flask-Login to log in the user
            return f"Welcome, {name}!"

    return "Facebook login failed", 400

@app.route('/logout')
def logout():
    logout_user()  # Use Flask-Login to log out the user
    return redirect(url_for('home'))
# @app.route('/profile')
# @login_required  # Ensure the user is logged in
# def profile():
#     user = current_user  # Get the logged-in user
#     return render_template('profile.html', user=user)


# Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Contact {self.name}>'

# Create the database tables
with app.app_context():
    db.create_all()

# Route to handle form submissions
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Store data in the database
        new_contact = Contact(name=name, email=email, subject=subject, message=message)
        db.session.add(new_contact)
        db.session.commit()

        # return flash("Thank You for contacting us")

    return render_template('contact.html')  # Ensure the form is displayed
# @app.route("/movie/<title>", endpoint="movie_details")
@login_required
# def movie_details(title):
#     url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
#     response = requests.get(url).json()

#     if response["Response"] == "True":
#         movie = {
#             "Title": response.get("Title"),
#             "Year": response.get("Year"),
#             "imdbRating": response.get("imdbRating"),
#             "Poster": response.get("Poster"),
#             "Genre": response.get("Genre"),
#             "Director": response.get("Director"),
#             "Actors": response.get("Actors"),
#             "Runtime": response.get("Runtime"),
#             "BoxOffice": response.get("BoxOffice", "N/A"),
#             "RottenTomatoes": next(
#                 (rating["Value"] for rating in response.get("Ratings", []) if rating["Source"] == "Rotten Tomatoes"), 
#                 "N/A"
#             ),
#             "Plot": response.get("Plot"),
#             "Language": response.get("Language"),
#             "Country": response.get("Country"),
#             "Awards": response.get("Awards"),
#             "imdbID": response.get("imdbID")
#         }

#         # Log the movie visit
#         new_visit = MovieVisit(user_id=current_user.id, movie_title=title)
#         db.session.add(new_visit)
#         db.session.commit()

#         # Fetch average rating from the database
#         avg_rating = db.session.query(db.func.avg(Rating.rating)).filter(Rating.movie_title == title).scalar()
#         average_rating = round(avg_rating, 1) if avg_rating else None

#         return render_template("movie_details.html", movie=movie, average_rating=average_rating)
    
#     return "Movie not found", 404


# ...existing code...

@app.route('/profile')
@login_required
def profile():
    user = current_user
    recently_viewed = MovieVisit.query.filter_by(user_id=user.id).order_by(MovieVisit.timestamp.desc()).limit(5).all()
    return render_template('profile.html', user=user, recently_viewed=recently_viewed)

@app.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    user = current_user
    user.name = request.form.get('name')
    user.email = request.form.get('email')
    try:
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating your profile.', 'danger')
    return redirect(url_for('profile'))



    
# Admin Panel Route
@app.route('/admin')
@login_required
def admin_panel():
    if current_user.email != "admin@example.com":  # Change to actual admin email
        flash("Access denied!", "danger")
        return redirect(url_for('home'))

    users = User.query.all()
    ratings = Rating.query.all()
    visits = MovieVisit.query.all()
    contacts = Contact.query.all()
    return render_template('admin.html', users=users, ratings=ratings, visits=visits, contacts=contacts)

# Add a new user
@app.route('/admin/add_user', methods=['POST'])
@login_required
def add_user():
    if current_user.email != "admin@example.com":
        return redirect(url_for('home'))

    name = request.form['name']
    email = request.form['email']
    password = generate_password_hash(request.form['password'])
    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('admin_panel'))

# Delete a user
@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.email != "admin@example.com":
        return redirect(url_for('home'))

    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_panel'))

# Update a user's name or email
@app.route('/admin/update_user/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    if current_user.email != "admin@example.com":
        return redirect(url_for('home'))

    user = User.query.get(user_id)
    user.name = request.form['name']
    user.email = request.form['email']
    db.session.commit()
    return redirect(url_for('admin_panel'))

# Delete a movie rating
@app.route('/admin/delete_rating/<int:rating_id>', methods=['POST'])
@login_required
def delete_rating(rating_id):
    if current_user.email != "admin@example.com":
        return redirect(url_for('home'))

    rating = Rating.query.get(rating_id)
    db.session.delete(rating)
    db.session.commit()
    return redirect(url_for('admin_panel'))

# Delete a movie visit
@app.route('/admin/delete_visit/<int:visit_id>', methods=['POST'])
@login_required
def delete_visit(visit_id):
    if current_user.email != "admin@example.com":
        return redirect(url_for('home'))

    visit = MovieVisit.query.get(visit_id)
    db.session.delete(visit)
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/contact')
@login_required
def admin_contact():
    if current_user.email != "admin@example.com":
        flash("Access Denied!", "danger")
        return redirect(url_for('home'))

    contacts = Contact.query.all()
    return render_template('admin.html', users=users, ratings=ratings, visits=visits, contacts=contacts)


@app.route('/admin/delete_contact/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id):
    if current_user.email != "admin@example.com":
        return redirect(url_for('home'))

    contact = Contact.query.get(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return redirect(url_for('admin_panel'))




    # return render_template('profile.html', user=user, recently_visited=recently_visited)

if __name__ == '__main__':
    app.run(debug=True)