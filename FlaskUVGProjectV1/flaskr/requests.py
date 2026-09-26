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
    RequestItem,
    Movement,
    MovementItem
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

def update_request_status(
    request_record
):

    statuses = [
        item.item_status
        for item in request_record.items
    ]

    if not statuses:
        request_record.status = "pending"
        return

    if all(
        status == "approved"
        for status in statuses
    ):
        request_record.status = "approved"

    elif all(
        status == "rejected"
        for status in statuses
    ):
        request_record.status = "rejected"

    elif all(
        status != "pending"
        for status in statuses
    ):
        request_record.status = (
            "partially_approved"
        )

    else:
        request_record.status = "pending"

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
    item_movement_status = {}

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

        has_exit = (
            Movement.query
            .join(MovementItem)
            .filter(
                Movement.request_id == request_record.id,
                Movement.movement_type == "exit",
                MovementItem.specimen_id == item.specimen_id
            )
            .first()
            is not None
        )

        has_entry = (
            Movement.query
            .join(MovementItem)
            .filter(
                Movement.request_id == request_record.id,
                Movement.movement_type == "entry",
                MovementItem.specimen_id == item.specimen_id
            )
            .first()
            is not None
        )


        if has_entry:

            movement_status = "returned"

        elif has_exit:

            movement_status = "delivered"

        else:

            movement_status = "reserved"


        item_movement_status[
            item.id
        ] = movement_status
        

    return render_template(
        "requests/detail.html",
        request_record=request_record,
        item_checks=item_checks,
        item_movement_status=item_movement_status
    )

@bp.route(
    "/<int:request_id>/items/<int:item_id>/approve",
    methods=("POST",)
)
@login_required
def approve_item(
    request_id,
    item_id
):

    request_record = (
        Request.query.get_or_404(
            request_id
        )
    )

    item = (
        RequestItem.query.get_or_404(
            item_id
        )
    )

    if item.request_id != request_record.id:

        return redirect(
            url_for(
                "requests.detail",
                id=request_id
            )
        )

    if item.item_status != "pending":

        return redirect(
            url_for(
                "requests.detail",
                id=request_id
            )
        )

    conflict = get_item_conflict(
        item,
        request_record
    )

    if conflict:

        return redirect(
            url_for(
                "requests.detail",
                id=request_id
            )
        )

    item.item_status = "approved"

    update_request_status(
        request_record
    )

    db.session.commit()

    return redirect(
        url_for(
            "requests.detail",
            id=request_id
        )
    )

@bp.route(
    "/<int:request_id>/items/<int:item_id>/reject",
    methods=("POST",)
)
@login_required
def reject_item(
    request_id,
    item_id
):

    request_record = (
        Request.query.get_or_404(
            request_id
        )
    )

    item = (
        RequestItem.query.get_or_404(
            item_id
        )
    )

    if item.request_id != request_record.id:

        return redirect(
            url_for(
                "requests.detail",
                id=request_id
            )
        )

    # Solo permitimos decidir items pendientes.
    if item.item_status != "pending":

        return redirect(
            url_for(
                "requests.detail",
                id=request_id
            )
        )

    rejection_reason = request.form.get(
        "rejection_reason",
        ""
    ).strip()

    rejection_comment = request.form.get(
        "rejection_comment",
        ""
    ).strip()

    valid_reasons = {
        "unavailable",
        "schedule_conflict",
        "specimen_condition",
        "incomplete_request",
        "other"
    }

    if rejection_reason not in valid_reasons:

        return redirect(
            url_for(
                "requests.detail",
                id=request_id
            )
        )

    if (
        rejection_reason == "other"
        and not rejection_comment
    ):

        return redirect(
            url_for(
                "requests.detail",
                id=request_id
            )
        )

    item.item_status = "rejected"

    item.rejection_reason = (
        rejection_reason
    )

    item.rejection_comment = (
        rejection_comment or None
    )

    update_request_status(
        request_record
    )

    db.session.commit()

    return redirect(
        url_for(
            "requests.detail",
            id=request_id
        )
    )
