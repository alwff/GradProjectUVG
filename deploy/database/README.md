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
└── Unity WebGL
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
se utiliza para servicios externos como Resend y ngrok.

---

## 2. Estructura de despliegue

Los archivos versionados necesarios para reconstruir la configuración del
servidor se encuentran dentro del directorio `deploy/`.

La estructura actual es:

```
deploy/
├── database/
│   ├── backup-database.sh
│   └── restore-database.sh
│
├── env/
│   └── uvgcollections.env.example
│
├── network/
│   └── setup-rfid-network.sh
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
- Python 3
- soporte para entornos virtuales de Python
- PostgreSQL
- herramientas cliente de PostgreSQL
- NetworkManager
- acceso a Internet cuando se requieran servicios externos

Clonar el repositorio:

```bash
git clone https://github.com/alwff/GradProjectUVG.git
```

Ingresar al proyecto:

```bash
cd GradProjectUVG
```

La instalación de las dependencias de Python y la preparación del entorno
virtual deben realizarse antes de instalar los servicios systemd.

---

## 5. Variables de entorno

Las credenciales y claves privadas utilizadas por el sistema no deben
almacenarse directamente en el repositorio.

El archivo de referencia se encuentra en
`deploy/env/uvgcollections.env.example`.

La configuración real del servidor debe almacenarse en:

`/etc/uvgcollections.env`

El archivo debe contener:

```
DATABASE_URL=
SECRET_KEY=
MASTER_DELETE_PASSWORD=
RESEND_API_KEY=
```

Las variables tienen las siguientes funciones:

- `DATABASE_URL`: contiene la cadena de conexión utilizada por Flask para
  acceder a PostgreSQL.
- `SECRET_KEY`: contiene la clave utilizada por Flask para la gestión segura
  de sesiones.
- `MASTER_DELETE_PASSWORD`: contiene la contraseña maestra utilizada por las
  operaciones protegidas correspondientes.
- `RESEND_API_KEY`: contiene la credencial utilizada para el envío de correos
  mediante Resend.

Los valores reales deben configurarse únicamente en el servidor.

> **Nunca deben copiarse las credenciales reales al repositorio Git.**

Los servicios `uvgcollections` y `uvg-rfid` cargan estas variables mediante:

```
EnvironmentFile=/etc/uvgcollections.env
```

Después de modificar `/etc/uvgcollections.env`, los servicios correspondientes
deben reiniciarse para cargar nuevamente la configuración.

---

## 6. Servicios systemd

El sistema utiliza dos servicios principales.

### `uvgcollections.service`

Ejecuta la aplicación Flask mediante Gunicorn.

La configuración utilizada durante el desarrollo ejecuta Gunicorn con:

- 1 worker
- 2 threads
- puerto `8000`
- dirección `0.0.0.0`

El servicio utiliza el entorno virtual ubicado dentro del proyecto y carga las
variables desde `/etc/uvgcollections.env`.

### `uvg-rfid.service`

Ejecuta permanentemente el worker de supervisión RFID mediante:

```bash
python -u -m tools.rfid_worker
```

La opción `-u` mantiene la salida de Python sin buffering, permitiendo observar
las detecciones RFID en tiempo real mediante `journalctl`.

### Instalar los servicios

Los archivos utilizados por systemd se encuentran en `deploy/systemd/`.

Para instalarlos ejecutar:

```bash
sudo ./deploy/systemd/install-services.sh
```

El script:

1. comprueba la existencia de los archivos de servicio;
2. comprueba la existencia de `/etc/uvgcollections.env`;
3. copia los servicios a `/etc/systemd/system/`;
4. ejecuta `systemctl daemon-reload`;
5. habilita ambos servicios para iniciar automáticamente con Ubuntu.

Después de la instalación pueden iniciarse mediante:

```bash
sudo systemctl start uvgcollections
sudo systemctl start uvg-rfid
```

Para comprobar su estado:

```bash
sudo systemctl status uvgcollections --no-pager
sudo systemctl status uvg-rfid --no-pager
```

También puede comprobarse de forma compacta:

```bash
systemctl is-active uvgcollections
systemctl is-active uvg-rfid
```

La respuesta esperada para ambos es:

```
active
```

Para comprobar si inician automáticamente con Ubuntu:

```bash
systemctl is-enabled uvgcollections
systemctl is-enabled uvg-rfid
```

La respuesta esperada es:

```
enabled
```

### Observar el worker RFID

Para visualizar las detecciones y mensajes del supervisor RFID en tiempo real:

```bash
journalctl -u uvg-rfid -f
```

Para salir de la visualización utilizar `Ctrl+C`.

---

## 7. Respaldo de PostgreSQL

La base de datos utilizada por el sistema se denomina `uvg_collections`.

Para crear un respaldo ejecutar, desde la raíz del repositorio:

```bash
./deploy/database/backup-database.sh
```

El script utiliza `pg_dump` en formato personalizado de PostgreSQL y genera
un archivo con un nombre similar a:

```
backups/uvg_collections_2026-10-03_05-30-10.dump
```

Los archivos generados utilizan el formato `CUSTOM` de PostgreSQL, compatible
con `pg_restore`.

Los respaldos incluyen la estructura y los datos necesarios para reconstruir
la base de datos.

El script asigna permisos restrictivos al archivo generado:

```
-rw-------
```

De esta forma, únicamente el propietario puede leer o modificar directamente
el respaldo.

Para listar los respaldos existentes:

```bash
ls -lh backups/
```

Para comprobar el contenido lógico de un respaldo sin restaurarlo:

```bash
pg_restore -l backups/<archivo>.dump
```

### Importante

La carpeta `backups/` está excluida de Git.

Por lo tanto, los archivos `.dump` deben copiarse adicionalmente a un medio
externo seguro si se desea protección frente a una falla física de la laptop
o de su unidad de almacenamiento.

Mantener un respaldo únicamente dentro de la misma laptop no protege frente
a la pérdida física del equipo o de su almacenamiento.

---

## 8. Restauración de PostgreSQL

La restauración completa puede realizarse mediante:

```bash
sudo ./deploy/database/restore-database.sh backups/<archivo>.dump
```

Antes de reemplazar la base de datos, el script solicita escribir:

```
RESTAURAR
```

como confirmación explícita.

En una restauración de producción, el procedimiento:

1. detiene el servicio de supervisión RFID;
2. detiene el servidor Flask/Gunicorn;
3. elimina la base `uvg_collections` existente;
4. crea nuevamente la base de datos;
5. restaura el archivo `.dump`;
6. inicia nuevamente los servicios;
7. comprueba el estado de los servicios.

### Prueba de restauración sin afectar producción

El script permite restaurar un respaldo en una base temporal:

```bash
sudo env \
    DATABASE_NAME=uvg_collections_restore_test \
    ./deploy/database/restore-database.sh \
    backups/<archivo>.dump
