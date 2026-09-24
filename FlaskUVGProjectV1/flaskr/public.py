from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    url_for
)

from datetime import date, datetime

from flaskr.models import (
    Request,
    RequestItem,
    PortalSettings,
    Specimen
)

from flaskr.extensions import db

bp = Blueprint(
    "public",
    __name__
)

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

def get_specimen_conflict(
    specimen_id,
    needed_date,
    return_date,
    start_time,
    end_time
):

    requested_start = datetime.strptime(
        f"{needed_date} {start_time}",
        "%Y-%m-%d %H:%M"
    )

    requested_end = datetime.strptime(
        f"{return_date} {end_time}",
        "%Y-%m-%d %H:%M"
    )

    approved_items = (
        RequestItem.query
        .join(Request)
        .filter(
            RequestItem.specimen_id == specimen_id,
            RequestItem.item_status == "approved"
        )
        .all()
    )

    for item in approved_items:

        existing_start = datetime.combine(
            item.request.needed_date,
            item.request.start_time
        )

        existing_end = datetime.combine(
            item.request.return_date,
            item.request.end_time
        )

        if (
            requested_start < existing_end
            and requested_end > existing_start
        ):
            return item

    return None

@bp.route("/")
def home():
    return render_template(
        "public/home.html"
    )

@bp.route(
    "/request/create",
    methods=("GET", "POST")
)
def create_request():

    if request.method == "POST":

        needed_date = request.form.get(
            "needed_date",
            ""
        )

        return_date = request.form.get(
            "return_date",
            ""
        )

        start_time = request.form.get(
            "start_time",
            ""
        )

        end_time = request.form.get(
            "end_time",
            ""
        )

        if (
            not needed_date
            or not return_date
            or not start_time
            or not end_time
        ):

            return render_template(
                "public/request_create.html",
                current_date=date.today(),
                settings=get_portal_settings(),
                error=(
                    "Debes indicar las fechas y horas "
                    "de uso y devolución."
                )
            )

        try:

            start_datetime = datetime.strptime(
                f"{needed_date} {start_time}",
                "%Y-%m-%d %H:%M"
            )

            end_datetime = datetime.strptime(
                f"{return_date} {end_time}",
                "%Y-%m-%d %H:%M"
            )
            

        except ValueError:

            return render_template(
                "public/request_create.html",
                current_date=date.today(),
                settings=get_portal_settings(),
                error=(
                    "Las fechas u horas ingresadas "
                    "no son válidas."
                )
            )

        now = datetime.now()

        if start_datetime < now:

            return render_template(
                "public/request_create.html",
                current_date=date.today(),
                settings=get_portal_settings(),
                error=(
                    "La fecha y hora de uso no puede "
                    "ser anterior al momento actual."
                )
            )

        if end_datetime <= start_datetime:

            return render_template(
                "public/request_create.html",
                current_date=date.today(),
                settings=get_portal_settings(),
                error=(
                    "La fecha y hora de devolución "
                    "debe ser posterior a la fecha "
                    "y hora de uso."
                )
            )

        session["request_data"] = {

            "teacher_name":
                request.form["teacher_name"],

            "course":
                request.form["course"],

            "assistant":
                request.form["assistant"],

            "request_date":
                str(date.today()),

            "needed_date":
                needed_date,

            "return_date":
                return_date,

            "start_time":
                start_time,

            "end_time":
                end_time

        }

        session["request_items"] = []

        return redirect(
            url_for("public.request_items")
        )

    settings = get_portal_settings()

    return render_template(
        "public/request_create.html",
        current_date=date.today(),
        settings=settings
    )

