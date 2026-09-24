from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flaskr.auth import login_required

from flaskr.models import Specimen
from flaskr.extensions import db

from sqlalchemy import or_

bp = Blueprint(
    "inventory",
    __name__,
    url_prefix="/inventory"
)

@bp.route("/")
@login_required
def index():

    search = request.args.get(
        "search",
        ""
    ).strip()

    query = Specimen.query

    if search:

        query = query.filter(
            or_(
                Specimen.portal_code.ilike(
                    f"%{search}%"
                ),
                Specimen.barcode.ilike(
                    f"%{search}%"
                ),
                Specimen.rfid_epc.ilike(
                    f"%{search}%"
                )
            )
        )

    specimens = query.order_by(
        Specimen.portal_code
    ).all()

    return render_template(
        "inventory/index.html",
        specimens=specimens,
        search=search
    )

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():

    if request.method == "POST":

        specimen = Specimen(
            portal_code=request.form["portal_code"],
            catalog_number=request.form["catalog_number"],
            scientific_name=request.form["scientific_name"],
            taxon_family=request.form["taxon_family"],
            collection=request.form["collection"],
            rfid_epc=request.form["rfid_epc"],
            barcode=request.form["barcode"],
            description=request.form["description"]
        )

        db.session.add(specimen)
        db.session.commit()

        flash("Especímen creado correctamente.")

        return redirect(url_for("inventory.index"))

    return render_template("inventory/create.html")

@bp.route("/<int:id>")
@login_required
def detail(id):

    specimen = db.session.get(
        Specimen,
        id
    )

    if specimen is None:

        flash(
            "Especímen no encontrado."
        )

        return redirect(
            url_for("inventory.index")
        )

    return render_template(
        "inventory/detail.html",
        specimen=specimen
    )

@bp.route("/<int:id>/edit", methods=("GET", "POST"))
@login_required
def edit(id):

    specimen = db.session.get(
        Specimen,
        id
    )

    if specimen is None:
        flash("Especímen no encontrado.")
        return redirect(url_for("inventory.index"))

    if request.method == "POST":

        specimen.portal_code = request.form["portal_code"]
        specimen.catalog_number = request.form["catalog_number"]
        specimen.scientific_name = request.form["scientific_name"]
        specimen.taxon_family = request.form["taxon_family"]
        specimen.collection = request.form["collection"]
        specimen.rfid_epc = request.form["rfid_epc"]
        specimen.barcode = request.form["barcode"]
        specimen.description = request.form["description"]

        db.session.commit()

        flash("Especímen actualizado correctamente.")

        return redirect(url_for("inventory.index"))

    return render_template(
        "inventory/edit.html",
        specimen=specimen
    )