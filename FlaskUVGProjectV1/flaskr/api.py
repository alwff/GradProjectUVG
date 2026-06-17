from flask import Blueprint, jsonify
from flaskr.models import Specimen
from flaskr.movements import find_specimen

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.route("/specimen/<identifier>", methods=["GET"])
def get_specimen(identifier):

    specimen = find_specimen(identifier)

    if specimen is None:
        return jsonify({"error": "Not found"}), 404

    base_url = f"http://127.0.0.1:5000/assets/specimens/{specimen.portal_code}"

    return jsonify({
        "id": specimen.portal_code,
        "name": specimen.scientific_name,
        "description": specimen.description,
        "collection": specimen.collection,
        "status": specimen.status,

        # 🔥 ahora usando assets (no static)
        "images": [
            f"{base_url}/0.jpg",
            f"{base_url}/1.jpg"
        ]
    })