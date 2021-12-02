from flask.helpers import url_for
from app import app
from app.forms import LoginForm
from flask import render_template, flash, redirect
from flask_login import current_user, login_user
from app.models import User
from flask_login import logout_user
from flask_login import login_required
from flask import request 
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from app.forms import PostForm
from app.models import Post
from datetime import datetime

@app.route('/')
# @app.route('/index')
# @login_required
# def index():

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('menu'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        #if nothing entered or if username and password don't match database then
        #do not allow them to sign in
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        #next_page = request.args.get('next')

        #next page after signing in is always the menu
        next_page = url_for('menu')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('menu')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
    
@app.route("/menu", methods=['GET', 'POST'])
@login_required
def menu():
    return render_template("menu.html")

@app.route("/tracker", methods=['GET', 'POST'])
@login_required
def tracker():
    return render_template("tracker.html")

@app.route("/activity", methods=['GET', 'POST'])
@login_required
def activity():
    return render_template("activity.html")

@app.route("/journal", methods=['GET', 'POST'])
@login_required
def journal():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('You succesfully submitted a post. Check under previous journal entries to see it.')
        return redirect(url_for('journal'))

    
    return render_template("journal.html", title='Journal Submit', form=form)

@app.route('/prev')
@login_required
def prev():

    #will start creating navigatable pages when too
    #many posts are on one page
    page = request.args.get('page', 1, type=int)

    #accesses all the posts tied to the user and sends it to the html file
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('prev', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('prev', page=posts.prev_num) \
        if posts.has_prev else None

    #pass the ids for the posts through here as well
    return render_template("prev.html", title="Previous Journal Entries", 
                            posts=posts.items, next_url=next_url,
                            prev_url=prev_url)

#deletes entire account as well as posts associated with it
@app.route("/delete_acc")
def delete_acc():

    try:
        db.session.delete(current_user)
        db.session.commit()
        flash("Account deleted successfully")
        return redirect(url_for("login"))

    except:
        flash("There was a problem deleting account, try again.")

#deletes the selected post
@app.route("/delete_post/<int:id>")
def delete_post(id):

    try:
        post_to_delete = Post.query.get_or_404(id)
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Post deleted successfully")
        return redirect(url_for("prev"))
    
    except:
        flash("There was a problem deleting the post, try again.")

@app.route("/edit_post/<int:id>", methods=['GET', 'POST'])
def edit_post(id):

    #from models: class Post, has id, body (where user input is stored in the database)
    post_to_save = Post.query.get_or_404(id)

    #from forms: class PostForm, has post (user input words)
    form = PostForm()

    #if submit is clicked
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        
        db.session.commit()
        flash('You succesfully edited a post.')
        return redirect(url_for('prev'))
    
    print("POST HERE: " + str(post_to_save.body))

    #form.post = post

    return render_template("edit_post.html", title='Edit Post', form=form, post=post_to_save)






