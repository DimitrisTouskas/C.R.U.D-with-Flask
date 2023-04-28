from crypt import methods
from tkinter import E
from flask import Flask, render_template,request,redirect,session,url_for ,g
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
from flask_wtf import FlaskForm
from sqlalchemy.orm import backref, query
from sqlalchemy.orm.session import Session,sql
from sqlalchemy.sql.schema import ForeignKey
from wtforms import StringField , PasswordField
from wtforms.validators import InputRequired , Email
from wtforms.widgets.core import Select
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import os
from sqlalchemy import or_

baseDir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this is a sercret key'

#Δηλωση βασης δεδομενων
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///post.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(baseDir, 'post.db')
DATABASE = 'post.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
connection = sqlite3.connect('post.db', check_same_thread=False)
cursor = connection.cursor()


def get_db():
  db = getattr(g, 'posts', None)
  if db is None:
    db = g.posts = sqlite3.connect(DATABASE)
  return db

@app.route("/logout")
def logout():
  session.pop('id',None)
  return redirect("/login")


  

class Students(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    Onoma = db.Column(db.String(20), nullable=False)
    Epitheto = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(200), nullable=False)
    dieuthinsi = db.Column(db.Text(200), nullable= False , default="N/A")
    Phone = db.Column(db.Integer(), nullable = False , default= 'N/A')
    eksamino = db.Column(db.Integer(), nullable = False)
    A_M = db.Column(db.String(10), nullable = False)

    def __init__(self,Onoma,Epitheto,Email,dieuthinsi,Phone,eksamino,A_M):
      self.Onoma = Onoma
      self.Epitheto = Epitheto
      self.Email = Email
      self.dieuthinsi = dieuthinsi
      self.Phone = Phone
      self.eksamino = eksamino
      self.A_M = A_M

#Δημιουργια της βασης δεδομενων για τους χρηστες.
class Users (db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer , primary_key=True)
  name = db.Column(db.String(20), nullable=False)
  lastname = db.Column(db.String(20),nullable = False)
  email = db.Column(db.String(100), nullable = False)
  password = db.Column(db.String(20), nullable = False)
  user_posts = db.relationship('BlogPost', backref = 'poster')

  def __init__(self,name,lastname,email,password):
      self.name = name
      self.lastname = lastname
      self.email = email
      self.password = password      

class BlogPost(db.Model):
  __tablename__ = 'blogpost'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  content = db.Column(db.Text , nullable=False)
  tag = db.Column(db.String(20) , nullable=False, default='N/A' )
  date_posted= db.Column(db.DateTime, nullable=False, default = datetime.utcnow )
  user_id = db.Column(db.Integer,db.ForeignKey('users.id'))

  def __init__(self,title,content,tag,user_id):
    self.title = title
    self.content = content
    self.tag = tag    
    self.user_id = user_id

handler_id = db.Column(db.Integer ,nullable= False)
def __repr__(self):
  return 'Blog Post ' + str(self.id)




#δηλωση route αρχικης
@app.route('/')
def index():
  return render_template('index.html')

#αρχικοποιηση σελιδας για την εμφανιση των σημειωσεων
@app.route('/posts' , methods = ['GET', 'POST'])
def posts():
  if "id" in session:
    if request.method == 'POST': 
      post_title = request.form['title']
      post_content = request.form['content']
      post_tag = request.form['tag']
      new_post = BlogPost(title=post_title, content=post_content, tag= post_tag, user_id = session['id'])
      db.session.add(new_post)
      db.session.commit()
      return redirect('/posts')
    else:
      all_posts = BlogPost.query.order_by(BlogPost.date_posted).filter_by(user_id = session['id']).all()
      return render_template('posts.html', posts= all_posts)
  else:
    return redirect("/login")

#κουμπι delete
@app.route('/posts/delete/<int:id>')
def delete(id):
  post= BlogPost.query.get_or_404(id)
  db.session.delete(post)
  db.session.commit()
  return redirect('/posts')



#κουμπι edit
@app.route('/posts/edit/<int:id>', methods = ["GET","POST"])
def edit(id):
  
  post= BlogPost.query.get_or_404(id)

  if request.method=="POST":
    post.title = request.form['title']
    post.tag = request.form['tag']
    post.content = request.form['content']
    db.session.commit()
    return redirect('/posts')
  else:
    return render_template('edit.html' , post = post)

#πρεπει να δω αν θα κανω τελικα προφιλ και αν ναι τι θα περιεχει... ???  
@app.route('/profile')
def profile():
    return 'Profile'


class LoginForm(FlaskForm):
  email = StringField('email' , validators=[InputRequired(message='Email is required')])
  password = PasswordField('password', validators=[InputRequired(message='Password is required')])

@app.route('/login', methods = ["POST", "GET"])
def login():
  login = LoginForm()
  if login.validate_on_submit():
    user = Users.query.filter_by(email = login.email.data).first()
    if user:
      if user.password == login.password.data:
        user_id_log = user.id
        session["id"] = user_id_log
        return redirect (url_for('foitites'))
    return  redirect("/login")
  return render_template('login.html', login=login)


@app.route('/signup' , methods = ["POST","GET"])
def signup():
    error = None
    if request.method == 'POST':
      user_name = request.form['name']
      user_lastname = request.form['lastname']
      user_email= request.form['email']
      user_password= request.form['password']
      user_password_conf = request.form['password_conf']
      if (user_password==user_password_conf ):
        new_user = Users(name = user_name, lastname = user_lastname, email= user_email, password= user_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect ("/login")
      else:
        error ="Email addresses did not match."
        return render_template("signup.html", error=error)
    return render_template("signup.html")


# σελιδα καταλογου φοιτητων
@app.route('/foitites' , methods = ['GET', 'POST'])
def foitites():
    rows = Students.query.all()
    return render_template('foitites.html', rows = rows)

@app.route('/search', methods = ['GET', 'POST'])
def search():
    
    search = request.form.get('search')
    
    rows = Students.query.filter(
    or_(
      Students.Onoma==search,
      Students.Epitheto==search,
      Students.Email== search,
      Students.dieuthinsi== search,
      Students.Phone== search,
      Students.eksamino == search,
      Students.A_M== search
    )
    )

    rows1 = BlogPost.query.filter(
    or_(
      BlogPost.title==search,
      BlogPost.content==search,
      BlogPost.tag== search
    )
    )
    
      
    #rows1 = BlogPost.query.filter(BlogPost.title==search or BlogPost.content== search or BlogPost.tag== search).all()
    return render_template('search.html', rows= rows, rows1= rows1)



@app.route('/addStudents',methods = [ 'GET' , 'POST'  ] )
def addStudents():
  if request.method =='POST':
    student_name = request.form ['name']
    student_lastname = request.form ['lastname']
    student_email = request.form['email']
    student_address = request.form['dieuthinsi']
    student_phone = request.form['Phone']
    student_eksamino = request.form ['eksamino']
    student_A_M = request.form ['A_M']
    new_student = Students(Onoma= student_name, Epitheto=student_lastname, Email=student_email , dieuthinsi= student_address, Phone=student_phone, eksamino= student_eksamino, A_M=student_A_M)
    db.session.add(new_student)
    db.session.commit()
    return redirect('/foitites')
  return render_template ("addStudents.html")

#κουμπι delete
@app.route('/foitites/delete/<int:id>')
def deleteStudent(id):
  foititis= Students.query.get_or_404(id)
  db.session.delete(foititis)
  db.session.commit()
  return redirect('/foitites')

#κουμπι edit
@app.route('/foitites/editStudents/<int:id>', methods = ["GET","POST"])
def editStudents(id):
  
  student= Students.query.get_or_404(id)

  if request.method=="POST":
    student.Onoma = request.form['name']
    student.Epitheto = request.form['lastname']
    student.Email = request.form['email']
    student.dieuthinsi = request.form['dieuthinsi']
    student.Phone = request.form['Phone']
    student.eksamino = request.form['eksamino']
    student.A_M = request.form['A_M']
    db.session.commit()
    return redirect('/foitites')
  else:
    return render_template('editStudents.html' , student = student)

if __name__ == "__main__":
 app.run(debug=True)

