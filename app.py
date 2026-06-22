from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#secretkey for sessions and login security
app.config["secret_key"] = "temp_secret_key"

# sqLite database file
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///andeki.db"

# turn off unnecessary tracking warnings
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ceates the database controller object
db = SQLAlchemy(app)

#create route and pages
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

#run website only if app is run
if __name__ == "__main__":
    app.run(debug=True, port=5001)