# Introductory Notes 

from flask import Flask, request, redirect, render_template

# Use Flask SQLAlchemy to connect to blog database
from flask_sqlalchemy import SQLAlchemy

# Dependencies
import pymysql
import cgi

# Create app variable and set to the
# name of the module in Flask
app = Flask(__name__)

# Blog starts in developer mode
app.config['DEBUG'] = True

# Local database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:3306/build-a-blog'

# Print ORM commands in console
app.config['SQLALCHEMY_ECHO'] = True

# MYSQL DB Connection
db = SQLAlchemy(app)

# Basic Model for Blog Post
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    body = db.Column(db.String(255))

    def __init__(self, title, body):
        self.title = title
        self.body = body


# Temporarily store form fields
# fields = []

# URL address to create a New Post
@app.route('/newpost', methods=['POST', 'GET'])
def index():

    title_error = ''    
    body_error = ''
    all_errors = []
    
    # If the form has been submitted
    if request.method == 'POST':
        # Grab the value from input title
        post_title = cgi.escape(request.form['title'])
        
        # If the User doesn't type a title
        if post_title == '':
            # Display title error message
            title_error = "Title field cannot be empty"
            # Store title error in an array
            all_errors.append(title_error)
        
        # Grab the value of textarea body
        post_body = cgi.escape(request.form['body'])
        
        # If the User doesn't type a description
        if post_body == '':
            # Display body error message
            body_error = "Body field cannot be empty"
            # Store body error in an array
            all_errors.append(body_error)
        
        # Check for input errors
        if all_errors:
            # Render the create post form with error messages
            return render_template("create_post.html", title=post_title, body=post_body, title_error=title_error, body_error=body_error )
        
        # Store the fields entered in Database
        new_post = Blog(post_title, post_body)
        db.session.add(new_post)
        db.session.commit()
        # Set the id for created Post
        post_id = new_post.id

        # Redirect User to the Post created page
        return redirect('/single_post?post_id=' + str(post_id))
    else:
        return render_template('create_post.html')

# Same URL address for home and page to display blog posts
@app.route('/', methods=['POST', 'GET'])
@app.route('/blog_posts', methods=['POST', 'GET'])
def blog_posts():
    # Display all created Blog Posts
    posts = Blog.query.all()
    
    # If there are GET requests
    if request.args:
        # Handle the query paramater for each 
        # blog post so that post_id is stored        
        print('request.args: ', request.args)
        post_id = request.args.get("post_id")
        print('post_id: ', post_id)
        
        # Display each blog Post when User clicks
        # on individual Post 
        return redirect('/single_post?post_id=' + post_id)

    # Render blog posts page with each single post 
    return render_template('blog_posts.html', posts=posts)

# URL address for single Post
@app.route('/single_post')
def single_post():
    # Grab the single Post if
    post_id = request.args.get("post_id")
    # Display each single Post from Database
    post = Blog.query.get(post_id)
    
    # Render the template for single Post page
    return render_template('single_post.html', post=post)

# This is the main file to run the app
if __name__ == "__main__":
    app.run()