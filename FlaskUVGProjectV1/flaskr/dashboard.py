from flask import Blueprint, render_template

from flaskr.auth import login_required

bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)

@bp.route("/")
@login_required
def index():
    return render_template(
        "dashboard/index.html"
    )

@bp.route("/exhibicion")
@login_required
def exhibition():
    return render_template(
        "dashboard/exhibition.html"
    )