```

Cuando se utiliza un nombre de base diferente de `uvg_collections`, los
servicios de producción no son detenidos.

Esto permite comprobar la integridad de un respaldo sin modificar la base
utilizada por Flask.

Para consultar las tablas de la base restaurada:

```bash
sudo -u postgres psql \
    -d uvg_collections_restore_test \
    -c "\dt"
```

La base temporal puede eliminarse posteriormente mediante:

```bash
sudo -u postgres dropdb uvg_collections_restore_test
```

### Validación realizada

El procedimiento de respaldo y restauración fue comprobado utilizando una
base temporal independiente.

Durante la prueba se restauraron correctamente las tablas del sistema y se
compararon registros críticos entre la base original y la restaurada.

Los resultados obtenidos fueron:

| Información | Original | Restaurada |
|---|---:|---:|
| Especímenes | 1 | 1 |
| Movimientos | 18 | 18 |
| Eventos RFID | 33 | 33 |
| Solicitudes | 6 | 6 |
| Usuarios | 1 | 1 |

La coincidencia de estos registros permitió verificar que el procedimiento
recuperó correctamente tanto la estructura como los datos almacenados.

---

## 9. Verificación del lector RFID

Una vez configurada la red y arrancado `uvg-rfid.service`, comprobar primero
la conectividad:

```bash
ping -c 4 192.168.1.116
```

Luego comprobar la ruta:

```bash
ip route get 192.168.1.116
```

La ruta debe utilizar la interfaz Ethernet dedicada.

Posteriormente observar el worker:

```bash
journalctl -u uvg-rfid -f
```

Al acercar un tag al lector debe aparecer una detección similar a:

```
[DETECCION] <EPC>
Evento RFID: <ID>
Estado: <clasificacion>
```

Cuando el tag deja de ser detectado durante el período configurado debe
aparecer:

```
[AUSENTE] <EPC>
```

---

## 10. Uso con Wi-Fi o hotspot móvil

La conexión Ethernet utilizada por RFID y la conexión Wi-Fi pueden funcionar
simultáneamente.

La configuración recomendada es:

```
                    Internet
                       |
                Wi-Fi / Hotspot
                       |
                       v
                Laptop Ubuntu
                  /         \
                 /           \
        Flask / Resend      Ethernet
        ngrok / GitHub         |
                               v
                         Yanzeo SR682
