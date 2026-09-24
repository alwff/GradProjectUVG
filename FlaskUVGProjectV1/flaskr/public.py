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
    PortalSettings
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

    if request.method == "POST":

        items = session["request_items"]

        items.append({

            "portal_code":
                request.form["portal_code"],

            "species_or_family":
                request.form["species_or_family"],

            "specifications":
                request.form["specifications"]

        })

        session["request_items"] = items

    settings = get_portal_settings()

    return render_template(
        "public/request_items.html",
        request_data=request_data,
        request_items=session["request_items"],
        settings=settings
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

    # Crear Request

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
            ).time()
            if request_data["start_time"]
            else None,

        end_time=
            datetime.strptime(
                request_data["end_time"],
                "%H:%M"
            ).time()
            if request_data["end_time"]
            else None,

        status="pending"

    )

    db.session.add(
        new_request
    )

    db.session.commit()

    # Generar tracking code

    tracking_code = (
        f"UVG-{date.today().year}-"
        f"{new_request.id:05d}"
    )

    new_request.tracking_code = (
        tracking_code
    )

    db.session.commit()

    # Crear RequestItems

    for item in request_items:

        request_item = RequestItem(

            request_id=
                new_request.id,

            portal_code=
                item["portal_code"],

            species_or_family=
                item["species_or_family"],

            specifications=
                item["specifications"]

        )

        db.session.add(
            request_item
        )

    db.session.commit()

    # Limpiar sesión

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

@bp.route(
    "/request/status",
    methods=("GET", "POST")
)
def request_status():

    request_record = None

    if request.method == "POST":

        tracking_code = request.form[
            "tracking_code"
        ]

        request_record = Request.query.filter_by(
            tracking_code=tracking_code
        ).first()

    return render_template(
        "public/request_status.html",
        request_record=request_record
    )
