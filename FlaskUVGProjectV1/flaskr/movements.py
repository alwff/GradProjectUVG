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
    Request
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
                "Especímen no encontrado."
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

    approved_items = [
        item
        for item in request_record.items
        if (
            item.item_status == "approved"
            and item.specimen.status == "available"
        )
    ]

    return render_template(
        "movements/request_delivery.html",
        request_record=request_record,
        approved_items=approved_items
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
