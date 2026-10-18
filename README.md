# UVG Collections

**Sistema de gestión de colecciones biológicas y exhibición virtual interactiva**

Proyecto de graduación desarrollado para las Colecciones Biológicas de la Universidad del Valle de Guatemala (UVG).

## Descripción general

UVG Collections integra una plataforma web para administrar especímenes biológicos, gestionar solicitudes de material académico, registrar préstamos y devoluciones, supervisar identificaciones RFID y ofrecer una exhibición virtual interactiva desarrollada en Unity.

El sistema combina tecnologías de identificación, una base de datos relacional y una aplicación web para apoyar las actividades de gestión de las colecciones biológicas.

## Funcionalidades principales

### Inventario de especímenes

- Registro, consulta y actualización de especímenes.
- Identificación mediante códigos de barras y etiquetas RFID UHF.
- Almacenamiento de códigos del portal, números de catálogo e información taxonómica.
- Búsqueda y consulta de registros del inventario.

### Solicitudes y movimientos

- Formulario público para solicitar especímenes destinados a actividades académicas.
- Consulta del estado de las solicitudes mediante códigos de seguimiento.
- Revisión y administración de solicitudes por los encargados.
- Registro de préstamos, devoluciones y movimientos de especímenes.

### Supervisión RFID

- Lectura de etiquetas RFID UHF mediante el lector Yanzeo SR682 conectado por Ethernet.
- Identificación de especímenes y clasificación de detecciones.
- Registro de eventos en PostgreSQL.
- Alertas por correo ante movimientos no autorizados.
- Control de presencia para evitar registros repetidos por lecturas continuas.
- Recuperación automática de sesiones después de interrupciones temporales de PostgreSQL.

### Exhibición virtual

- Entorno interactivo desarrollado en Unity y publicado mediante WebGL.
- Recorrido virtual en primera persona.
- Visualización de especímenes mediante secuencias de imágenes de 360°.
- Integración con Flask para consultar información y cargar imágenes.
- Herramientas administrativas para configurar elementos de la exhibición.

## Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Aplicación web | Python y Flask |
| Base de datos | PostgreSQL |
| ORM y migraciones | SQLAlchemy, Flask-Migrate y Alembic |
| Servidor de aplicación | Gunicorn |
| Sistema operativo del servidor | Ubuntu |
| Administración de servicios | systemd |
| Acceso externo HTTPS | ngrok |
| Supervisión RFID | Yanzeo SR682, UHF EPC Gen2 |
| Lectura de códigos de barras | Zebra DS2208 |
| Exhibición virtual | Unity WebGL |
| Notificaciones | Resend |
| Control de versiones | Git y GitHub |

## Estructura del repositorio

```text
GradProjectUVG/
├── FlaskUVGProjectV1/
│   ├── flaskr/
│   ├── tools/
│   ├── migrations/
│   ├── tests/
│   └── README.md
├── deploy/
│   ├── database/
│   ├── env/
│   ├── network/
│   ├── ngrok/
│   ├── systemd/
│   └── README.md
├── UVGProject/
└── README.md
```

## Arquitectura general

El sistema utiliza una laptop Ubuntu como servidor principal.

Flask y Gunicorn proporcionan la aplicación web, mientras que PostgreSQL almacena los registros de especímenes, solicitudes, movimientos y detecciones RFID.

El lector Yanzeo SR682 se comunica con un worker Python mediante una conexión Ethernet dedicada. El worker procesa las detecciones y registra los eventos correspondientes en PostgreSQL.

La exhibición Unity WebGL se integra con Flask mediante servicios HTTP, sin acceder directamente a la base de datos.

El acceso externo a la plataforma se proporciona mediante ngrok.

## Documentación

- [Aplicación Flask](FlaskUVGProjectV1/README.md): estructura y desarrollo de la aplicación.
- [Despliegue y recuperación](deploy/README.md): instalación, configuración, servicios, respaldos, restauración y mantenimiento del servidor.

## Alcance

El proyecto constituye un prototipo funcional para apoyar la administración y supervisión de las colecciones biológicas de la UVG.

Su implementación contempla mecanismos de recuperación ante fallos temporales de PostgreSQL y control de detecciones RFID repetidas.

No incluye una cola persistente de eventos ni garantiza la entrega exactamente una vez de las notificaciones por correo.

Estas limitaciones forman parte del alcance definido para el prototipo.