@bp.route(
    "/request/items",
    methods=("GET", "POST")
)
def request_items():

    request_data = session.get(
        "request_data"
    )

    if request_data is None:

        return redirect(
            url_for("public.create_request")
        )

    if "request_items" not in session:
        session["request_items"] = []

    selected_specimen = None
    availability_error = None
    conflict = None

    if request.method == "POST":

        action = request.form.get(
            "action"
        )

        portal_code = request.form.get(
            "portal_code",
            ""
        ).strip()

        if not portal_code:

            availability_error = (
                "Ingresa un código de portal."
            )

        else:

            selected_specimen = (
                Specimen.query.filter_by(
                    portal_code=portal_code
                ).first()
            )

            if selected_specimen is None:

                availability_error = (
                    "No se encontró ningún espécimen "
                    "con ese código de portal."
                )

            else:

                conflict = get_specimen_conflict(
                    selected_specimen.id,
                    request_data["needed_date"],
                    request_data["return_date"],
                    request_data["start_time"],
                    request_data["end_time"]
                )

                if action == "add":

                    if conflict:

                        availability_error = (
                            "El espécimen ya no está "
                            "disponible para el período "
                            "seleccionado."
                        )

                    else:

                        items = session[
                            "request_items"
                        ]

                        already_added = any(
                            item["specimen_id"]
                            == selected_specimen.id
                            for item in items
                        )

                        if already_added:

                            availability_error = (
                                "Este espécimen ya fue "
                                "agregado a la solicitud."
                            )

                        else:

                            species_or_family = (
                                selected_specimen.scientific_name
                                or selected_specimen.taxon_family
                                or "—"
                            )

                            items.append({
                                "specimen_id":
                                    selected_specimen.id,

                                "portal_code":
                                    selected_specimen.portal_code,

                                "species_or_family":
                                    species_or_family,

                                "specifications":
                                    request.form.get(
                                        "specifications",
                                        ""
                                    ).strip()
                            })

                            session[
                                "request_items"
                            ] = items

                            selected_specimen = None
                            conflict = None

    settings = get_portal_settings()

    return render_template(
        "public/request_items.html",
        request_data=request_data,
        request_items=session["request_items"],
        settings=settings,
        selected_specimen=selected_specimen,
        availability_error=availability_error,
        conflict=conflict
    )

@bp.route(
    "/request/submit",
    methods=("POST",)
)
def submit_request():

    request_data = session.get(
        "request_data"
    )

    request_items = session.get(
        "request_items",
        []
    )

    if request_data is None:

        return redirect(
            url_for("public.create_request")
        )

    if not request_items:

        return redirect(
            url_for("public.request_items")
        )

    for item in request_items:

        conflict = get_specimen_conflict(
            item["specimen_id"],
            request_data["needed_date"],
            request_data["return_date"],
            request_data["start_time"],
            request_data["end_time"]
        )

        if conflict:

            return redirect(
                url_for("public.request_items")
            )

    new_request = Request(

        teacher_name=
            request_data["teacher_name"],

        course=
            request_data["course"],

        assistant=
            request_data["assistant"],

        request_date=
            datetime.strptime(
                request_data["request_date"],
                "%Y-%m-%d"
            ).date(),

        needed_date=
            datetime.strptime(
                request_data["needed_date"],
                "%Y-%m-%d"
            ).date(),

        return_date=
            datetime.strptime(
                request_data["return_date"],
                "%Y-%m-%d"
            ).date(),

        start_time=
            datetime.strptime(
                request_data["start_time"],
                "%H:%M"
            ).time(),

        end_time=
            datetime.strptime(
                request_data["end_time"],
                "%H:%M"
            ).time(),

        status="pending"
    )

    db.session.add(
        new_request
    )

    # Necesitamos el ID antes del commit,
    # pero seguimos dentro de la misma transacción.
    db.session.flush()

    tracking_code = (
        f"UVG-{date.today().year}-"
        f"{new_request.id:05d}"
    )

    new_request.tracking_code = (
        tracking_code
    )


    for item in request_items:

        request_item = RequestItem(

            request_id=
                new_request.id,

            specimen_id=
                item["specimen_id"],

            portal_code=
                item["portal_code"],

            species_or_family=
                item["species_or_family"],

            specifications=
                item["specifications"],

            item_status="pending"
        )

        db.session.add(
            request_item
        )


    db.session.commit()


    session.pop(
        "request_data",
        None
    )

    session.pop(
        "request_items",
        None
    )


    return render_template(
        "public/request_success.html",
        tracking_code=
            tracking_code
    )