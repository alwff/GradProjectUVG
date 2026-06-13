from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request
)
from flaskr.auth import login_required

from flaskr.models import (
    Request,
    RequestItem
)

from flaskr.extensions import db

bp = Blueprint(
    "requests",
    __name__,
    url_prefix="/requests"
)

@bp.route("/")
@login_required
def index():

    requests = Request.query.order_by(
        Request.created_at.desc()
    ).all()

    return render_template(
        "requests/index.html",
        requests=requests
    )

@bp.route("/<int:id>")
@login_required
def detail(id):

    request_record = Request.query.get_or_404(
        id
    )

    return render_template(
        "requests/detail.html",
        request_record=request_record
    )

@bp.route(
    "/<int:id>/update",
    methods=("POST",)
)
@login_required
def update_status(id):

    request_record = Request.query.get_or_404(
        id
    )

    request_record.status = request.form[
        "status"
    ]

    request_record.status_notes = request.form[
        "status_notes"
    ]

    db.session.commit()

    return redirect(
        url_for(
            "requests.detail",
            id=id
        )
    )