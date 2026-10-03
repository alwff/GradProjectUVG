# Despliegue y recuperación — UVG Collections

Este directorio contiene los archivos y procedimientos necesarios para
reconstruir el servidor de UVG Collections en caso de migración, reemplazo
o fallo de la laptop utilizada como servidor.

> **IMPORTANTE:** Los archivos de este directorio no contienen credenciales
> reales. Las contraseñas, claves privadas y API keys deben configurarse
> directamente en el servidor.

---

## 1. Arquitectura del servidor

El sistema utiliza una laptop Ubuntu como servidor principal.

En ella se ejecutan:

- Flask
- Gunicorn
- PostgreSQL
- Worker de supervisión RFID
- Unity WebGL
- ngrok
- Servicios systemd

La conexión física del lector RFID utiliza una interfaz Ethernet dedicada.

La arquitectura de conexión es:

```
Internet
   |
Wi-Fi / Hotspot
   |
   v
Laptop Ubuntu
├── Flask / Gunicorn
├── PostgreSQL
├── Worker RFID
├── Unity WebGL
└── ngrok
   |
   | Ethernet directo
   | 192.168.1.23/24
   |
   v
Yanzeo SR682
├── 192.168.1.116
└── TCP 49152
```

La interfaz Ethernet no utiliza gateway ni DNS. De esta forma, la comunicación
con el lector RFID permanece separada de la conexión utilizada para acceder a
Internet.

El acceso a Internet se realiza mediante Wi-Fi o un punto de acceso móvil y
se utiliza para servicios externos como Resend, ngrok y GitHub.

---

## 2. Estructura de despliegue

Los archivos versionados necesarios para reconstruir la configuración del
servidor se encuentran dentro del directorio `deploy/`.

La estructura actual es:

```
deploy/
├── database/
│   ├── backup-database.sh
│   ├── copy-backup-to-usb.sh
│   └── restore-database.sh
│
├── env/
│   └── uvgcollections.env.example
│
├── network/
│   └── setup-rfid-network.sh
│
├── ngrok/
│   ├── install-ngrok-service.sh
│   ├── ngrok.service
│   └── ngrok.yml.example
│
├── systemd/
│   ├── install-services.sh
│   ├── uvgcollections.service
│   └── uvg-rfid.service
│
└── README.md
```

Los respaldos reales de PostgreSQL se almacenan localmente en `backups/`.

La carpeta `backups/` está excluida del repositorio mediante `.gitignore`
para evitar que los datos de la base de datos sean publicados accidentalmente
en GitHub.

---

## 3. Configuración del hardware RFID

El lector RFID utilizado por el sistema tiene la siguiente configuración:

- **Modelo:** Yanzeo SR682
- **IP:** `192.168.1.116`
- **Puerto TCP:** `49152`
- **Alimentación:** 12 V

La laptop Ubuntu utiliza una conexión Ethernet dedicada para comunicarse con
el lector:

- **IPv4:** `192.168.1.23/24`
- **Gateway:** ninguno
- **DNS:** ninguno
- **Autoconnect:** habilitado

La conexión se realiza directamente mediante cable Ethernet entre la laptop
Ubuntu y el lector SR682. Por lo tanto, la comunicación RFID no requiere un
router.

La conexión Wi-Fi puede utilizarse simultáneamente para proporcionar acceso
a Internet sin interferir con la comunicación Ethernet del lector.

### Configurar la interfaz Ethernet

Primero identificar el nombre de la interfaz Ethernet:

```bash
ip -br link
```

Dependiendo del equipo, la interfaz puede llamarse `eno1`, `enp2s0`,
`enp3s0` u otro nombre similar.

Una vez identificada, ejecutar:

```bash
sudo ./deploy/network/setup-rfid-network.sh <interfaz>
```

Por ejemplo, en la laptop utilizada durante el desarrollo:

```bash
sudo ./deploy/network/setup-rfid-network.sh eno1
```

El script crea o actualiza automáticamente el perfil de NetworkManager
denominado `RFID` y configura la dirección `192.168.1.23/24`, sin gateway
ni DNS.

