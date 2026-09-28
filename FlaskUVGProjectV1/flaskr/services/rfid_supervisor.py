from flaskr.models import (
    Specimen,
    Movement,
    MovementItem
)
from flaskr.services.rfid_reader import read_epc

def identify_specimen_by_epc(epc):

    if not epc:
        return None, "no_tag", None

    specimen = Specimen.query.filter_by(
        rfid_epc=epc
    ).first()

    if specimen is None:
        return None, "unknown_epc", epc

    return specimen, "identified", epc

def identify_specimen():

    epc = read_epc()

    return identify_specimen_by_epc(
        epc
    )

def get_latest_movement(specimen):

    movement = (
        Movement.query
        .join(MovementItem)
        .filter(
            MovementItem.specimen_id == specimen.id
        )
        .order_by(
            Movement.created_at.desc(),
            Movement.id.desc()
        )
        .first()
    )

    return movement

def classify_detection(specimen):

    movement = get_latest_movement(
        specimen
    )

    if movement is None:
        return {
            "status": "unauthorized",
            "reason": "no_movement",
            "movement": None
        }

    if (
        movement.movement_type == "exit"
        and specimen.status == "loaned"
    ):
        return {
            "status": "authorized",
            "reason": movement.source,
            "movement": movement
        }

    return {
        "status": "unauthorized",
        "reason": "no_active_exit",
        "movement": movement
    }

def supervise_epc(epc):

    specimen, identification_status, epc = (
        identify_specimen_by_epc(
            epc
        )
    )

    if identification_status == "no_tag":
        return {
            "status": "no_tag",
            "epc": None,
            "specimen": None,
            "reason": "no_tag",
            "movement": None
        }

    if identification_status == "unknown_epc":
        return {
            "status": "unknown_epc",
            "epc": epc,
            "specimen": None,
            "reason": "unknown_epc",
            "movement": None
        }

    classification = classify_detection(
        specimen
    )

    return {
        "status": classification["status"],
        "epc": epc,
        "specimen": specimen,
        "reason": classification["reason"],
        "movement": classification["movement"]
    }

def supervise_detection():

    epc = read_epc()

    return supervise_epc(
        epc
    )