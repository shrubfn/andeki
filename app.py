from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db
from werkzeug.security import generate_password_hash


app = Flask(__name__)

#secretkey for sessions and login security
app.config["SECRET_KEY"] = "temp_secret_key"

# sqLite database file
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///andeki.db"

# turn off unnecessary tracking warnings
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ceates the database controller object
db.init_app(app)
from models import User

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



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        #check 4 existing users or email
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already exists.")
            return redirect(url_for("register"))
        
        #hash
        hashed_password = generate_password_hash(password)

        # create new user obj
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )

        #add new user to database
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully. You can now log in.")
        return redirect(url_for("index"))

    return render_template("register.html")



@app.route("/login")
def login():
    return render_template("login.html")

#run website only if app is run
if __name__ == "__main__":
    app.run(debug=True, port=5001)