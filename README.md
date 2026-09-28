# Trabajo de Graduación: Diseño e implementación de una exhibición virtual para colecciones biológicas utilizando códigos de barras y entornos inmersivos 

Alejandra Cardona (22043)

## Propósito

Se busca la creación e implementación de una exhibición virtual en el entorno Unity medio que se vincula a una base de datos alimentada por un sistema de lectura de códigos de barra mediante un escáner. El propósito de esta exhibición es difundir las Colecciones Biológicas de la Universidad del Valle de Guatemala a través de un ambiente atractivo e interactivo. 

## ¿Cómo se divide el proyecto?
* Unity
* Base de Datos
  * Especímenes
    * Ingresados por el lector de códigos de barras.
    * Ingresados manualmente (parte de formularios).  
  * RFID
    * Tags RFID
    * Eventos (entradas y salidas)     
  * Formularios
    * Solicitudes (la persona interesada ingresa qué especímenes desea retirar de colecciones)
    * Préstamos (se llena por el encargado al hacer entrega del espécimen solicitado)
    * Devoluciones (se llena por el encargado al recibir el espécimen prestado)
    * Ingreso de espécimen manualmente (no cuenta con un código de barras asignado)
* Python + Flask
 * Implementación de notificaciones por correo para salidas y entradas a los encargados.   

## ¿Qué tengo ya y qué me falta?

* [x] Unity
* [x] Base de Datos
  * [ ] Especímenes
    * [ ] Ingresados por el lector de códigos de barras.
    * [x] Ingresados manualmente (parte de formularios).  
  * [ ] RFID
    * [ ] Tags RFID
    * [x] Eventos (entradas y salidas)     
  * [x] Formularios
    * [x] Solicitudes (la persona interesada ingresa qué especímenes desea retirar de colecciones)
    * [x] Préstamos (se llena por el encargado al hacer entrega del espécimen solicitado)
    * [x] Devoluciones (se llena por el encargado al recibir el espécimen prestado)
    * [x] Ingreso de espécimen manualmente (no cuenta con un código de barras asignado)
 * [ ] Python + Flask
  * [ ] Implementación de notificaciones por correo para salidas y entradas a los encargados.   
