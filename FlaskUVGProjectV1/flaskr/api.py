from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
    send_from_directory
)
from flaskr.models import (
    Specimen,
    ExhibitionSlot,
    ExhibitionSettings
)
from flaskr.movements import find_specimen
from flaskr.extensions import db
from werkzeug.security import check_password_hash

from itsdangerous import (
    URLSafeTimedSerializer,
    BadSignature,
    SignatureExpired
)

from pathlib import Path

bp = Blueprint("api", __name__, url_prefix="/api")

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

def get_exhibition_serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt="exhibition-admin"
    )


def create_exhibition_token():
    serializer = get_exhibition_serializer()

    return serializer.dumps({
        "role": "exhibition_admin"
    })


def validate_exhibition_token(token):
    serializer = get_exhibition_serializer()

    try:
        data = serializer.loads(
            token,
            max_age=3600
        )

        return (
            data.get("role")
            == "exhibition_admin"
        )

    except (
        SignatureExpired,
        BadSignature
    ):
        return False

def get_bearer_token():

    authorization = request.headers.get(
        "Authorization",
        ""
    )

    if not authorization.startswith(
        "Bearer "
    ):
        return None

    return authorization[7:].strip()

def get_specimen_images(
    portal_code
):

    specimen_dir = (
        SPECIMEN_ASSETS_DIR
        / portal_code
    )

    if not specimen_dir.exists():
        return []


    def image_sort_key(filename):

        stem = Path(filename).stem

        if stem.isdigit():

            return (
                0,
                int(stem)
            )

        return (
            1,
            filename.lower()
        )


    return sorted(
        (
            file.name
            for file in specimen_dir.iterdir()
            if (
                file.is_file()
                and file.suffix.lower()
                in ALLOWED_IMAGE_EXTENSIONS
            )
        ),
        key=image_sort_key
    )

@bp.route(
    "/specimen/<identifier>",
    methods=["GET"]
)
def get_specimen(identifier):

    specimen = find_specimen(
        identifier
    )

    if specimen is None:

        return jsonify({
            "error": "Not found"
        }), 404


    image_files = get_specimen_images(
        specimen.portal_code
    )


    image_urls = [
        (
            request.host_url.rstrip("/")
            + "/api/specimen-assets/"
            + specimen.portal_code
            + "/"
            + filename
        )
        for filename in image_files
    ]


    return jsonify({
        "id":
            specimen.portal_code,

        "name":
            specimen.scientific_name,

        "description":
            specimen.description,

        "collection":
            specimen.collection,

        "status":
            specimen.status,

        "images":
            image_urls
    })

@bp.route(
    "/specimens",
    methods=["GET"]
)
def get_all_specimens():

    specimens = Specimen.query.order_by(
        Specimen.portal_code
    ).all()

    result = []

    for specimen in specimens:

        image_files = get_specimen_images(
            specimen.portal_code
        )

        if not image_files:
                    continue

        preview_url = (
            request.host_url.rstrip("/")
            + "/api/specimen-assets/"
            + specimen.portal_code
            + "/"
            + image_files[0]
        )

        result.append({
            "id":
                specimen.portal_code,

            "name":
                specimen.scientific_name,

            "collection":
                specimen.collection,

            "preview":
                preview_url
        })

    return jsonify(result)

@bp.route("/exhibition/config", methods=["GET"])
def get_exhibition_config():

    slots = ExhibitionSlot.query.order_by(
        ExhibitionSlot.slot_index
    ).all()

    result = [""] * 16

    for slot in slots:

        if 0 <= slot.slot_index < 16:

            if slot.specimen is not None:
                result[slot.slot_index] = (
                    slot.specimen.portal_code
                )

    return jsonify({
        "slots": result
    })

@bp.route("/exhibition/config", methods=["PUT"])
def save_exhibition_config():

    # -----------------------------------------
    # AUTORIZACION ADMINISTRATIVA
    # -----------------------------------------

    token = get_bearer_token()

    if (
        token is None
        or not validate_exhibition_token(token)
    ):
        return jsonify({
            "success": False,
            "error": "Unauthorized"
        }), 401


    # -----------------------------------------
    # CONFIGURACION DE LA GALERIA
    # -----------------------------------------

    data = request.get_json(silent=True)

    if not data or "slots" not in data:
        return jsonify({
            "error": "Invalid configuration"
        }), 400

    slots = data["slots"]

    if not isinstance(slots, list):
        return jsonify({
            "error": "Slots must be a list"
        }), 400

    if len(slots) != 16:
        return jsonify({
            "error": "Exactly 16 slots are required"
        }), 400

    try:

        for index, portal_code in enumerate(slots):

            exhibition_slot = ExhibitionSlot.query.filter_by(
                slot_index=index
            ).first()

            if exhibition_slot is None:

                exhibition_slot = ExhibitionSlot(
                    slot_index=index
                )

                db.session.add(exhibition_slot)

            if not portal_code:

                exhibition_slot.specimen_id = None
                continue

            specimen = Specimen.query.filter_by(
                portal_code=portal_code
            ).first()

            if specimen is None:
                db.session.rollback()

                return jsonify({
                    "error":
                        f"Specimen '{portal_code}' not found"
                }), 400

            exhibition_slot.specimen_id = specimen.id

        db.session.commit()

    except Exception:

        db.session.rollback()
        raise

    return jsonify({
        "success": True
    })

@bp.route("/exhibition/settings", methods=["GET"])
def get_exhibition_settings():

    settings = ExhibitionSettings.query.first()

    if settings is None:
        return jsonify({
            "wall_texture": None,
            "floor_texture": None,
            "ceiling_texture": None
        })

    def texture_url(filename):

        if not filename:
            return None

        return (
            request.host_url.rstrip("/")
            + "/assets/exhibition/textures/"
            + filename
        )

    return jsonify({
        "wall_texture":
            texture_url(settings.wall_texture),

        "floor_texture":
            texture_url(settings.floor_texture),

        "ceiling_texture":
            texture_url(settings.ceiling_texture)
    })

@bp.route(
    "/exhibition/auth",
    methods=["POST"]
)
def exhibition_auth():

    data = request.get_json(
        silent=True
    )

    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid request"
        }), 400

    password = data.get(
        "password",
        ""
    )

    settings = ExhibitionSettings.query.first()

    if (
        settings is None
        or not settings.admin_password
    ):
        return jsonify({
            "success": False,
            "error": "Administrative access is not configured"
        }), 503

    if not check_password_hash(
        settings.admin_password,
        password
    ):
        return jsonify({
            "success": False
        }), 401

    token = create_exhibition_token()

    return jsonify({
        "success": True,
        "token": token
    })

@bp.route(
    "/specimen-assets/<portal_code>/<path:filename>",
    methods=["GET"]
)
def specimen_asset(
    portal_code,
    filename
):

    specimen = Specimen.query.filter_by(
        portal_code=portal_code
    ).first()

    if specimen is None:

        return jsonify({
            "error": "Not found"
        }), 404


    specimen_dir = (
        SPECIMEN_ASSETS_DIR
        / specimen.portal_code
    )


    return send_from_directory(
        specimen_dir,
        filename
    )