Para comprobar la ruta utilizada hacia el lector:

```bash
ip route get 192.168.1.116
```

La salida debe indicar que el tráfico utiliza la interfaz Ethernet configurada.

Por ejemplo:

```
192.168.1.116 dev eno1 src 192.168.1.23
```

También puede comprobarse la comunicación con el lector mediante:

```bash
ping -c 4 192.168.1.116
```

Una comunicación correcta debe presentar respuestas del lector y 0 % de
pérdida de paquetes.

---

## 4. Requisitos de una nueva instalación

La nueva máquina debe utilizar Ubuntu y disponer, como mínimo, de:

- Git
- Python 3.14 o una versión compatible con el proyecto
- soporte para entornos virtuales de Python
- PostgreSQL
- herramientas cliente de PostgreSQL
- NetworkManager
- acceso a Internet cuando se requieran servicios externos

### Clonar el repositorio

```bash
git clone https://github.com/alwff/GradProjectUVG.git
```

Ingresar al directorio de la aplicación:

```bash
cd GradProjectUVG/FlaskUVGProjectV1
```

### Preparar el entorno virtual de Python

Crear el entorno virtual:

```bash
python3 -m venv venv
```

Activarlo:

```bash
source venv/bin/activate
```

Actualizar `pip`:

```bash
python -m pip install --upgrade pip
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Instalar UVG Collections en modo editable:

```bash
pip install -e .
```

Comprobar la instalación:

```bash
pip list --editable
```

Debe aparecer `uvg-collections` asociado al directorio local
`FlaskUVGProjectV1`.

El proyecto utiliza `flaskr` como paquete principal de Python. Esta relación
se encuentra declarada en `pyproject.toml` mediante:

```toml
[tool.flit.module]
name = "flaskr"
```

### Comprobar la aplicación manualmente

Las terminales interactivas no cargan automáticamente las variables definidas
en `/etc/uvgcollections.env`.

Para cargarlas temporalmente:

```bash
set -a
source /etc/uvgcollections.env
set +a
```

Posteriormente puede comprobarse la creación de la aplicación:

```bash
python -c "from flaskr import create_app; app=create_app(); print('Import OK')"
```

La salida esperada es:

```
Import OK
```

Los servicios systemd no requieren ejecutar manualmente `source`, ya que
cargan `/etc/uvgcollections.env` mediante `EnvironmentFile`.

### Instalar y preparar PostgreSQL

Instalar PostgreSQL y sus herramientas cliente utilizando los paquetes
correspondientes de Ubuntu.

Comprobar la instalación mediante:

```bash
psql --version
pg_dump --version
pg_restore --version
```

La instalación utilizada durante el desarrollo emplea PostgreSQL 18.

El sistema utiliza actualmente el rol administrativo `postgres` para la
conexión local de Flask con la base de datos.

La configuración corresponde conceptualmente a:

```
Usuario: postgres
Host: localhost
Puerto: 5432
Base de datos: uvg_collections
```

La contraseña del usuario `postgres` no debe almacenarse en Git.

Para asignar o modificar la contraseña:

```bash
sudo -u postgres psql
```

Dentro de PostgreSQL:

```sql
\password postgres
```

PostgreSQL solicitará la nueva contraseña sin necesidad de escribirla
directamente dentro del comando.

Salir mediante:

```sql
\q
```

La variable `DATABASE_URL` almacenada en `/etc/uvgcollections.env` debe
utilizar la misma contraseña configurada para el rol `postgres`.

Su estructura es:

```
postgresql://postgres:<CONTRASEÑA>@localhost:5432/uvg_collections
```

No copiar una contraseña real al README ni al repositorio.

### Crear una base vacía

Si se realiza una instalación nueva sin restaurar inmediatamente un respaldo:

```bash
sudo -u postgres createdb uvg_collections
```

Comprobar su existencia:

```bash
sudo -u postgres psql -lqt | grep uvg_collections
```

### Recuperar una instalación existente

Si existe un respaldo de una instalación anterior, copiar el archivo `.dump`
a `backups/`.

Posteriormente utilizar:

```bash
sudo ./deploy/database/restore-database.sh backups/<archivo>.dump
```

El script crea nuevamente `uvg_collections` y restaura su estructura y datos.

### Verificar la conexión de Flask con PostgreSQL

Cargar las variables:

```bash
set -a
source /etc/uvgcollections.env
set +a
```

Activar el entorno virtual:

```bash
cd ~/GradProjectUVG/FlaskUVGProjectV1
source venv/bin/activate
```

Comprobar la conexión:

```bash
python -c "from flaskr import create_app; from flaskr.models import User; app=create_app(); ctx=app.app_context(); ctx.push(); print('PostgreSQL OK, usuarios:', User.query.count()); ctx.pop()"
```

La salida esperada tiene la forma:

```
PostgreSQL OK, usuarios: <cantidad>
```

---

## 5. Variables de entorno

Las credenciales y claves privadas utilizadas por el sistema no deben
almacenarse directamente en el repositorio.

El archivo de referencia se encuentra en:

`deploy/env/uvgcollections.env.example`

La configuración real debe almacenarse en:

`/etc/uvgcollections.env`

El archivo contiene:

```
DATABASE_URL=
SECRET_KEY=
MASTER_DELETE_PASSWORD=
RESEND_API_KEY=
```

Las variables tienen las siguientes funciones:

- `DATABASE_URL`: conexión utilizada por Flask para acceder a PostgreSQL.
- `SECRET_KEY`: clave utilizada por Flask para la gestión segura de sesiones.
- `MASTER_DELETE_PASSWORD`: contraseña maestra utilizada por las operaciones
  protegidas correspondientes.
- `RESEND_API_KEY`: credencial utilizada para el envío de correos mediante
  Resend.

> **Nunca deben copiarse las credenciales reales al repositorio Git.**

Los servicios `uvgcollections` y `uvg-rfid` cargan estas variables mediante:

```
EnvironmentFile=/etc/uvgcollections.env
```

Después de modificar `/etc/uvgcollections.env`, los servicios correspondientes
deben reiniciarse.

---

## 6. Servicios systemd

El sistema utiliza dos servicios principales para Flask y RFID.

### `uvgcollections.service`

Ejecuta la aplicación Flask mediante Gunicorn.

La configuración utilizada ejecuta Gunicorn con:

- 1 worker
- 2 threads
- puerto `8000`
- dirección `0.0.0.0`

El servicio utiliza el entorno virtual del proyecto y carga las variables
desde `/etc/uvgcollections.env`.

### `uvg-rfid.service`

Ejecuta permanentemente el worker RFID mediante:

```bash
python -u -m tools.rfid_worker
```

La opción `-u` mantiene la salida sin buffering y permite observar las
detecciones inmediatamente mediante `journalctl`.

### Instalar los servicios

Ejecutar:

```bash
sudo ./deploy/systemd/install-services.sh
```

El script:

1. identifica el usuario y grupo de la instalación;
2. detecta la ubicación real del repositorio y del entorno virtual;
3. comprueba la existencia de `/etc/uvgcollections.env`;
4. genera los servicios adaptados a la máquina actual en
   `/etc/systemd/system/`;
5. ejecuta `systemctl daemon-reload`;
6. habilita ambos servicios para iniciar automáticamente con Ubuntu.

Iniciar:

```bash
sudo systemctl start uvgcollections
sudo systemctl start uvg-rfid
```

Comprobar:

```bash
sudo systemctl status uvgcollections --no-pager
sudo systemctl status uvg-rfid --no-pager
```

Comprobación compacta:

```bash
systemctl is-active uvgcollections
systemctl is-active uvg-rfid
```

La respuesta esperada es `active`.

Para comprobar el inicio automático:

```bash
systemctl is-enabled uvgcollections
systemctl is-enabled uvg-rfid
```

La respuesta esperada es `enabled`.

### Observar el worker RFID

```bash
journalctl -u uvg-rfid -f
```

Para salir utilizar `Ctrl+C`.

### Portabilidad de los servicios

El instalador no depende del nombre de usuario `uvg-grad` ni de una ruta fija
dentro de `/home/`.

Detecta automáticamente:

- el usuario que ejecutó `sudo`;
- el grupo principal;
- la ubicación real del repositorio;
- el directorio `FlaskUVGProjectV1`;
- la ubicación del entorno virtual `venv`.

Por ejemplo, durante el desarrollo detectó:

```
Usuario:     uvg-grad
Grupo:       uvg-grad
Repositorio: /home/uvg-grad/GradProjectUVG
Aplicacion:  /home/uvg-grad/GradProjectUVG/FlaskUVGProjectV1
Entorno:     /home/uvg-grad/GradProjectUVG/FlaskUVGProjectV1/venv
```

Por lo tanto, el repositorio puede instalarse bajo otro usuario o en otra ruta
sin editar manualmente los archivos `.service`.

Antes de instalar los servicios deben existir:

- `FlaskUVGProjectV1/venv`;
- Gunicorn dentro del entorno virtual;
- `/etc/uvgcollections.env`.

Para comprobar los servicios generados:

```bash
sudo systemctl cat uvgcollections
sudo systemctl cat uvg-rfid
```

---

## 7. Respaldo de PostgreSQL

La base de datos utilizada por el sistema se denomina `uvg_collections`.

Crear un respaldo desde la raíz del repositorio:

```bash
./deploy/database/backup-database.sh
```

El script utiliza `pg_dump` en formato personalizado y genera un archivo
similar a:

```
backups/uvg_collections_2026-10-03_05-30-10.dump
```

Los respaldos incluyen estructura y datos y son compatibles con `pg_restore`.

El archivo local utiliza permisos restrictivos:

```
-rw-------
```

Listar respaldos:

```bash
ls -lh backups/
```

Comprobar el contenido lógico:

```bash
pg_restore -l backups/<archivo>.dump
```

### Respaldo externo en memoria USB

Mantener el respaldo únicamente en la laptop no protege frente a una falla
física de la unidad de almacenamiento.

Por ello debe mantenerse una segunda copia en una memoria USB.

El procedimiento recomendado es:

1. crear un respaldo actualizado;
2. conectar la memoria USB;
3. identificarla;
4. montarla si es necesario;
5. copiar el respaldo mediante el script;
6. verificar la copia;
7. desmontar la memoria correctamente.

Crear el respaldo:

```bash
./deploy/database/backup-database.sh
```

Identificar la memoria:

```bash
lsblk -f
```

Durante la prueba realizada se utilizó una memoria FAT32 con etiqueta `UVG`.

Si Ubuntu no la monta automáticamente, crear un punto de montaje:

```bash
sudo mkdir -p /media/$USER/UVG
```

Para una memoria FAT32 puede montarse asignando la propiedad al usuario actual:

```bash
sudo mount \
    -o uid=$(id -u),gid=$(id -g),umask=077 \
    /dev/sdb1 \
    /media/$USER/UVG
