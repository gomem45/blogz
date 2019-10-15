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

app.secret_key = 'ioga;skebr'

# MYSQL DB Connection
db = SQLAlchemy(app)

# Basic Model for Blog Post

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user == None:
            flash('Username does not exists', 'user')
            return render_template('login.html')

        if password == '':
            flash('Password does not exists', 'pwd')
            return render_template('login.html')
        
        elif not check_pw_hash(password, user.pw_hash):
            flash('User password is incorrect', 'pwd')
            return render_template('login.html')

        else:
            session['username'] = username
            return redirect('/blog_posts')

    return render_template('login.html')


@app.route('/signup', methods=['GET','POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        pwd = request.form['password']
        verify = request.form['verify']

        user = User.query.filter_by(username=username).first()

        if user != None:
            if user.username == username:
                flash('This username already exists')

        elif username == '':
            flash('Username must be filled in')
         
        elif len(username) < 3:
            flash('Username need to be at least 3 characters')
         
        elif pwd == '':
            flash('Password need to be filled in')
            
        elif len(pwd) < 3:
            flash('Password needs to be at least 3 characters')

        elif verify == '':
            flash('Confirm Password need to be filled in')

        elif pwd != verify:
            flash('Passwords do not match')
      
        else:
            new_user = User(username, pwd)
            db.session.add(new_user)
            db.session.commit()
         
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')


@app.route('/logout')
def logout():

    if session:
        del session['username']
    
    return redirect('/blog_posts')


@app.before_request
def require_login():
    allowed_routes = ['index','login', 'blog_posts', 'signup']

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



# Same URL address for home and page to display blog posts
@app.route('/blog_posts', methods=['POST', 'GET'])
def blog_posts():

    post_id = request.args.get('id')
    user_id = request.args.get('user')

    if user_id:
        writers = Blog.query.filter_by(owner_id=user_id).all()

        return render_template('blog_posts.html',user=writers, authors=user_id)

    elif post_id:
        posts = Blog.query.filter_by(id=post_id).all()

        return render_template('blog_posts.html', post=posts, page=post_id)     
    else:

        # Display all created Blog Posts
        posts = Blog.query.all()
    
        # Render blog posts page with each single post 
        return render_template('blog_posts.html', posts=posts)


@app.route('/')
def index():

    users = User.query.all()
    return render_template('index.html', users=users)



# This is the main file to run the app
if __name__ == "__main__":
    app.run()
