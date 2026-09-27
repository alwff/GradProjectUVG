from flaskr.models import (
    Specimen,
    Movement,
    MovementItem
)
from flaskr.services.rfid_reader import read_epc


def identify_specimen():

    epc = read_epc()

    if not epc:
        return None, "no_tag"

    specimen = Specimen.query.filter_by(
        rfid_epc=epc
    ).first()

    if specimen is None:
        return None, "unknown_epc"

    return specimen, "identified"

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