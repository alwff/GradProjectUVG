from datetime import (
    datetime,
    timezone
)

from zoneinfo import ZoneInfo

from sqlalchemy import or_

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    g
)

from flaskr.auth import login_required

from flaskr.extensions import db

from flaskr.models import (
    Movement,
    MovementItem,
    Specimen,
    Request,
    RFIDDetectionEvent
)

GUATEMALA_TZ = ZoneInfo(
    "America/Guatemala"
)

bp = Blueprint(
    "movements",
    __name__,
    url_prefix="/movements"
)

def find_specimen(identifier):

    specimen = Specimen.query.filter_by(
        portal_code=identifier
    ).first()

    if specimen:
        return specimen

    specimen = Specimen.query.filter_by(
        barcode=identifier
    ).first()

    if specimen:
        return specimen

    specimen = Specimen.query.filter_by(
        rfid_epc=identifier
    ).first()

    return specimen

def specimen_has_request_exit(
    request_id,
    specimen_id
):

    movement = (
        Movement.query
        .join(MovementItem)
        .filter(
            Movement.request_id == request_id,
            Movement.movement_type == "exit",
            MovementItem.specimen_id == specimen_id
        )
        .first()
    )

    return movement is not None

def specimen_has_request_entry(
    request_id,
    specimen_id
):

    movement = (
        Movement.query
        .join(MovementItem)
        .filter(
            Movement.request_id == request_id,
            Movement.movement_type == "entry",
            MovementItem.specimen_id == specimen_id
        )
        .first()
    )

    return movement is not None

def create_movement(
    specimens,
    movement_type,
    source,
    username,
    notes,
    request_record=None
):

    movement = Movement(

        request_id=(
            request_record.id
            if request_record
            else None
        ),

        movement_type=
            movement_type,

        source=
            source,

        performed_by=
            username,

        notes=
            notes
    )

    db.session.add(
        movement
    )

    db.session.flush()

    for specimen in specimens:

        movement_item = MovementItem(

            movement_id=
                movement.id,

            specimen_id=
                specimen.id
        )

        db.session.add(
            movement_item
        )

    return movement

def update_request_return_status(
    request_record
):

    approved_items = [
        item
        for item in request_record.items
        if item.item_status == "approved"
    ]

    if not approved_items:
        return


    for item in approved_items:

        was_delivered = (
            specimen_has_request_exit(
                request_record.id,
                item.specimen_id
            )
        )

        # Todavía existe material aprobado
        # que nunca fue entregado.
        if not was_delivered:
            return

        was_returned = (
            specimen_has_request_entry(
                request_record.id,
                item.specimen_id
            )
        )

        if not was_returned:
            return


    request_record.status = "returned"

@bp.route("/")
@login_required
def index():

    movements = Movement.query.order_by(
        Movement.created_at.desc()
    ).all()

    return render_template(
        "movements/index.html",
        movements=movements
    )

@bp.route("/rfid")
@login_required
def rfid_history():

    search = request.args.get(
        "search",
        ""
    ).strip()

    classification = request.args.get(
        "classification",
        "all"
    ).strip()

    query = RFIDDetectionEvent.query

    if search:

        search_term = f"%{search}%"

        query = (
            query
            .outerjoin(
                Specimen,
                RFIDDetectionEvent.specimen_id
                == Specimen.id
            )
            .filter(
                or_(
                    RFIDDetectionEvent.epc.ilike(
                        search_term
                    ),
                    Specimen.portal_code.ilike(
                        search_term
                    ),
                    Specimen.scientific_name.ilike(
                        search_term
                    )
                )
            )
        )

    allowed_classifications = {
        "authorized",
        "unauthorized",
        "unknown_epc"
    }

    if classification in allowed_classifications:

        query = query.filter(
            RFIDDetectionEvent.classification
            == classification
        )

    events = (
        query
        .order_by(
            RFIDDetectionEvent.detected_at.desc()
        )
        .all()
    )

    now_local = datetime.now(
        GUATEMALA_TZ
    )

    today_start_local = now_local.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    today_start = (
        today_start_local
        .astimezone(timezone.utc)
    )

    detections_today = (
        RFIDDetectionEvent.query
        .filter(
            RFIDDetectionEvent.detected_at
            >= today_start
        )
        .count()
    )

    unauthorized_today = (
        RFIDDetectionEvent.query
        .filter(
            RFIDDetectionEvent.detected_at
            >= today_start,
            RFIDDetectionEvent.classification
            == "unauthorized"
        )
        .count()
    )

    unknown_today = (
        RFIDDetectionEvent.query
        .filter(
            RFIDDetectionEvent.detected_at
            >= today_start,
            RFIDDetectionEvent.classification
            == "unknown_epc"
        )
        .count()
    )

    alerts_today = (
        RFIDDetectionEvent.query
        .filter(
            RFIDDetectionEvent.alert_sent.is_(True),
            RFIDDetectionEvent.alert_sent_at
            >= today_start
        )
        .count()
    )

    def to_local_time(value):

        if value is None:
            return None

        return value.astimezone(
            GUATEMALA_TZ
        )

    return render_template(
        "movements/rfid_history.html",
        events=events,
        search=search,
        classification=classification,
        detections_today=detections_today,
        unauthorized_today=unauthorized_today,
        unknown_today=unknown_today,
        alerts_today=alerts_today,
        to_local_time=to_local_time
    )

