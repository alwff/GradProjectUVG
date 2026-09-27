import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.models import User
from flaskr.extensions import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        error = None

        if not username:
            error = 'El usuario es obligatorio.'

        elif not email:
            error = 'El correo electrónico es obligatorio.'

        elif not password:
            error = 'La contraseña es obligatoria.'

        elif User.query.filter_by(
            username=username
        ).first():
            error = 'Ese nombre de usuario ya está registrado.'

        elif User.query.filter_by(
            email=email
        ).first():
            error = 'Ese correo electrónico ya está registrado.'

        if error is None:
            try:
                new_user = User(
                    username=username,
                    email=email,
                    password=generate_password_hash(
                        password
                    )
                )

                db.session.add(new_user)
                db.session.commit()

            except Exception:
                db.session.rollback()

                error = (
                    'No fue posible registrar el usuario.'
                )
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(
            username=username
        ).first()
        error = None

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id

            return redirect(
                url_for('dashboard.index')
            )

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(
        url_for('public.home')
    )


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Debe iniciar sesión.")
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
