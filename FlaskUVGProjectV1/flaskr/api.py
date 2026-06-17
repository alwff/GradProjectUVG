from flask import Blueprint, jsonify, url_for
from flaskr.models import Specimen
from flaskr.movements import find_specimen

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.route("/specimen/<identifier>", methods=["GET"])
def get_specimen(identifier):

    specimen = find_specimen(identifier)

    if specimen is None:
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "id": specimen.portal_code,
        "name": specimen.scientific_name,
        "description": specimen.description,
        "collection": specimen.collection,
        "status": specimen.status,

        # Imagenes
        "images": [
            url_for(
                'static',
                filename=f"specimens/{specimen.portal_code}/0.jpg",
                _external=True
            ),
            url_for(
                'static',
                filename=f"specimens/{specimen.portal_code}/1.jpg",
                _external=True
            )
        ]
    })