```

> `/dev/sdb1` es únicamente un ejemplo. Debe utilizarse el dispositivo
> identificado previamente mediante `lsblk -f`.

Comprobar que el usuario pueda escribir:

```bash
touch /media/$USER/UVG/prueba_escritura.txt
rm /media/$USER/UVG/prueba_escritura.txt
```

Copiar el respaldo más reciente:

```bash
./deploy/database/copy-backup-to-usb.sh \
    /media/$USER/UVG
```

El script:

- identifica automáticamente el respaldo más reciente;
- crea `UVG_Collections_Backups/` dentro de la memoria;
- copia el archivo `.dump`;
- ejecuta `sync`;
- compara la copia con el archivo original mediante `cmp`.

La estructura resultante es:

```
UVG/
└── UVG_Collections_Backups/
    └── uvg_collections_2026-10-03_05-30-10.dump
```

Después de la copia:

```bash
sync
sudo umount /media/$USER/UVG
```

La memoria puede retirarse físicamente después de desmontarla.

La memoria USB debe mantenerse separada de la laptop servidor cuando no esté
siendo utilizada.

---

## 8. Restauración de PostgreSQL

La restauración completa se realiza mediante:

```bash
sudo ./deploy/database/restore-database.sh backups/<archivo>.dump
```

Antes de reemplazar la base, el script solicita escribir:

```
RESTAURAR
```

En una restauración de producción:

1. detiene `uvg-rfid`;
2. detiene Flask/Gunicorn;
3. elimina `uvg_collections`;
4. crea nuevamente la base;
5. restaura el `.dump`;
6. inicia los servicios;
7. comprueba su estado.

### Prueba de restauración sin afectar producción

```bash
sudo env \
    DATABASE_NAME=uvg_collections_restore_test \
    ./deploy/database/restore-database.sh \
    backups/<archivo>.dump
