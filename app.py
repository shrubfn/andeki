from flask import Flask, render_template, request, redirect, url_for, flash, session
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from authservice import create_user, authenticate_user
from animeservice import search_anime


app = Flask(__name__)

#secretkey for sessions and login security
app.config["SECRET_KEY"] = "temp_secret_key"

# sqLite database file
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///andeki.db"

# turn off unnecessary tracking warnings
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ceates the database controller object
db.init_app(app)
from models import User, Anime

#create route and pages
@app.route("/")
def index():
    return render_template("index.html")



@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to view your dashboard.", "error")
        return redirect(url_for("login"))
    
    #find all anime with user id of session id
    anime_list = Anime.query.filter_by(user_id=session["user_id"]).all()

    return render_template("dashboard.html", anime_list=anime_list)



@app.route("/search")
def search():
    if "user_id" not in session:
            flash("Please log in to search anime.", "error")
            return redirect(url_for("login"))

    query = request.args.get("q", "")
    results = []

    if query:
        success, message, results = search_anime(query)

        if not success:
            flash(message, "error")
        elif len(results) == 0:
            flash("No anime results found.", "error")

    return render_template("search.html", query=query, results=results)



@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        flash("You are already logged in.", "error")
        return redirect(url_for("dashboard"))
    else:
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")

            #use register function
            success, message = create_user(username, email, password)

            #flash class for css
            flash(message, "success" if success else "error")

            if success:
                return redirect(url_for("login"))

            return render_template(
                "register.html",
                username=username,
                email=email
            )

        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        flash("You are already logged in.", "error")
        return redirect(url_for("dashboard"))
    else:
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            #use auth function 
            success, message, user = authenticate_user(email, password)

            flash(message, "success" if success else "error")

            if success:
                session["user_id"] = user.id
                session["username"] = user.username
                return redirect(url_for("dashboard"))

            return render_template("login.html", email=email)
        
        return render_template("login.html")


#backend route for library adding
@app.route("/add-to-library", methods=["POST"])
def add_to_library():
    if "user_id" not in session:
        flash("Please log in to add anime to your library.", "error")
        return redirect(url_for("login"))

    mal_id = request.form.get("mal_id")
    title = request.form.get("title")
    image_url = request.form.get("image_url")
    total_episodes = request.form.get("total_episodes")
    genre = request.form.get("genre")
    synopsis = request.form.get("synopsis")
    api_score = request.form.get("api_score")

    existing_anime = Anime.query.filter_by(
        user_id=session["user_id"],
        mal_id=mal_id
    ).first()

    if existing_anime:
        flash("This anime is already in your library.", "error")
        return redirect(request.referrer)

    new_anime = Anime(
        user_id=session["user_id"],
        mal_id=mal_id,
        title=title,
        image_url=image_url,
        total_episodes=total_episodes,
        current_episode=0,
        genre=genre,
        synopsis=synopsis,
        api_score=api_score,
        status="Plan to Watch",
        rating=None,
        notes=""
    )

    db.session.add(new_anime)
    db.session.commit()

    flash(f"{title} added to your library.", "success")
    return redirect(url_for("dashboard"))



#logout route
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


#anime page route
@app.route("/anime/<int:anime_id>")
def anime_detail(anime_id):
    if "user_id" not in session:
        flash("Please log in to view your library.")
        return redirect(url_for("login"))

    anime = Anime.query.filter_by(
        id=anime_id,
        user_id=session["user_id"]
    ).first()

    if anime is None:
        flash("Anime not found.")
        return redirect(url_for("dashboard"))

    return render_template("anime_detail.html", anime=anime)



#adding and decreasing episode
@app.route("/anime/<int:anime_id>/increase", methods=["POST"])
def increase_episode(anime_id):
    if "user_id" not in session:
        flash("Please log in to update your anime.", "error")
        return redirect(url_for("login"))

    anime = Anime.query.filter_by(
        id=anime_id,
        user_id=session["user_id"]
    ).first()

    if anime is None:
        flash("Anime not found.", "error")
        return redirect(url_for("dashboard"))

    # if total episodes is known, do not go past the maximum
    if anime.total_episodes is not None:
        if anime.current_episode < anime.total_episodes:
            anime.current_episode += 1
        else:
            flash("You have already reached the final episode.", "error")
            return redirect(url_for("anime_detail", anime_id=anime.id))

    # Iif total episodes is unknown, allow it to keep increasing
    else:
        anime.current_episode += 1

    db.session.commit()

    flash("Episode progress updated.", "success")
    return redirect(url_for("anime_detail", anime_id=anime.id))


@app.route("/anime/<int:anime_id>/decrease", methods=["POST"])
def decrease_episode(anime_id):
    if "user_id" not in session:
        flash("Please log in to update your anime.", "error")
        return redirect(url_for("login"))

    anime = Anime.query.filter_by(
        id=anime_id,
        user_id=session["user_id"]
    ).first()

    if anime is None:
        flash("Anime not found.", "error")
        return redirect(url_for("dashboard"))

    if anime.current_episode > 0:
        anime.current_episode -= 1
    else:
        flash("Episode progress cannot go below 0.", "error")
        return redirect(url_for("anime_detail", anime_id=anime.id))

    db.session.commit()

    flash("Episode progress updated.", "success")
    return redirect(url_for("anime_detail", anime_id=anime.id))


#deleting anime from library
@app.route("/anime/<int:anime_id>/delete", methods=["POST"])
def delete_anime(anime_id):
    if "user_id" not in session:
        flash("Please log in to delete anime.", "error")
        return redirect(url_for("login"))

    anime = Anime.query.filter_by(
        id=anime_id,
        user_id=session["user_id"]
    ).first()

    if anime is None:
        flash("Anime not found.", "error")
        return redirect(url_for("dashboard"))

    db.session.delete(anime)
    db.session.commit()

    flash("Anime removed from your library.", "success")
    return redirect(url_for("dashboard"))



#route for rating and status
@app.route("/anime/<int:anime_id>/update", methods=["POST"])
def update_anime(anime_id):
    if "user_id" not in session:
        flash("Please log in to update your anime.", "error")
        return redirect(url_for("login"))

    anime = Anime.query.filter_by(
        id=anime_id,
        user_id=session["user_id"]
    ).first()

    if anime is None:
        flash("Anime not found.", "error")
        return redirect(url_for("dashboard"))


    #get values and data from the html req form
    status = request.form.get("status")
    rating = request.form.get("rating")

    allowed_statuses = [
        "Plan to Watch",
        "Watching",
        "Completed",
        "On Hold",
        "Dropped"
    ]

    if status not in allowed_statuses:
        flash("Invalid status selected.", "error")
        return redirect(url_for("anime_detail", anime_id=anime.id))

    anime.status = status


    #error handling, make sure rating and status is correct before changing db and committing
    if rating == "":
        anime.rating = None
    else:
        #try for excpetion handling, prevent crash
        try:
            rating = int(rating)

            if rating < 1 or rating > 10:
                flash("Rating must be between 1 and 10.", "error")
                return redirect(url_for("anime_detail", anime_id=anime.id))

            anime.rating = rating

        #use except to prevent crashing
        except ValueError:
            flash("Rating must be a number.", "error")
            return redirect(url_for("anime_detail", anime_id=anime.id))

    db.session.commit()

    flash("Anime details updated.", "success")
    return redirect(url_for("anime_detail", anime_id=anime.id))



#run website only if app is run
if __name__ == "__main__":
    app.run(debug=True, port=5001)