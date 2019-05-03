from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blog:Aa02850621!@localhost:8889/blog'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'sjhdakfjhkja8931hr8'
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship ('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ["login", "signup", "blog", "index", "static"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = user.username
            flash('Welcome back, '+user.username)
            return redirect("/newpost")
        if not user:
            flash('Username does not exists')
            return redirect('/login')
        else:
            flash('Bad username or password')
            return redirect("/login")
 

    return render_template("login.html")

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    flash('Logged out')
    return redirect("/")

def verified(text):
    if len(text) >= 3 and len(text) <= 20 and not ' ' in text:
        return True
    else:
        return False

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password'] 
        existing_user = User.query.filter_by(username=username).first()  

        if len(username) ==0:
            flash("Username must not be blank")
            return redirect("/signup")
        elif not verified(username):
            flash("Must enter an acceptable username")
            username = username
            return redirect("/signup")
        else:
            username = username
        if len(username) <= 3 or len(username) > 20:
            flash("Username must be between 3 and 20 characters long")
            return redirect("/signup")
        elif " " in username:
            flash('Username cannot contain any space')
            return redirect("/signup")
        else:
            username = username
        if len(password) ==0:
            flash("Password is blank")
            return redirect("/signup")
        elif not verified(password):
            flash("Must enter an acceptable password")
            return redirect("/signup")
        else:
            password = password
        if password != verify_password:
            flash("Password must match")
            return redirect("/signup")
        elif username:
            flash('Username already exists')

        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect("/newpost")


    return render_template("signup.html")

@app.route('/newpost')
def post():
    return render_template('newpost.html', title="New Post")

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    title = request.form["title"]
    body = request.form["body"]
    owner = User.query.filter_by(username=session['username']).first()

    if title == "":
        flash('Must have a title')
        return redirect("/newpost")
    if body == "":
        flash('Must have a body')
        return redirect("/newpost")
    else:
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        return redirect ("/blog?id={}".format(new_post.id)) 
    
    return render_template('newpost.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog(): 
    blog_id = request.args.get('id')
    user_id = request.args.get('userid')
    posts = Blog.query.all()
    
    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template("blogpost.html", title="Single blog", post=post, username=session['username'])
    if user_id:
        entries = Blog.query.filter_by(owner_id=user_id)
        return render_template('user.html', entries=entries)
    
    return render_template('blog.html', posts=posts)

@app.route("/")
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()