```

Cuando se utiliza un nombre diferente de `uvg_collections`, los servicios de
producción no son detenidos.

Consultar las tablas restauradas:

```bash
sudo -u postgres psql \
    -d uvg_collections_restore_test \
    -c "\dt"
```

Eliminar posteriormente la base temporal:

```bash
sudo -u postgres dropdb uvg_collections_restore_test
```

### Validación realizada

El procedimiento fue probado restaurando una base temporal independiente.

Los registros comparados fueron:

| Información | Original | Restaurada |
|---|---:|---:|
| Especímenes | 1 | 1 |
| Movimientos | 18 | 18 |
| Eventos RFID | 33 | 33 |
| Solicitudes | 6 | 6 |
| Usuarios | 1 | 1 |

La coincidencia permitió comprobar la recuperación de la estructura y de los
datos almacenados.

---

## 9. Verificación del lector RFID

Comprobar conectividad:

```bash
ping -c 4 192.168.1.116
```

Comprobar ruta:

```bash
ip route get 192.168.1.116
```

La ruta debe utilizar la interfaz Ethernet dedicada.

Observar el worker:

```bash
journalctl -u uvg-rfid -f
```

Una lectura debe producir información similar a:

```
[DETECCION] <EPC>
Evento RFID: <ID>
Estado: <clasificacion>
```

Después del período de ausencia configurado:

```
[AUSENTE] <EPC>
```

---

## 10. Uso con Wi-Fi o hotspot móvil

Ethernet y Wi-Fi pueden utilizarse simultáneamente:

```
                    Internet
                       |
                 Wi-Fi / Hotspot
                       |
                       v
                 Laptop Ubuntu
                   /         \
                  /           \
         Servicios web      Ethernet
         Resend / ngrok        |
         GitHub                v
                         Yanzeo SR682
