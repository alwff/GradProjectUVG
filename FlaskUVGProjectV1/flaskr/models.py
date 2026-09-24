from .extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

class PortalSettings(db.Model):
    __tablename__ = "portal_settings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    request_instructions = db.Column(
        db.Text,
        nullable=True
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

class Specimen(db.Model):
    __tablename__ = "specimens"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Código utilizado actualmente en el Portal de Biodiversidad
    portal_code = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    # Código interno de catálogo de la colección
    catalog_number = db.Column(
        db.String(100),
        unique=True
    )

    # Nombre científico completo
    scientific_name = db.Column(
        db.String(255),
        nullable=False
    )

    # Familia taxonómica
    taxon_family = db.Column(
        db.String(255)
    )

    # Colección a la que pertenece
    collection = db.Column(
        db.String(100),
        nullable=False
    )

    # EPC de la etiqueta RFID UHF
    rfid_epc = db.Column(
        db.String(255),
        unique=True
    )

    # Código leído por el escáner Zebra
    barcode = db.Column(
        db.String(255),
        unique=True
    )

    # Estado actual del espécimen
    status = db.Column(
        db.String(50),
        nullable=False,
        default="available"
    )

    # Observaciones generales
    description = db.Column(
        db.Text
    )

    # Fecha de incorporación al sistema
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

class Request(db.Model):
    __tablename__ = "requests"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    tracking_code = db.Column(
    db.String(50),
    unique=True
    )

    teacher_name = db.Column(
        db.String(255),
        nullable=False
    )

    course = db.Column(
        db.String(255),
        nullable=False
    )

    assistant = db.Column(
        db.String(255)
    )

    request_date = db.Column(
        db.Date,
        nullable=False
    )

    needed_date = db.Column(
        db.Date,
        nullable=False
    )

    return_date = db.Column(
        db.Date,
        nullable=False
    )

    start_time = db.Column(
        db.Time
    )

    end_time = db.Column(
        db.Time
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="pending"
    )

    status_notes = db.Column(
    db.Text
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    items = db.relationship(
    "RequestItem",
    backref="request",
    lazy=True,
    cascade="all, delete-orphan"
    )



class RequestItem(db.Model):
    __tablename__ = "request_items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    request_id = db.Column(
        db.Integer,
        db.ForeignKey("requests.id"),
        nullable=False
    )

    portal_code = db.Column(
        db.String(100)
    )

    species_or_family = db.Column(
        db.String(255),
        nullable=False
    )

    specifications = db.Column(
        db.Text
    )

class Movement(db.Model):

    __tablename__ = "movements"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    specimen_id = db.Column(
        db.Integer,
        db.ForeignKey("specimens.id"),
        nullable=False
    )

    specimen = db.relationship(
    "Specimen"
    )

    movement_type = db.Column(
        db.String(20),
        nullable=False
    )

    source = db.Column(
    db.String(20),
    nullable=False,
    default="manual"
    )

    performed_by = db.Column(
        db.String(80),
        nullable=False
    )

    notes = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

class ExhibitionSlot(db.Model):

    __tablename__ = "exhibition_slots"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    slot_index = db.Column(
        db.Integer,
        unique=True,
        nullable=False
    )

    specimen_id = db.Column(
        db.Integer,
        db.ForeignKey("specimens.id"),
        nullable=True
    )

    specimen = db.relationship(
        "Specimen"
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

class ExhibitionSettings(db.Model):

    __tablename__ = "exhibition_settings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    wall_texture = db.Column(
        db.String(500),
        nullable=True
    )

    floor_texture = db.Column(
        db.String(500),
        nullable=True
    )

    ceiling_texture = db.Column(
        db.String(500),
        nullable=True
    )

    admin_password = db.Column(
        db.String(255),
        nullable=True
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )