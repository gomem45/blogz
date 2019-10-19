# Introductory Notes

from flask import Flask, request, redirect, render_template, flash, session

# Use Flask SQLAlchemy to connect to blog database
from flask_sqlalchemy import SQLAlchemy

from hashutils import make_pw_hash, check_pw_hash

# Dependencies
import pymysql
import cgi

# Create app variable and set to the
# name of the module in Flask
app = Flask(__name__)

# Blog starts in developer mode
app.config['DEBUG'] = True

# Local database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:3306/blogz'

# Print ORM commands in console
app.config['SQLALCHEMY_ECHO'] = True

app.secret_key = '71408a9f3f75d712b98d4f20bad52'

# MYSQL DB Connection
db = SQLAlchemy(app)

# Basic Model for Blog Post

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    # Create a foreign key that connects User class to 
    # Blog class. (one User can have many Posts). 
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

# TODO
# Create a User model with some starting fields
# that include username and passkey. Create a 
# relationship that points to tne owner field

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    # Encrypt the password by using one of the functions
    # in hashutils file, and store it in passkey field
    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


# TODO
# After User has created an account. User can see
# all the blog Posts published and authors page.
@app.route('/login', methods=['POST', 'GET'])
def login():
    
    # When User submits Login form
    if request.method == 'POST':
        # Store the fields for each User
        username = request.form['username']
        password = request.form['password']

        # Access the User stored in the Database by 
        # searching for the username
        user = User.query.filter_by(username=username).first()

        # if the Username does not exist
        if user == None:
            flash('Username could not be found', 'user')

            return render_template('login.html')

        # If user leaves a blank password    
        if password == '':
            flash('Cannot leave password blank', 'pwd')
            
            return render_template('login.html')
        
        # If the password enter does not match has stored in
        # the Database
        elif not check_pw_hash(password, user.pw_hash):
            flash('Password typed is incorrect', 'pwd')
            
            return render_template('login.html')

        # Login validation passes
        else:
            # Store each username in a cookie session
            session['username'] = username

            # Redirect User to published posts page
            return redirect('/blog_posts')

    return render_template('login.html')


# TODO
# Guest User needs to create an account, 
# in order to create a New Post 
@app.route('/signup', methods=['GET','POST'])
def signup():
    # When User submits Signup form
    if request.method == 'POST':
        # Access the fields of Signup form
        username = request.form['username']
        pwd = request.form['password']
        verify = request.form['verify']

        # Query the Database to compare uf User 
        # already exists. Grab the first record
        user = User.query.filter_by(username=username).first()

        # If a User has already register with that username
        if user != None:
            if user.username == username:
                flash('That username has already been taken')
        
        # If User leaves username field blank 
        elif username == '':
            flash('Username field cannot be blank')
        
        # If username is not a least 3 characters 
        elif len(username) < 3:
            flash('Username need to be at least 3 characters')
         
        # if User leaves password blank
        elif pwd == '':
            flash('Password field cannot be blank')

        # If password is not at least 3 characters
        elif len(pwd) < 3:
            flash('Password needs to be at least 3 characters')

        # If User leaves Confirm Password field blank
        elif verify == '':
            flash('Confirm Password cannot be blank')
        
        # If Password enter is not equal Confirm password 
        elif pwd != verify:
            flash('Password entered does not match')
        
        # Registration validation passes
        else:
            # Create the new User registered and 
            # stored it in MySQL Database
            new_user = User(username, pwd)
            db.session.add(new_user)
            db.session.commit()

            # Keep the session of username
            # registered and redirect User
            # to the create post page.
            session['username'] = username

            return redirect('/newpost')

    return render_template('signup.html')


# TODO
# 
@app.route('/logout')
def logout():
    
    # Check User session is active 
    # before deleting session cookie
    if session:
        del session['username']
    
    return redirect('/blog_posts')

# TODO
# Users must login in order to create an 
# unlimited number of Posts
@app.before_request
def require_login():
    # Public routes guests can browse
    allowed_routes = ['index','login', 'blog_posts', 'signup']
    
    # Restrict guests from unauthorized pages
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


# URL address to create a New Post
@app.route('/newpost', methods=['POST', 'GET'])
def create_post():

    # If the form has been submitted
    if request.method == 'POST':
   
        # Grab the value from input title
        post_title = request.form['title']

        # Grab the value of textarea body
        post_body = request.form['body']
        
        # If the User doesn't type a title
        if request.form['title'] == '':
            # Display title error message
            title_error = "Title field cannot be empty"
        else:
            title_error = ''

        # If the User doesn't type a description
        if request.form['body'] == '':
            # Display body error message
            body_error = "Body field cannot be empty"
         
        else:
            body_error = ''
        
        # Check for input errors
        if title_error or body_error:
            # Render the create post form with error messages
            return render_template("create_post.html", title=post_title, body=post_body, title_error=title_error, body_error=body_error)

        else:
            post_title = request.form['title']
            post_body = request.form['body']

            user = session['username']

            user_id = User.query.filter_by(username=user).first()
            blog = Blog(post_title, post_body, user_id)
            db.session.add(blog)
            db.session.commit()

            # Store the fields entered in Database
            post_id = blog.id
      
            # Redirect User to the Post created page
            return redirect('/blog_posts?post_id=' + str(post_id))
    
    return render_template('create_post.html')

# TODO
# Change route so that a decision can be made when blog posts 
# page needs to display dynamically all registered users, a 
# template for each individual post, or all the blog posts.

@app.route('/blog_posts', methods=['POST', 'GET'])
def blog_posts():

    # TODO
    # Use request.args.get to store the parsed contents 
    # that comes from Post and User table string query

    # post id that belongs to each Post 
    post_id = request.args.get('id')
    # user id that belongs to each User
    user_id = request.args.get('user')

    # If author is found
    if user_id:
        # Access all the authors that has written a Post
        writers = Blog.query.filter_by(owner_id=user_id).all()

        return render_template('blog_posts.html',user=writers, authors=user_id)

    # if post is found 
    elif post_id:
        # Access each individual Post written by author
        posts = Blog.query.filter_by(id=post_id).all()

        return render_template('blog_posts.html', post=posts, page=post_id)     
    else:

        # Display all created Blog Posts
        posts = Blog.query.all()
    
        # Render blog posts page with each single post 
        return render_template('blog_posts.html', posts=posts)

# TODO
# User can browse blog Posts that belong to each author
# as he or she clicked on the corresponding username
@app.route('/')
def index():

    # In this case, Users stored in the Database
    # are all authors. So all of them are display
    users = User.query.all()

    return render_template('index.html', users=users)


# This is the main file to run the app
if __name__ == "__main__":
    app.run()