```

La interfaz Ethernet RFID no tiene gateway.

Esto permite utilizar:

- Ethernet directo para el SR682;
- Wi-Fi o hotspot para Internet;
- Resend para correo;
- ngrok para acceso externo;
- GitHub para sincronización.

Esta configuración fue comprobada físicamente utilizando un hotspot móvil
mientras el SR682 permanecía conectado directamente por Ethernet.

---

## 11. Acceso externo mediante ngrok

Ngrok proporciona acceso HTTPS externo a la aplicación Flask.

La relación es:

```
Flask / Gunicorn
localhost:8000
      |
      v
ngrok
      |
      v
HTTPS público
```

Los archivos de despliegue se encuentran en:

```
deploy/ngrok/
├── install-ngrok-service.sh
├── ngrok.service
└── ngrok.yml.example
```

### Configuración

El archivo real se almacena en:

`~/.config/ngrok/ngrok.yml`

La plantilla segura se encuentra en:

`deploy/ngrok/ngrok.yml.example`

El túnel utilizado se denomina `flask` y apunta al puerto local `8000`.

El archivo real contiene el `authtoken`.

> **El authtoken real nunca debe almacenarse en Git.**

Comprobar la configuración:

```bash
ngrok config check
```

### Servicio systemd

Ngrok se ejecuta mediante `ngrok.service` utilizando:

```bash
/usr/local/bin/ngrok start flask
```

Instalar el servicio:

```bash
sudo ./deploy/ngrok/install-ngrok-service.sh
```

El instalador detecta automáticamente el usuario y su directorio home,
comprueba la instalación de ngrok, valida `ngrok.yml`, genera el servicio y
lo habilita para iniciar automáticamente.

Iniciar:

```bash
sudo systemctl start ngrok
```

Reiniciar:

```bash
sudo systemctl restart ngrok
```

Comprobar:

```bash
sudo systemctl status ngrok --no-pager
systemctl is-active ngrok
systemctl is-enabled ngrok
```

Las dos últimas comprobaciones deben devolver:

```
active
enabled
```

El reinicio y recuperación automática del túnel fueron comprobados durante
el desarrollo.

---

## 12. Comandos de diagnóstico

### Estado de interfaces

```bash
ip -br addr
```

### Rutas

```bash
ip route
```

### Ruta hacia el SR682

```bash
ip route get 192.168.1.116
```

### Flask/Gunicorn

```bash
sudo systemctl status uvgcollections --no-pager
```

### Worker RFID

```bash
sudo systemctl status uvg-rfid --no-pager
```

### Logs RFID

```bash
journalctl -u uvg-rfid -f
```

### ngrok

```bash
sudo systemctl status ngrok --no-pager
```

### PostgreSQL

```bash
sudo -u postgres psql
```

Seleccionar la base:

```sql
\c uvg_collections
```

Salir:

```sql
\q
```

---

## 13. Seguridad

Las siguientes reglas deben mantenerse:

- no almacenar contraseñas directamente en el código;
- no subir `/etc/uvgcollections.env` a Git;
- no subir los respaldos PostgreSQL a Git;
- mantener las API keys como variables de entorno;
- mantener `SECRET_KEY` fuera del repositorio;
- mantener `MASTER_DELETE_PASSWORD` fuera del repositorio;
- mantener el authtoken de ngrok fuera del repositorio;
- utilizar permisos restrictivos para los `.dump`;
- proteger el acceso administrativo a PostgreSQL;
- mantener `/auth/register` protegido mediante autenticación.

Las credenciales que estuvieron presentes anteriormente en el historial Git
fueron reemplazadas durante el endurecimiento de la configuración.

Los valores actualmente utilizados por el servidor se almacenan fuera del
repositorio mediante `/etc/uvgcollections.env` y los archivos privados de
configuración correspondientes.

---

## 14. Resumen de recuperación

En caso de fallo o reemplazo de la laptop servidor:

1. instalar Ubuntu;
2. instalar Git, Python, PostgreSQL y NetworkManager;
3. clonar `GradProjectUVG`;
4. crear y activar `FlaskUVGProjectV1/venv`;
5. instalar `requirements.txt`;
6. ejecutar `pip install -e .`;
7. configurar la contraseña de PostgreSQL;
8. crear `/etc/uvgcollections.env`;
9. recuperar un `.dump` desde la memoria USB;
10. configurar Ethernet mediante `setup-rfid-network.sh`;
11. instalar los servicios mediante `install-services.sh`;
12. restaurar PostgreSQL mediante `restore-database.sh`;
13. iniciar y comprobar `uvgcollections`;
14. iniciar y comprobar `uvg-rfid`;
15. comprobar comunicación con `192.168.1.116`;
16. configurar `~/.config/ngrok/ngrok.yml` con el authtoken real;
17. instalar ngrok mediante `install-ngrok-service.sh`;
18. comprobar `ngrok.service`;
19. comprobar la interfaz web;
20. comprobar una lectura RFID física;
21. comprobar el envío de correo mediante Resend;
22. comprobar el acceso externo mediante ngrok;
23. crear un nuevo respaldo;
24. copiar el respaldo a la memoria USB y desmontarla correctamente.

Los scripts incluidos en `deploy/` reducen la cantidad de configuración manual
necesaria para reconstruir el servidor.