@bp.route(
    "/register",
    methods=("GET", "POST")
)
@login_required
def register():

    specimen = None

    if request.method == "POST":

        identifier = request.form[
            "identifier"
        ]

        specimen = find_specimen(
            identifier
        )

        if specimen is None:

            flash(
                "Espécimen no encontrado."
            )

    return render_template(
        "movements/register.html",
        specimen=specimen
    )

@bp.route(
    "/request/<int:request_id>/delivery",
    methods=("GET",)
)
@login_required
def request_delivery(request_id):

    request_record = (
        Request.query.get_or_404(
            request_id
        )
    )

    if request_record.status not in (
        "approved",
        "partially_approved"
    ):

        flash(
            "La solicitud todavía no tiene "
            "material aprobado para entregar."
        )

        return redirect(
            url_for(
                "requests.detail",
                id=request_record.id
            )
        )


    pending_delivery = []
    already_delivered = []
    unavailable_delivery = []


    for item in request_record.items:

        if item.item_status != "approved":
            continue


        was_delivered = (
            specimen_has_request_exit(
                request_record.id,
                item.specimen_id
            )
        )


        if was_delivered:

            already_delivered.append(
                item
            )

        elif item.specimen.status == "available":

            pending_delivery.append(
                item
            )

        else:

            unavailable_delivery.append(
                item
            )


    return render_template(
        "movements/request_delivery.html",
        request_record=request_record,
        approved_items=pending_delivery,
        already_delivered=already_delivered,
        unavailable_items=unavailable_delivery
    )

@bp.route(
    "/request/<int:request_id>/delivery/process",
    methods=("POST",)
)
@login_required
def process_request_delivery(request_id):

    request_record = (
        Request.query.get_or_404(
            request_id
        )
    )

    if request_record.status not in (
        "approved",
        "partially_approved"
    ):

        flash(
            "Esta solicitud no permite "
            "registrar una entrega."
        )

        return redirect(
            url_for(
                "requests.detail",
                id=request_id
            )
        )

    specimen_ids = request.form.getlist(
        "specimen_ids"
    )

    if not specimen_ids:

        flash(
            "Debes seleccionar al menos "
            "un espécimen."
        )

        return redirect(
            url_for(
                "movements.request_delivery",
                request_id=request_id
            )
        )


    approved_specimen_ids = {
        item.specimen_id
        for item in request_record.items
        if item.item_status == "approved"
    }


    specimens = (
        Specimen.query
        .filter(
            Specimen.id.in_(
                specimen_ids
            )
        )
        .all()
    )


    if len(specimens) != len(specimen_ids):

        flash(
            "Uno o más especímenes "
            "seleccionados no existen."
        )

        return redirect(
            url_for(
                "movements.request_delivery",
                request_id=request_id
            )
        )


    for specimen in specimens:

        if (
            specimen.id
            not in approved_specimen_ids
        ):

            flash(
                "Uno de los especímenes "
                "seleccionados no pertenece "
                "a los materiales aprobados."
            )

            return redirect(
                url_for(
                    "movements.request_delivery",
                    request_id=request_id
                )
            )

        if specimen_has_request_exit(
            request_record.id,
            specimen.id
        ):

            flash(
                f"{specimen.portal_code} ya registra "
                "una entrega para esta solicitud."
            )

            return redirect(
                url_for(
                    "movements.request_delivery",
                    request_id=request_id
                )
            )

        if specimen.status != "available":

            flash(
                f"{specimen.portal_code} "
                "ya no se encuentra disponible."
            )

            return redirect(
                url_for(
                    "movements.request_delivery",
                    request_id=request_id
                )
            )


    for specimen in specimens:

        specimen.status = "loaned"


    create_movement(
        specimens,
        "exit",
        "request",
        g.user.username,
        request.form.get(
            "notes",
            ""
        ).strip(),
        request_record=request_record
    )


    db.session.commit()


    flash(
        "Entrega registrada correctamente."
    )

    return redirect(
        url_for(
            "movements.index"
        )
    )

