from flask import render_template
from app import app

@app.route("/")
@app.route('/home')
def index():
    user = { 'username': 'CosmicTiger' }
    books = [
        {
            "title": "Memory",
            "author": "Doug Lloyd",
            "year": 2015,
            "isbn": "1632168146",
            "review_count": 28,
            "average_score": 5.0
        },
        {
            "title": "Memory2",
            "author": "Doug Lloyd",
            "year": 2015,
            "isbn": "1632168146",
            "review_count": 28,
            "average_score": 5.0
        },
        {
            "title": "Memory3",
            "author": "Doug Lloyd",
            "year": 2015,
            "isbn": "1632168146",
            "review_count": 28,
            "average_score": 5.0
        },
    ]
    return render_template('index.html', title='Home', user=user, books=books)
