import os
import requests

# apikey = "08RobCaWGfWv8ABg0tHk3Q"
apikey = os.getenv("GOODREADS_API")

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["POST", "GET"])
def index():
    if session.get("user") == None:
        return redirect(url_for('login'))
    if request.method == "GET":
        books = db.execute("SELECT * FROM books LIMIT 50")
        return render_template("index.html", user=session["user"], books=books)
    elif request.method == "POST":
        title = "%{}%".format(request.form.get('title'))
        author = "%{}%".format(request.form.get('author'))
        isbn = "%{}%".format(request.form.get('isbn'))
        books = db.execute("SELECT * FROM books WHERE (title ILIKE :title AND author ILIKE :author AND isbn ILIKE :isbn) LIMIT 50", {'title':title, 'author':author, 'isbn':isbn}).fetchall()
        return render_template("index.html", user=session["user"], books=books)

@app.route("/<isbn>", methods=["POST", "GET"])
def book(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": apikey, "isbns": isbn})
    data = res.json()
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {'isbn':isbn}).fetchone()
    if request.method == "POST":
        rating = request.form.get("rating")
        review = request.form.get("review")
        db.execute("INSERT INTO reviews (rating, review, book_isbn, user_id) VALUES (:rating, :review, :book_isbn, :user_id)", {'rating':rating, 'review':review, 'book_isbn':isbn, 'user_id':session["user"].id})
        db.commit()
    user_review = db.execute("SELECT * FROM reviews WHERE user_id = :id AND book_isbn = :isbn", {'isbn':isbn, 'id':session["user"].id}).fetchone()
    reviews = db.execute("SELECT * FROM reviews JOIN users ON reviews.user_id = users.id WHERE user_id != :id AND book_isbn = :isbn", {'isbn':isbn, 'id':session["user"].id}).fetchall()
    if user_review == None:
        return render_template("book.html", user=session["user"], book=book, rating=data["books"][0]["average_rating"], rating_count=data["books"][0]['work_ratings_count'], isReviewed=False, user_review=user_review, reviews=reviews)
    else:
        return render_template("book.html", user=session["user"], book=book, rating=data["books"][0]["average_rating"], rating_count=data["books"][0]['work_ratings_count'], isReviewed=True, user_review=user_review, reviews=reviews)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.execute("SELECT * FROM users WHERE username = :username", {'username':username}).fetchone()
        if user == None or user.password != password:
            return render_template("login.html", isFirst=False, isUser=False)
        else:
            session["user"] = user
            return redirect(url_for("index"))
    elif request.method == "GET":
        if session.get("user") != None:
            session.pop("user") 
    return render_template("login.html", isFirst=True, isUser=True)

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "" or password == "":
            return render_template("register.html", isFirst=False, isNew=True)
        user = db.execute("SELECT * FROM users WHERE username = :username", {'username':username}).fetchone()
        if user == None:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {'username':username, 'password':password})
            db.commit()
            return redirect(url_for('login'))
        else:
            return render_template("register.html", isFirst=True, isNew=False)
    return render_template("register.html", isFirst=True, isNew=True)

@app.route("/api/<isbn>")
def flight_api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {'isbn':isbn}).fetchone()
    review_count = db.execute("SELECT COUNT(*) FROM reviews WHERE book_isbn = :isbn", {'isbn':isbn}).scalar()
    average_score = float(db.execute("SELECT AVG(rating) FROM reviews WHERE book_isbn = :isbn", {'isbn':isbn}).scalar())
    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 404

    return jsonify(
        {
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": isbn,
            "review_count": review_count,
            "average_score": average_score
        })