@bp.route(
    "/process",
    methods=("POST",)
)
@login_required
def process():

    specimen = Specimen.query.get_or_404(
        request.form["specimen_id"]
    )

    movement_type = request.form[
        "movement_type"
    ]

    if movement_type == "entry":

        specimen.status = (
            "available"
        )

    elif movement_type == "exit":

        specimen.status = (
            "loaned"
        )

    create_movement(

        [specimen],

        movement_type,

        "manual",

        g.user.username,

        request.form.get(
            "notes",
            ""
        )
    )

    db.session.commit()

    flash(
        "Movimiento registrado correctamente."
    )

    return redirect(
        url_for(
            "movements.index"
        )
    )


@bp.route(
    "/request/<int:request_id>/return",
    methods=("GET",)
)
@login_required
def request_return(request_id):

    request_record = (
        Request.query.get_or_404(
            request_id
        )
    )

    returnable_items = []

    for item in request_record.items:

        if item.item_status != "approved":
            continue

        was_delivered = (
            specimen_has_request_exit(
                request_record.id,
                item.specimen_id
            )
        )

        was_returned = (
            specimen_has_request_entry(
                request_record.id,
                item.specimen_id
            )
        )

        if (
            was_delivered
            and not was_returned
            and item.specimen.status == "loaned"
        ):

            returnable_items.append(
                item
            )


    return render_template(
        "movements/request_return.html",
        request_record=request_record,
        returnable_items=returnable_items
    )

@bp.route(
    "/request/<int:request_id>/return/process",
    methods=("POST",)
)
@login_required
def process_request_return(request_id):

    request_record = (
        Request.query.get_or_404(
            request_id
        )
    )

    specimen_ids = request.form.getlist(
        "specimen_ids"
    )

    if not specimen_ids:

        flash(
            "Debes seleccionar al menos "
            "un espécimen."
        )

        return redirect(
            url_for(
                "movements.request_return",
                request_id=request_id
            )
        )


    approved_specimen_ids = {
        item.specimen_id
        for item in request_record.items
        if item.item_status == "approved"
    }


    specimens = (
        Specimen.query
        .filter(
            Specimen.id.in_(
                specimen_ids
            )
        )
        .all()
    )


    if len(specimens) != len(specimen_ids):

        flash(
            "Uno o más especímenes "
            "seleccionados no existen."
        )

        return redirect(
            url_for(
                "movements.request_return",
                request_id=request_id
            )
        )


    for specimen in specimens:

        if specimen.id not in approved_specimen_ids:

            flash(
                "Uno de los especímenes no pertenece "
                "a los materiales aprobados."
            )

            return redirect(
                url_for(
                    "movements.request_return",
                    request_id=request_id
                )
            )


        if not specimen_has_request_exit(
            request_record.id,
            specimen.id
        ):

            flash(
                f"{specimen.portal_code} no registra "
                "una salida para esta solicitud."
            )

            return redirect(
                url_for(
                    "movements.request_return",
                    request_id=request_id
                )
            )

        if specimen_has_request_entry(
            request_record.id,
            specimen.id
        ):

            flash(
                f"{specimen.portal_code} ya registra "
                "una devolución para esta solicitud."
            )

            return redirect(
                url_for(
                    "movements.request_return",
                    request_id=request_id
                )
            )

        if specimen.status != "loaned":

            flash(
                f"{specimen.portal_code} no figura "
                "actualmente como prestado."
            )

            return redirect(
                url_for(
                    "movements.request_return",
                    request_id=request_id
                )
            )


    for specimen in specimens:

        specimen.status = "available"


    create_movement(
        specimens,
        "entry",
        "request",
        g.user.username,
        request.form.get(
            "notes",
            ""
        ).strip(),
        request_record=request_record
    )


    db.session.flush()


    update_request_return_status(
        request_record
    )


    db.session.commit()


    flash(
        "Devolución registrada correctamente."
    )

    return redirect(
        url_for(
            "movements.index"
        )
    )