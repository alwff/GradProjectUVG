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
    "/entry",
    methods=("GET", "POST")
)
@login_required
def entry():

    if request.method == "POST":

        specimen = find_specimen(
            request.form[
                "portal_code"
            ]
        )

        if specimen is None:

            flash(
                "Especímen no encontrado."
            )

            return redirect(
                url_for(
                    "movements.entry"
                )
            )

        if specimen.status == "available":

            flash(
                "El espécimen ya se encuentra disponible."
            )

            return redirect(
                url_for(
                    "movements.entry"
                )
            )

        create_movement(
            specimen,
            "entry",
            "manual",
            g.user.username,
            request.form["notes"]
        )

        specimen.status = (
            "available"
        )

        db.session.add(
            movement
        )

        db.session.commit()

        flash(
            "Entrada registrada."
        )

        return redirect(
            url_for(
                "movements.index"
            )
        )

    return render_template(
        "movements/entry.html"
    )

@bp.route(
    "/exit",
    methods=("GET", "POST")
)
@login_required
def exit():

    if request.method == "POST":

        specimen = find_specimen(
            request.form[
                "portal_code"
            ]
        )

        if specimen is None:

            flash(
                "Especímen no encontrado."
            )

            return redirect(
                url_for(
                    "movements.exit"
                )
            )
        
        if specimen.status == "loaned":

            flash(
                "El espécimen ya se encuentra prestado."
            )

            return redirect(
                url_for(
                    "movements.exit"
                )
            )

        create_movement(
            specimen,
            "exit",
            "manual",
            g.user.username,
            request.form["notes"]
        )

        specimen.status = (
            "loaned"
        )

        db.session.add(
            movement
        )

        db.session.commit()

        flash(
            "Salida registrada."
        )

        return redirect(
            url_for(
                "movements.index"
            )
        )

    return render_template(
        "movements/exit.html"
    )