from extensions import db

#create user datatable, every field is necessary
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    #lets user objects have many relations to 
    anime_list = db.relationship("Anime", backref="user", lazy=True)


#create anime datatable
class Anime(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    mal_id = db.Column(db.Integer)
    title = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500))
    total_episodes = db.Column(db.Integer)
    current_episode = db.Column(db.Integer, default=0)
    api_score = db.Column(db.Float)
    genre = db.Column(db.String(100))
    synopsis = db.Column(db.Text)

    status = db.Column(db.String(50), default="Plan to Watch")
    rating = db.Column(db.Integer)
    notes = db.Column(db.Text)

