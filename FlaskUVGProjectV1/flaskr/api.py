from flask import Blueprint, jsonify, request
from flaskr.models import Specimen, ExhibitionSlot
from flaskr.movements import find_specimen
from flaskr.extensions import db

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.route("/specimen/<identifier>", methods=["GET"])
def get_specimen(identifier):

    specimen = find_specimen(identifier)

    if specimen is None:
        return jsonify({"error": "Not found"}), 404

    base_url = request.host_url + f"assets/specimens/{specimen.portal_code}"

    return jsonify({
        "id": specimen.portal_code,
        "name": specimen.scientific_name,
        "description": specimen.description,
        "collection": specimen.collection,
        "status": specimen.status,

        "images": [
            f"{base_url}/1.png",
            f"{base_url}/2.png"
        ]
    })

@bp.route("/specimens", methods=["GET"])
def get_all_specimens():
    specimens = Specimen.query.all()

    return jsonify([
    {
        "id": s.portal_code,
        "name": s.scientific_name,
        "collection": s.collection
    }
    for s in specimens
    
    ])

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