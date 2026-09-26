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

from datetime import datetime

bp = Blueprint(
    "requests",
    __name__,
    url_prefix="/requests"
)

def get_item_conflict(
    item,
    request_record
):

    requested_start = datetime.combine(
        request_record.needed_date,
        request_record.start_time
    )

    requested_end = datetime.combine(
        request_record.return_date,
        request_record.end_time
    )

    approved_items = (
        RequestItem.query
        .join(Request)
        .filter(
            RequestItem.specimen_id
                == item.specimen_id,

            RequestItem.item_status
                == "approved",

            RequestItem.id
                != item.id
        )
        .all()
    )

    for approved_item in approved_items:

        approved_request = (
            approved_item.request
        )

        existing_start = datetime.combine(
            approved_request.needed_date,
            approved_request.start_time
        )

        existing_end = datetime.combine(
            approved_request.return_date,
            approved_request.end_time
        )

        if (
            requested_start < existing_end
            and requested_end > existing_start
        ):
            return approved_item

    return None

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

    request_record = (
        Request.query.get_or_404(id)
    )

    item_checks = {}

    for item in request_record.items:

        conflict = get_item_conflict(
            item,
            request_record
        )

        item_checks[item.id] = {
            "available":
                conflict is None,

            "conflict":
                conflict
        }

    return render_template(
        "requests/detail.html",
        request_record=request_record,
        item_checks=item_checks
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