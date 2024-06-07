from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

movie_api_key="77344cb61719d3572ecb5fa74a680c41"
movie_access_token="eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3NzM0NGNiNjE3MTlkMzU3MmVjYjVmYTc0YTY4MGM0MSIsInN1YiI6IjY2NjMyMGZjNDA1NzMyZjEzYTEzM2VlOCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.5LFEGJRvgBz_FmqYd0aR9AY7YrleXRkFWw4ZSW8huW0"



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///movies.db'
db=SQLAlchemy(model_class=Base)

db.init_app(app)


# CREATE TABLE

class Movie(db.Model):
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    title:Mapped[str]=mapped_column(String(250),nullable=False,unique=True)
    year:Mapped[int]=mapped_column(Integer,nullable=False)
    description:Mapped[str]=mapped_column(String(250),nullable=False)
    rating:Mapped[float]=mapped_column(Float)
    ranking:Mapped[int]=mapped_column(Integer)
    review:Mapped[str]=mapped_column(String(250))
    img_url:Mapped[str]=mapped_column(String(250),nullable=False)
    
with app.app_context():
    db.create_all()
    

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )

# second_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )

# with app.app_context():
#     db.session.add(second_movie)
#     db.session.commit()
    
    
class RatingForm(FlaskForm):
    rating=StringField("Your Rating out of 10 eg 7.5",validators=[DataRequired()])
    review=StringField("Your Review",validators=[DataRequired()])
    submit=SubmitField("submit")
    
class addMovie(FlaskForm):
    title=StringField("Movie Title",validators=[DataRequired()])
    submit=SubmitField("submit")


@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies = result.scalars().all() # convert ScalarResult to Python List
    
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    
    return render_template("index.html",movies=all_movies)

@app.route("/edit",methods=['GET','POST'])

def edit():
    id=int(request.args.get('id'))
    movie=db.session.execute(db.Select(Movie).where(Movie.id==id)).scalar()
    form=RatingForm()
    if form.validate_on_submit():
        rating=form.rating.data
        review=form.review.data
        
        movie=db.session.execute(db.select(Movie).where(Movie.id==id)).scalar()
        movie.rating=rating
        movie.review=review
        db.session.commit()
        
        return redirect("/")
        
    
    return render_template('edit.html',x=movie,form=form)


@app.route("/delete",methods=['GET','POST'])

def delete():
    id=int(request.args.get('id'))
    movie=db.session.execute(db.Select(Movie).where(Movie.id==id)).scalar()
    db.session.delete(movie)
    db.session.commit()
    
    return redirect("/")


@app.route("/add", methods=['GET','POST'])
    
def add():
    form=addMovie()
    if form.validate_on_submit():
        title=form.title.data
        movie_db_search_url="https://api.themoviedb.org/3/search/movie"
        response=requests.get(movie_db_search_url,params={"api_key":movie_api_key,"query":title})
        movies=response.json()["results"]
        
        return render_template("select.html",movies=movies)
        
    
    return render_template("add.html",form=form)

MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
@app.route("/add_to_database")

def add_to_database():
    id=int(request.args.get('id'))
    details=f'https://api.themoviedb.org/3/movie/{id}'
    response=requests.get(details,params={"api_key":movie_api_key,"language": "en-US"})
    data=response.json()
    img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}"
    title=data["title"]
    year=int(data["release_date"].split("-")[0])
    description=data["overview"]
    
    new_movie=Movie(id=id,title=title,img_url=img_url,year=year,description=description)
    db.session.add(new_movie)
    db.session.commit()
    
    movie=db.session.execute(db.Select(Movie).where(Movie.id==id)).scalar()
    form=RatingForm()
    
    return render_template('edit.html',x=movie,form=form)
    
    
    


if __name__ == '__main__':
    app.run(debug=True)
