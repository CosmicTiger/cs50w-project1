from app import app

@app.route("/")
@app.route('/home')
def index():
    return "Project 1: TODO"
