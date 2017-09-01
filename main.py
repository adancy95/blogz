
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12345@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] =True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    post = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, post, owner):
        self.title = title
        self.post = post
        self.owner = owner
        
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')       

@app.route('/')
def index():
    '''loads the home page'''
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/blog')
def blog():
    '''loads page with all of the blog posts'''
    if request.args.get('user'):
        user = User.query.get((request.args.get('user')))
        blogs = Blog.query.filter_by(owner_id=user.id).all()
        return render_template('blog.html', blogs=blogs, title=user.username, blogger=user)

    elif request.args.get('post_id'):
        blog=Blog.query.get(request.args.get('post_id'))
        user = User.query.filter_by(id=blog.owner_id).first()
        return render_template('individual.html', blog=blog, blogger=user)
    else:
         blogs = Blog.query.all()
         user=User.query.all()
         return render_template('blog.html', blogs=blogs, title='Blog', blogger=user)

@app.route('/newpost')
def newpost():
    '''loads page to submit a new blog'''
    return render_template('newpost.html')

@app.route('/valid', methods=['POST'])
def valid():
    '''checks if the blog entry is valid'''
    title = request.form['title']
    post = request.form['post']
    

    if title == "" and post == "":
        flash('Blog Title and Your New Blog cannot be empty')
        return render_template('newpost.html')
    elif title == "":
        flash('Your Blog Title cannot be empty')
        return render_template('newpost.html')
    elif post == "":
        flash(' Your New Blog cannot be empty')
        return render_template('newpost.html')
    else:
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(title,post,owner)
        db.session.add(new_blog)         
        db.session.commit()
    blog_post = Blog.query.filter_by(title=title).first()
    post_id = blog_post.id
    return redirect('/individual?post_id='+str(post_id))

@app.route('/individual')
def individual():
    blog=Blog.query.get(int(request.args.get('post_id')))
    user = User.query.filter_by(id=blog.owner_id).first()
    return render_template('individual.html', blog=blog, blogger=user)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
       
        if existing_user and existing_user.password == password:
            session['username'] = username
            return redirect('/newpost')
        elif existing_user and existing_user.password != password:
            password_error= "Incorrect Password"
            return render_template('login.html', password_error=password_error, username=username)
        elif not existing_user:
            username_error='The username does not exist. Please create a new account.'
            return render_template('login.html', username_error=username_error)
            
    return render_template('login.html')

    

def length(parameter):
    """checks the number of characters in the user input fields"""
    if len(parameter) >= 3 and len(parameter) <= 20:
        return True

def no_space(parameter):
    """checks if any spaces are in the user input fields"""
    if parameter.count(" ") == 0:
        return True

def confirmation(parameter, parameter2):
    """checks if the passwords match"""
    if parameter == parameter2:
        return True

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    """ Allows a user to signup for a blogz account if they provide a valid username and password"""
    if request.method == 'GET':
        return render_template('signup.html')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verifyPass = request.form['verifyPass']

        existing_user = User.query.filter_by(username=username).first()
        
        if length(username) and no_space(username) and not existing_user:
            username_error = ""
        elif existing_user:
            username_error = "Username already exist. Choose a different username."
        else:
            username_error = "Not a valid username"

        if length(password) and no_space(password) and confirmation(password, verifyPass):
            password_error = ""
        elif not confirmation(password, verifyPass):
            password_error = "Passwords do not match"
        else:
            password_error = "Not a valid password" 
        
        if username_error == "" and password_error == "":
            new_user = User(username, password)
            db.session.add(new_user)         
            db.session.commit()
            session['username']=username
            return redirect('/newpost')
        else: 
            return render_template('signup.html', username_error=username_error, password_error=password_error, username=username)
    
    
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__== '__main__':
    app.run()