```

La interfaz Ethernet RFID no tiene gateway, por lo que no intenta utilizarse
como salida a Internet.

Esto permite utilizar:

- Ethernet directo para la comunicación con el SR682.
- Wi-Fi o hotspot móvil para acceso a Internet.
- Resend para correos electrónicos.
- ngrok para acceso externo.
- GitHub para sincronización del proyecto.

Esta configuración fue comprobada utilizando un hotspot de datos móviles
mientras el lector RFID permanecía conectado directamente por Ethernet a la
laptop Ubuntu.

---

## 11. Comandos de diagnóstico

### Estado de interfaces de red

```bash
ip -br addr
```

### Rutas de red

```bash
ip route
```

### Ruta específica hacia el SR682

```bash
ip route get 192.168.1.116
```

### Estado de Flask/Gunicorn

```bash
sudo systemctl status uvgcollections --no-pager
```

### Estado del worker RFID

```bash
sudo systemctl status uvg-rfid --no-pager
```

### Logs RFID en tiempo real

```bash
journalctl -u uvg-rfid -f
```

### Acceso a PostgreSQL

```bash
sudo -u postgres psql
```

Dentro de PostgreSQL:

```sql
\c uvg_collections
```

Para salir:

```sql
\q
```

---

## 12. Seguridad

Las siguientes reglas deben mantenerse en cualquier instalación:

- No almacenar contraseñas directamente en el código fuente.
- No subir `/etc/uvgcollections.env` a Git.
- No subir los respaldos de PostgreSQL a Git.
- Mantener las API keys únicamente como variables de entorno.
- Mantener `SECRET_KEY` fuera del repositorio.
- Mantener `MASTER_DELETE_PASSWORD` fuera del repositorio.
- Utilizar permisos restrictivos para los archivos `.dump`.
- Proteger el acceso al usuario administrador de PostgreSQL.
- Mantener `/auth/register` protegido mediante autenticación.

Las credenciales que hayan sido expuestas previamente en el historial Git
deben considerarse comprometidas y deben ser reemplazadas.

---

## Resumen de recuperación

En caso de fallo o reemplazo de la laptop servidor, el procedimiento general
será:

1. instalar Ubuntu;
2. instalar Git, Python, PostgreSQL y NetworkManager;
3. clonar `GradProjectUVG`;
4. preparar el entorno virtual de Python;
5. instalar las dependencias del proyecto;
6. configurar PostgreSQL;
7. copiar un respaldo `.dump` externo a `backups/`;
8. crear `/etc/uvgcollections.env`;
9. configurar la interfaz Ethernet mediante `setup-rfid-network.sh`;
10. instalar los servicios mediante `install-services.sh`;
11. restaurar PostgreSQL mediante `restore-database.sh`;
12. iniciar y comprobar `uvgcollections`;
13. iniciar y comprobar `uvg-rfid`;
14. comprobar comunicación con `192.168.1.116`;
15. comprobar la interfaz web;
16. comprobar una lectura RFID física;
17. comprobar los servicios externos necesarios.

Los scripts incluidos en `deploy/` fueron creados para reducir la cantidad de
configuración manual necesaria durante este procedimiento.