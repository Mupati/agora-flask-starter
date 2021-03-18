from flask import render_template, redirect, flash, url_for
from flask_login import login_required, login_user, logout_user, current_user

from . import auth
from .forms import LoginForm, RegistrationForm

from .. import db

from ..models import User


@auth.route('/auth/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('agora.index'))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()

            # check password validity
            if user is not None and user.verify_password(
                    form.password.data):
                # log user in
                login_user(user)
                # redirect to the dashboard page after login
                return redirect('/')
            # when login details are incorrect
            else:
                flash('Invalid Email or Password')
        return render_template('auth/login.html', title='Log in', form=form)


@auth.route('/auth/register', methods=['GET', 'POST'])
def register():
    """
    Handle registration
    """
    if current_user.is_authenticated:
        return redirect(url_for('agora.index'))
    else:
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(email=form.email.data,
                        username=form.username.data,
                        password=form.password.data)

            # store user details in db
            db.session.add(user)
            db.session.commit()
            flash('You have successfully registered! You may now login.')

            # redirect to the login page
            return redirect(url_for('auth.login'))

        return render_template('auth/register.html', title='Register', form=form)


@auth.route('/logout')
@login_required
def logout():
    """
    Logout user
    """
    logout_user()
    # redirect to the login page
    return redirect(url_for('auth.login'))
