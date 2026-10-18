# UVG Collections — Aplicación Flask

Aplicación web desarrollada en Python y Flask para la gestión de las Colecciones Biológicas de la Universidad del Valle de Guatemala.

Este directorio contiene la aplicación principal, los modelos de datos, los servicios de integración, el worker RFID y las migraciones de PostgreSQL.

## 1. Funcionalidades

La aplicación implementa:

- Autenticación y administración de usuarios.
- Inventario de especímenes biológicos.
- Identificación mediante códigos de barras y RFID.
- Solicitudes públicas de material académico y consulta de su estado.
- Administración de solicitudes, préstamos, devoluciones y movimientos.
- Registro y supervisión de detecciones RFID.
- Alertas por correo ante movimientos no autorizados.
- API para la integración con Unity WebGL.
- Configuración administrativa de la exhibición virtual.

## 2. Estructura del proyecto

```text
FlaskUVGProjectV1/
├── flaskr/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   ├── services/
│   ├── templates/
│   └── static/
├── tools/
│   └── rfid_worker.py
├── migrations/
│   └── versions/
├── tests/
├── instance/
├── pyproject.toml
├── requirements.txt
└── README.md
```

El paquete `flaskr` contiene la aplicación Flask, sus rutas, modelos y servicios.

El directorio `tools/` contiene procesos auxiliares, incluyendo el worker de supervisión RFID.

Las migraciones de la base de datos se administran mediante Flask-Migrate y Alembic.

## 3. Tecnologías

- Python 3.14.
- Flask y Flask-SQLAlchemy.
- PostgreSQL.
- Flask-Migrate y Alembic.
- Flask-Login.
- Gunicorn.
- Resend para notificaciones.
- Flask-CORS para las rutas de integración correspondientes.

Las dependencias se encuentran declaradas en `pyproject.toml` y `requirements.txt`.

## 4. Preparación del entorno

Desde el directorio `FlaskUVGProjectV1`, crear un entorno virtual:

```bash
python3 -m venv venv
```

Activarlo en Ubuntu:

```bash
source venv/bin/activate
```

O en Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
pip install -e .
```

## 5. Configuración de PostgreSQL

La aplicación utiliza la variable de entorno `DATABASE_URL` para conectarse a PostgreSQL.

Las credenciales reales no deben almacenarse en el repositorio.

En Ubuntu, la configuración de producción se encuentra en:

`/etc/uvgcollections.env`

Los servicios systemd cargan este archivo mediante `EnvironmentFile`.

Para utilizar comandos de Flask manualmente en el servidor:

```bash
set -a
source /etc/uvgcollections.env
set +a
```

Para el desarrollo local debe configurarse una base de datos independiente, evitando utilizar directamente la base de producción.

## 6. Migraciones de la base de datos

Las modificaciones de los modelos se administran mediante Alembic.

Consultar la revisión actual:

```bash
flask --app flaskr db current
```

Consultar las migraciones disponibles:

```bash
flask --app flaskr db history
```

Aplicar migraciones pendientes:

```bash
flask --app flaskr db upgrade
```

Antes de ejecutar una migración en producción debe realizarse un respaldo verificado y seguirse el procedimiento de despliegue documentado.

La migración `a7f3c91d204e` incorporó la columna `detection_key` para identificar operaciones RFID mediante UUID.

## 7. Worker RFID

El proceso de supervisión RFID se encuentra en:

`tools/rfid_worker.py`

Puede ejecutarse manualmente desde el directorio de la aplicación mediante:

```bash
python -u -m tools.rfid_worker
```

El worker se comunica con el lector Yanzeo SR682 mediante Ethernet, utilizando `10.77.0.2:49152`.

Sus funciones incluyen:

- Lectura y clasificación de EPC.
- Registro de eventos RFID.
- Control de presencia mediante un umbral de ausencia de 10 segundos.
- Alertas por movimientos no autorizados.
- Cooldown de 300 segundos por EPC para el envío de alertas.
- Recuperación de sesiones SQLAlchemy después de errores de conexión.
- Identificación de operaciones mediante UUID para reducir registros duplicados.

En producción, el worker se ejecuta mediante `uvg-rfid.service`. No debe iniciarse simultáneamente otra instancia manual que compita por la conexión del lector.

## 8. Integración con Unity WebGL

La aplicación proporciona rutas HTTP y una API para integrar la exhibición virtual desarrollada en Unity.

Unity obtiene la información y las imágenes de los especímenes mediante Flask.

La exhibición no establece conexiones directas con PostgreSQL.

Los archivos WebGL se sirven desde los recursos estáticos de la aplicación.

## 9. Limitaciones conocidas

Los identificadores de detecciones pendientes se conservan únicamente en memoria durante la ejecución del worker.

No se implementa una cola persistente de eventos, por lo que una operación pendiente puede perderse ante un reinicio abrupto.

El envío de correos y la confirmación de su estado en PostgreSQL no constituyen una transacción única. Por ello, el sistema no garantiza la entrega exactamente una vez de las notificaciones.

Estas limitaciones forman parte del alcance definido para el prototipo.

## 10. Documentación adicional

- [Descripción general del proyecto](../README.md).
- [Despliegue, servicios y recuperación](../deploy/README.md).

Para instalar o reconstruir el servidor Ubuntu, configurar el lector RFID, gestionar los servicios systemd y realizar respaldos de PostgreSQL, consultar la documentación de despliegue.
