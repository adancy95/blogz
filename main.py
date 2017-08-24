from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2

app = Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog4life@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] =True
db = SQLAlchemy(app)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    post = db.Column(db.Text)


    def __init__(self, title, post):
        self.title = title
        self.post = post
        
@app.route('/blog')
def blog():
    '''loads page with all of the blog posts'''
    blogs = Blog.query.all()
    template = jinja_env.get_template('blog.html')
    return template.render(blogs=blogs, title='Blog')



@app.route('/newpost')
def newpost():
    '''loads page to submit a new blog'''
    template = jinja_env.get_template('newpost.html')
    return template.render()

@app.route('/valid', methods=['POST'])
def valid():
    '''checks if the blog entry is valid'''
    title = request.form['title']
    post = request.form['post']

    if title == "" or post == "":
        template = jinja_env.get_template('newpost.html')
        return template.render()
    else:
        new_blog = Blog(title,post)
        db.session.add(new_blog)         
        db.session.commit()
        return redirect('/blog')

if __name__== '__main__':
    app.run()