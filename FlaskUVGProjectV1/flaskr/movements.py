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
    Specimen
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
    specimen,
    movement_type,
    source,
    username,
    notes
):

    movement = Movement(

        specimen_id=
            specimen.id,

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

        specimen,

        movement_type,

        "manual",

        g.user.username,

        request.form["notes"]

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
