from flask import Blueprint, render_template


bp = Blueprint(
    "exhibition",
    __name__,
    url_prefix="/exhibicion"
)


@bp.route("/")
def index():
    return render_template(
        "exhibition/index.html"
    )