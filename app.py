from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship ,joinedload
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from all_forms import CreatePostForm ,RegisterForm ,LoginForm ,CommentForm
import os
from functools import wraps
import hashlib





def gravatar(email, size=100, default='retro', rating='g'):
    hash_email = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    gravatar_url = f"https://www.gravatar.com/avatar/{hash_email}?s={size}&d={default}&r={rating}"
    return gravatar_url














## admin is the first user >> admin@gmail.com password = Test@123
# guest user >> guest_one@gmail.com = Test@123
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# Register the gravatar filter
app.jinja_env.filters['gravatar'] = gravatar


##CONNECT TO DB
# app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///E:\All coursessssss\All  python staff\100 Days of Code\000-solutions and projects\69. Day 69 - Advanced - Blog Capstone Project Part 4 - Adding Users\blog.db'


# app.config['SQLALCHEMY_DATABASE_URI'] =os.environ.get("DATABASE_URL")
### - connecting to postgres database as external connection 
# app.config['SQLALCHEMY_DATABASE_URI'] =(r"postgresql://database_name_postgress_user:Y28wL6K5cOaaSOmBTwTD0pMCWtNNXksz@dpg-clkvn3sjtl8s73f44910-a.oregon-postgres.render.com/database_name_postgress")


### ---- connecting to postgres database as INTERNAL connection 
app.config['SQLALCHEMY_DATABASE_URI'] =(r"postgresql://database_name_postgress_user:Y28wL6K5cOaaSOmBTwTD0pMCWtNNXksz@dpg-clkvn3sjtl8s73f44910-a/database_name_postgress")



app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


###
class User(UserMixin, db.Model):
    __tablename__ = "users_table"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), unique=True, nullable=False)
    name = db.Column(db.String(250), nullable=False)
    #This will act like a List of BlogPost objects attached to each User. 
    #The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    #-----Add parent relationship--------
    #-----comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")


class Comment(db.Model):
    __tablename__ = "comments_table"
    id = db.Column(db.Integer, primary_key=True)
    the_text = db.Column(db.Text, nullable=False)

    ##------linking User as a parent to class comments as child  -----
    author_id = db.Column(db.Integer, db.ForeignKey("users_table.id"))
    comment_author = relationship("User", back_populates="comments")
        
    ###------linking BlogPost as a parent to class comments as child  -----
    ##  every post lists all comments
    post_id  = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost",back_populates="all_comments_at_blog")
    

    
##CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    
    ###------linking BlogPost as a child to class users as parent  -----
    # Create Foreign Key, "users_table.id" the users refers to the tablename of User class.
    author_id = db.Column(db.Integer, db.ForeignKey("users_table.id"))
    #  referencing the User class."posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    ## “”If any errors,  manually edit the database and added auther_id field with value 1”
    ###------linking BlogPost as a parent to class comments as child  -----
    all_comments_at_blog = relationship("Comment", back_populates="parent_post")





    
    
    
    
##### normal class before adding tables relationships
# class BlogPost(db.Model):
#     __tablename__ = "blog_posts"
#     id = db.Column(db.Integer, primary_key=True)
#     author = db.Column(db.String(250), nullable=False)
#     title = db.Column(db.String(250), unique=True, nullable=False)
#     subtitle = db.Column(db.String(250), nullable=False)
#     date = db.Column(db.String(250), nullable=False)
#     body = db.Column(db.Text, nullable=False)
#     img_url = db.Column(db.String(250), nullable=False)



login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # return User.query.get(int(user_id))
    return User.query.session.get(User, int(user_id))
    # return db.session.get((user_id))







#Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)    
    
    
        ### to show delete and create_now_post buttons >change this in index.html > at two locations
        # {% if current_user.is_authenticated  and current_user.id == 2 %}    

    return decorated_function




@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register',methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        if User.query.filter_by(email=form.email_var1.data).first():
            flash("You've already signed up with that email, log in instead!")
            #Redirect to /login route.
            return redirect(url_for('login'))
        hash_and_salted_password = generate_password_hash(
            form.password_var1.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        # Process the form data, for example, save it to the database
        adding_new_user = User(email=form.email_var1.data,
                    password=hash_and_salted_password, 
                    name=form.name_var1.data
                    )
        
        db.session.add(adding_new_user)
        db.session.commit()
        #This line will authenticate the user with Flask-Login
        login_user(adding_new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html",form= form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user :
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash('Password incorrect, please try again.')
        else:
            flash("That email does not exist, please try again.")
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):

    form_var1 = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    
    if form_var1.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        adding_new_comment = Comment(
        the_text = form_var1.comment_text.data,
        author_id  = current_user.id,
        post_id = requested_post.id)
        db.session.add(adding_new_comment)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    getting_blog_comments = Comment.query.filter_by(post_id=post_id).all()
    print(getting_blog_comments)
    return render_template("post.html", post=requested_post, form = form_var1,blog_comments_var1=getting_blog_comments)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")




@app.route("/new-post", methods=['GET', 'POST'])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>",methods = ["POST","GET"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, tab_title=f"Editing {post.title}")


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))





if __name__ == "__main__":
    with app.app_context():
	# all direct operations are added here
        db.create_all()
        app.run()
