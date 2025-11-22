from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_

from . import db
from .forms import RegistrationForm, UpdateProfileForm, LoginForm
from .models import User

# Blueprint keeps routes modular and easy to register in the factory.
main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Home page showing the newest registered users."""
    users = User.query.order_by(User.created_at.desc()).limit(10).all()
    return render_template('users.html', users=users)


@main.route('/register', methods=['GET', 'POST'])
def register():
    """Display and process the registration form."""
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()

        # Prevent duplicate username/email before we create the record.
        existing = User.query.filter(or_(User.username == username, User.email == email)).first()
        if existing:
            flash('A user with that username or email already exists.', 'warning')
        else:
            user = User(
                username=username,
                email=email,
                full_name=form.full_name.data.strip() if form.full_name.data else None,
                bio=form.bio.data.strip() if form.bio.data else None,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('.login'))

    return render_template('register.html', form=form)


@main.route('/user/<int:user_id>')
def profile(user_id):
    """Render an individual user's profile."""
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)


@main.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    """Allow owners to update their profile details."""
    user = User.query.get_or_404(user_id)

    # Guard condition ensures users can edit only their own profile.
    if current_user.id != user.id:
        flash('You are not authorized to edit that profile.', 'danger')
        return redirect(url_for('.profile', user_id=user.id))

    form = UpdateProfileForm(obj=user)

    if form.validate_on_submit():
        proposed_email = form.email.data.strip().lower()
        conflict = User.query.filter(User.email == proposed_email, User.id != user.id).first()
        if conflict:
            flash('Another user already uses that email address.', 'warning')
        else:
            user.full_name = form.full_name.data.strip() if form.full_name.data else None
            user.email = proposed_email
            user.bio = form.bio.data.strip() if form.bio.data else None
            db.session.commit()
            flash('Profile updated.', 'success')
            return redirect(url_for('.profile', user_id=user.id))

    return render_template('edit.html', form=form, user=user)


@main.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate users using username or email and their password."""
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.username_or_email.data.strip()
        user = User.query.filter(or_(User.username == identifier, User.email == identifier)).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('.profile', user_id=user.id))

        flash('Invalid credentials.', 'danger')

    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    """Terminate the current user session."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('.index'))
