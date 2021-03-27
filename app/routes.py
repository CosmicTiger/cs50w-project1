from flask import render_template, flash, redirect, url_for, session, request
from flask_login import current_user, login_user

from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, db
from app.forms import LoginForm
from app.helpers import login_required

@app.route('/')
@app.route('/index')
@login_required
def index():
    """ Show home with search box """
    return render_template('index.html', title='Home', user=session.get("username"))

@app.route("/search", methods=["GET"])
@login_required
def search():
    """ Fetch all books """
    book_request = request.args.get("book")

    # if a book request was not provided, it will fail
    if not book_request:
        return render_template("error.html", message="you must provide a book.", code=400)

    # parse the input and prepare it for the querying
    query = "%" + book_request + "%"

    query = query.title()

    rows = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn LIKE :query OR title LIKE :query OR author LIKE :query LIMIT 20",
                        { "query": query }
                    )
    # if any book wasn't found
    if rows.rowcount == 0:
        return render_template("error.html", message="We can't find books with that description", code=500)

    # fetch all results
    books = rows.fetchall()

    return render_template("index.html", title="Home - Books Results", user=session.get("username"), books=books)

@app.route("/book/<isbn>", methods=['GET', 'POST'])
@login_required
def book(isbn):
    """ Save users review and load same page with reviews updated. """

    if request.method == "POST":

        # Save current user info
        current_user = session["user_id"]

        # Fetch form data
        rating = request.form.get("rating")
        comment = request.form.get("comment")

        # Search id_book by ISBN
        row = db.execute("SELECT id_book FROM books WHERE isbn = :isbn",
                            { "isbn": isbn })

        # Save id into a variable
        book_parsing = row.fetchone()
        book = book_parsing[0]

        # Check for user submission (ONLY 1 review(rates) user is allowed for books)
        row2 = db.execute("SELECT * from rates WHERE id_user = :id_user AND id_book = :id_book",
                            {
                                "id_user": current_user,
                                "id_book": book
                            }
                        )

        if row2.rowcount == 1:
            flash('You already submitted a review for this book', 'warning')
            return redirect("/book/"+ isbn)

        # Convert rating to save the registry
        rating = int(rating)

        db.execute("INSERT INTO rates (id_user, id_book, comment, rating) VALUES (:id_user, :id_book, :comment, :rating)",
                        {
                            "id_user": current_user,
                            "id_book": book,
                            "comment": comment,
                            "rating": rating
                        }
                    )
        db.commit()

        flash('Review has been submitted!', 'info')
        return redirect("/book/"+isbn)

    # If is a GET method then it will take the book with its ISBN an redirect to the page
    else:

        row = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn",
                            {
                                "isbn": isbn
                            }
                        )

        book_info = row.fetchall()

        """ User's review """
        # Search id_books by ISBN
        row = db.execute("SELECT id_book FROM books WHERE isbn = :isbn",
                            {
                                "isbn": isbn
                            }
                        )

        # Save the id into a variable
        parsed_book = row.fetchone()
        book = parsed_book[0]

        # Fetch all reviews for that book
        results = db.execute("SELECT users.username, comment, rating, to_char(published_time, 'DD Mon YY - HH24:MI:SS') as time FROM users INNER JOIN rates ON users.id_user = rates.id_user WHERE id_book = :book ORDER BY time",
                                {
                                    "book": book
                                }
                            )
        rates = results.fetchall()

        return render_template("book.html", title=book_info[0]['title'], book=book_info, rates=rates)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    username = request.form.get("username")
    password = request.form.get("password")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not username:
            return render_template("error.html", message="must provide username", code=400)

        # Ensure password was submitted
        elif not password:
            return render_template("error.html", message="must provide password", code=400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          { "username": username })

        result = rows.fetchone()

        # Ensure username exists and password is correct
        if result == None or not check_password_hash(result[2], password):
            return render_template("error.html", message="invalid username and/or password", code=400)

        # Remember which user has logged in
        session["user_id"] = result[0]
        session["username"] = result[1]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", title="Sign In")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # forget any user_id just in case
    session.clear()

    # waiting for the values that were inserted
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username", code=400)

        # Querying database for username availability
        checking_user = db.execute("SELECT * FROM users WHERE username = :username",
                                    { "username": request.form.get("username")}).fetchone()

        # Confirming if the username already exists
        if checking_user:
            return render_template("error.html", message="username already exists", code=400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password", code=400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return render_template("error.html", message="must provide confirmation", code=400)

        # Ensure password and confirmation are equals
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("error.html", message="passwords didn't match", code=400)

        # Ensure email was submitted
        elif not request.form.get("email"):
            return render_template("error.html", message="must provide email", code=400)

        # Create instance of the username for best practices
        usernameForm = request.form.get("username")
        emailForm = request.form.get("email")

        # Generate the hash encryption for the password formulated
        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        # Creates the new user which is going to enter at the database
        db.execute("INSERT INTO users (username, hash, email) VALUES (:username, :hash, :email)",
                            {
                                "username": usernameForm,
                                    "hash": hashedPassword,
                                    "email": emailForm
                            })

        # Commit the changes to the database
        db.commit()

        # displaying a flash message
        flash("You've been registered succesfully!", 'info')

        # user is redirected to home because of his first login after registration
        return redirect("/login")
    else:
        return render_template("register.html", title="Sign Up")


