from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog4life@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] =True
db = SQLAlchemy(app)

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
    return render_template('blog.html', blogs=blogs, title='Blog')



@app.route('/newpost')
def newpost():
    '''loads page to submit a new blog'''
    return render_template('newpost.html')

@app.route('/valid', methods=['POST'])
def valid():
    '''checks if the blog entry is valid'''
    title = request.form['title']
    post = request.form['post']
    

    if title == "" or post == "":
        return render_template('newpost.html')
    else:
        new_blog = Blog(title,post)
        db.session.add(new_blog)         
        db.session.commit()
    blog_post = Blog.query.filter_by(title=title).first()
    post_id = blog_post.id
    return redirect('/individual?post_id='+str(post_id))

@app.route('/individual')
def individual():
    blog_id=int(request.args.get('post_id'))
    blog=Blog.query.get(blog_id)
    return render_template('individual.html', blog=blog)

if __name__== '__main__':
    app.run()