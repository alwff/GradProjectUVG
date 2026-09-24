import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

from flaskr.auth import login_required
from flaskr.extensions import db
from flaskr.models import (
    ExhibitionSettings,
    PortalSettings
)

ALLOWED_TEXTURE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg"
}

TEXTURE_FIELDS = {
    "walls": "wall_texture",
    "floor": "floor_texture",
    "ceiling": "ceiling_texture"
}

def get_exhibition_settings():

    settings = ExhibitionSettings.query.first()

    if settings is None:
        settings = ExhibitionSettings()
        db.session.add(settings)
        db.session.commit()

    return settings

def get_portal_settings():

    settings = PortalSettings.query.first()

    if settings is None:

        settings = PortalSettings(
            request_instructions=(
                "El formulario debe llenarse y enviarse "
                "al menos una semana antes de necesitar "
                "el material.\n\n"
                "El catedrático es responsable de revisar "
                "el pedido antes de iniciar la práctica y "
                "de colaborar con el resguardo del material "
                "al finalizar la actividad."
            )
        )

        db.session.add(settings)
        db.session.commit()

    return settings

bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)

@bp.route("/")
@login_required
def index():
    return render_template(
        "dashboard/index.html"
    )

@bp.route("/exhibicion")
@login_required
def exhibition():

    settings = get_exhibition_settings()

    return render_template(
        "dashboard/exhibition.html",
        settings=settings
    )


# Subir texturas

@bp.route(
    "/exhibicion/textura/<surface>",
    methods=["POST"]
)
@login_required
def upload_exhibition_texture(surface):

    field_name = TEXTURE_FIELDS.get(surface)

    if field_name is None:
        flash("Superficie no válida.")
        return redirect(
            url_for("dashboard.exhibition")
        )

    file = request.files.get("texture")

    if file is None or file.filename == "":
        flash("Selecciona una imagen.")
        return redirect(
            url_for("dashboard.exhibition")
        )

    extension = (
        file.filename.rsplit(".", 1)[1].lower()
        if "." in file.filename
        else ""
    )

    if extension not in ALLOWED_TEXTURE_EXTENSIONS:
        flash(
            "Formato no permitido. "
            "Utiliza PNG, JPG o JPEG."
        )
        return redirect(
            url_for("dashboard.exhibition")
        )

    settings = get_exhibition_settings()

    filename = (
        f"{surface}_{uuid.uuid4().hex}.{extension}"
    )

    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    texture_dir = os.path.join(
        base_dir,
        "assets",
        "exhibition",
        "textures"
    )

    os.makedirs(
        texture_dir,
        exist_ok=True
    )

    file_path = os.path.join(
        texture_dir,
        secure_filename(filename)
    )

    file.save(file_path)

    old_texture = getattr(
        settings,
        field_name
    )

    setattr(
        settings,
        field_name,
        filename
    )

    db.session.commit()

    # Eliminar la textura personalizada anterior
    if old_texture:

        old_path = os.path.join(
            texture_dir,
            old_texture
        )

        if os.path.isfile(old_path):
            os.remove(old_path)

    flash("Textura actualizada correctamente.")

    return redirect(
        url_for("dashboard.exhibition")
    )

# Restaurar textura predeterminada

@bp.route(
    "/exhibicion/textura/<surface>/restaurar",
    methods=["POST"]
)
@login_required
def reset_exhibition_texture(surface):

    field_name = TEXTURE_FIELDS.get(surface)

    if field_name is None:
        flash("Superficie no válida.")
        return redirect(
            url_for("dashboard.exhibition")
        )

    settings = get_exhibition_settings()

    old_texture = getattr(
        settings,
        field_name
    )

    setattr(
        settings,
        field_name,
        None
    )

    db.session.commit()

    if old_texture:

        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        old_path = os.path.join(
            base_dir,
            "assets",
            "exhibition",
            "textures",
            old_texture
        )

        if os.path.isfile(old_path):
            os.remove(old_path)

    flash("Textura predeterminada restaurada.")

    return redirect(
        url_for("dashboard.exhibition")
    )

@bp.route(
    "/exhibicion/clave",
    methods=["POST"]
)
@login_required
def change_exhibition_password():

    password = request.form.get(
        "password",
        ""
    )

    confirmation = request.form.get(
        "confirmation",
        ""
    )

    if not password:
        flash("Ingresa una nueva clave.")

        return redirect(
            url_for("dashboard.exhibition")
        )

    if password != confirmation:
        flash("Las claves no coinciden.")

        return redirect(
            url_for("dashboard.exhibition")
        )

    if not password.isdigit():
        flash(
            "La clave debe contener únicamente números."
        )

        return redirect(
            url_for("dashboard.exhibition")
        )

    if len(password) < 4:
        flash(
            "La clave debe contener al menos 4 dígitos."
        )

        return redirect(
            url_for("dashboard.exhibition")
        )

    settings = get_exhibition_settings()

    settings.admin_password = (
        generate_password_hash(password)
    )

    db.session.commit()

    flash(
        "Clave administrativa actualizada correctamente."
    )

    return redirect(
        url_for("dashboard.exhibition")
    )

@bp.route(
    "/configuracion/portal",
    methods=["GET", "POST"]
)
@login_required
def portal_settings():

    settings = get_portal_settings()

    if request.method == "POST":

        instructions = request.form.get(
            "request_instructions",
            ""
        ).strip()

        if not instructions:

            flash(
                "Las indicaciones no pueden quedar vacías."
            )

            return redirect(
                url_for("dashboard.portal_settings")
            )

        settings.request_instructions = instructions

        db.session.commit()

        flash(
            "Configuración del portal actualizada correctamente."
        )

        return redirect(
            url_for("dashboard.portal_settings")
        )

    return render_template(
        "dashboard/portal_settings.html",
        settings=settings
    )