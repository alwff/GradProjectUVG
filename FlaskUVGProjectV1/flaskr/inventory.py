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

    family = request.args.get(
        "family",
        ""
    ).strip()

    collection = request.args.get(
        "collection",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()

    query = Specimen.query

    if search:

        search_term = f"%{search}%"

        query = query.filter(
            or_(
                Specimen.portal_code.ilike(
                    search_term
                ),
                Specimen.catalog_number.ilike(
                    search_term
                ),
                Specimen.scientific_name.ilike(
                    search_term
                ),
                Specimen.barcode.ilike(
                    search_term
                ),
                Specimen.rfid_epc.ilike(
                    search_term
                )
            )
        )

    if family:

        query = query.filter(
            Specimen.taxon_family.ilike(
                family
            )
        )

    if collection:

        query = query.filter(
            Specimen.collection.ilike(
                collection
            )
        )
    if status in (
        "available",
        "loaned"
    ):

        query = query.filter(
            Specimen.status
            == status
        )

    specimens = (
        query
        .order_by(
            Specimen.portal_code
        )
        .all()
    )

    families = (
        db.session.query(
            Specimen.taxon_family
        )
        .filter(
            Specimen.taxon_family.isnot(None),
            Specimen.taxon_family != ""
        )
        .distinct()
        .order_by(
            Specimen.taxon_family
        )
        .all()
    )

    collections = (
        db.session.query(
            Specimen.collection
        )
        .filter(
            Specimen.collection.isnot(None),
            Specimen.collection != ""
        )
        .distinct()
        .order_by(
            Specimen.collection
        )
        .all()
    )

    families = [
        value[0].strip()
        for value in families
        if value[0]
    ]

    collections = [
        value[0].strip()
        for value in collections
        if value[0]
    ]

    return render_template(
        "inventory/index.html",
        specimens=specimens,
        search=search,
        family=family,
        collection=collection,
        status=status,
        families=families,
        collections=collections
    )

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():

    if request.method == "POST":

        specimen = Specimen(
            portal_code=request.form[
                "portal_code"
            ].strip(),

            catalog_number=request.form[
                "catalog_number"
            ].strip(),

            scientific_name=request.form[
                "scientific_name"
            ].strip(),

            taxon_family=request.form[
                "taxon_family"
            ].strip(),

            collection=request.form[
                "collection"
            ].strip(),

            rfid_epc=request.form[
                "rfid_epc"
            ].strip().upper(),

            barcode=request.form[
                "barcode"
            ].strip(),

            description=request.form[
                "description"
            ].strip()
        )

        db.session.add(specimen)
        db.session.commit()

        flash("Espécimen creado correctamente.")

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
            "Espécimen no encontrado."
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
        flash("Espécimen no encontrado.")
        return redirect(url_for("inventory.index"))

    if request.method == "POST":

        specimen.portal_code = (
            request.form["portal_code"]
            .strip()
        )

        specimen.catalog_number = (
            request.form["catalog_number"]
            .strip()
        )

        specimen.scientific_name = (
            request.form["scientific_name"]
            .strip()
        )

        specimen.taxon_family = (
            request.form["taxon_family"]
            .strip()
        )

        specimen.collection = (
            request.form["collection"]
            .strip()
        )

        specimen.rfid_epc = (
            request.form["rfid_epc"]
            .strip()
            .upper()
        )

        specimen.barcode = (
            request.form["barcode"]
            .strip()
        )

        specimen.description = (
            request.form["description"]
            .strip()
        )

        db.session.commit()

        flash("Espécimen actualizado correctamente.")

        return redirect(url_for("inventory.index"))

    return render_template(
        "inventory/edit.html",
        specimen=specimen
    )