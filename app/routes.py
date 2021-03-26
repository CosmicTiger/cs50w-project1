from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
                form.username.data, form.remember_me.data
            ))
        return redirect(url_form('index'))
    return render_template('login.html', title='Sign In', form=form)
