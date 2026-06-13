from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    g,
    flash,
    request,
    current_app
)

from flaskr.auth import login_required

from flaskr.models import User

from flaskr.extensions import db

bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)


@bp.route("/")
@login_required
def index():

    users = User.query.order_by(
        User.username
    ).all()

    return render_template(
        "users/index.html",
        users=users
    )


@bp.route("/<int:id>/confirm-delete")
@login_required
def confirm_delete(id):

    user = User.query.get_or_404(
        id
    )

    if user.id == g.user.id:

        flash(
            "No puede eliminar su propia cuenta."
        )

        return redirect(
            url_for("users.index")
        )

    return render_template(
        "users/confirm_delete.html",
        user=user
    )


@bp.route(
    "/<int:id>/delete",
    methods=("POST",)
)
@login_required
def delete(id):

    user = User.query.get_or_404(
        id
    )

    if user.id == g.user.id:

        flash(
            "No puede eliminar su propia cuenta."
        )

        return redirect(
            url_for("users.index")
        )

    password = request.form[
        "master_password"
    ]

    if password != current_app.config[
        "MASTER_DELETE_PASSWORD"
    ]:

        flash(
            "Contraseña maestra incorrecta."
        )

        return redirect(
            url_for(
                "users.confirm_delete",
                id=id
            )
        )

    db.session.delete(
        user
    )

    db.session.commit()

    flash(
        "Usuario eliminado correctamente."
    )

    return redirect(
        url_for("users.index")
    )