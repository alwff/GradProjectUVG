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

from pathlib import Path

from werkzeug.utils import secure_filename

bp = Blueprint(
    "inventory",
    __name__,
    url_prefix="/inventory"
)

SPECIMEN_ASSETS_DIR = (
    Path(__file__).resolve().parent
    / "assets"
    / "specimens"
)

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

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

@bp.route(
    "/<int:id>/images",
    methods=("GET", "POST")
)
@login_required
def images(id):

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


    specimen_dir = (
        SPECIMEN_ASSETS_DIR
        / specimen.portal_code
    )


    if request.method == "POST":

        uploaded_files = request.files.getlist(
            "images"
        )

        valid_files = []

        for uploaded_file in uploaded_files:

            if not uploaded_file.filename:
                continue

            extension = Path(
                secure_filename(
                    uploaded_file.filename
                )
            ).suffix.lower()

            if extension not in ALLOWED_IMAGE_EXTENSIONS:

                flash(
                    "Solo se permiten imágenes "
                    "JPG, JPEG, PNG o WEBP."
                )

                return redirect(
                    url_for(
                        "inventory.images",
                        id=specimen.id
                    )
                )

            valid_files.append(
                (
                    uploaded_file,
                    extension
                )
            )


        if not valid_files:

            flash(
                "Debes seleccionar al menos "
                "una imagen."
            )

            return redirect(
                url_for(
                    "inventory.images",
                    id=specimen.id
                )
            )


        specimen_dir.mkdir(
            parents=True,
            exist_ok=True
        )


        # La carga de una nueva secuencia reemplaza
        # completamente la secuencia anterior.
        for existing_file in specimen_dir.iterdir():

            if (
                existing_file.is_file()
                and existing_file.suffix.lower()
                in ALLOWED_IMAGE_EXTENSIONS
            ):

                existing_file.unlink()


        for index, (
            uploaded_file,
            extension
        ) in enumerate(
            valid_files,
            start=1
        ):

            filename = (
                f"{index:03d}"
                f"{extension}"
            )

            uploaded_file.save(
                specimen_dir / filename
            )


        flash(
            f"Secuencia 360 actualizada correctamente. "
            f"{len(valid_files)} imágenes cargadas."
        )

        return redirect(
            url_for(
                "inventory.images",
                id=specimen.id
            )
        )


    images = []

    if specimen_dir.exists():

        images = sorted(
            file.name
            for file in specimen_dir.iterdir()
            if (
                file.is_file()
                and file.suffix.lower()
                in ALLOWED_IMAGE_EXTENSIONS
            )
        )


    return render_template(
        "inventory/images.html",
        specimen=specimen,
        images=images
    )