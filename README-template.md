# ST0263 Tópicos Especiales en Telemática

# Estudiante(s):

- Manuela Castaño - mcastanof1@eafit.edu.co
- Miguel Vásquez - mvasquezb@eafit.edu.co
- Manuel Villegas - mvillegas6@eafit.edu.co

# Profesor:

- Edwin Montoya - emontoya@eafit.edu.co

# Diseño e Implementación de un Middleware orientado a mensajes

# 1. breve descripción de la actividad

El estudiante debe construir un sistema distribuido en clúster que soporte:

- Autenticación de usuarios.
- Creación, eliminación y listado de colas y tópicos.
- Envío y recepción de mensajes mediante estos canales.
- Comunicación REST entre cliente y servidor, y gRPC entre servidores.
- Funcionalidades como replicación, particionamiento, y tolerancia a fallos inspiradas en sistemas como Apache Kafka.

Además, se debe desarrollar una aplicación cliente de prueba, documentar todo el sistema, desplegarlo en AWS Academy, y presentar los resultados.

## 1.1. Que aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

### Funcionales

- Gestión de la conexión de clientes: El sistema debe permitir a múltiples clientes autenticarse, conectarse y desconectarse del MOM, ya sea de forma persistente (con estado) o sin mantener una conexión constante (sin estado).
- Autenticación y Autorización: Los usuarios deben autenticarse antes de interactuar con el sistema.
- Gestión del Ciclo de Vida de Tópicos: El sistema debe permitir la creación de tópicos, la eliminación de tópicos únicamente por parte del usuario que los creó, y listar todos los tópicos disponibles.
- Gestión del Ciclo de Vida de Colas: El sistema debe permitir la creación de colas, la eliminación de colas únicamente por parte del usuario que las creó, y listar todas las colas disponibles.
- Envío y Recepción de Mensajes: El sistema debe permitir enviar mensajes a una cola o tópico en específico, así como también recibir mensajes desde una cola o tópico.
- Modelo de Suscripción: El sistema debe ofrecer un modelo de suscripción a las colas y tópicos tanto por tipo push como tipo pull.
- API REST y gRPC: El sistema debe exponer servicios a los clientes a través de API REST, mientras que la comunicación entre servidores MOM es por medio de gRPC.
- Persistencia de Datos: El sistema debe implementar un mecanismo de persistencia para asegurar que los mensajes y configuraciones no se pierdan ante una falla.

### No Funcionales

- Seguridad: Las credenciales de autenticación deben ser transmitidas mediante mecanismos de cifrado.
- Tolerancia a fallos: El sistema debe ser capaz de recuperarse de fallos de algún nodo mediante replicación de datos y mecanismos de respaldo.
- Escalabilidad: La arquitectura del sistema debe permitir la incorporación de nuevos nodos al cluster sin afectar la funcionalidad existente.
- Particionamiento y Replicación: El sistema debe distribuir las colas y tópicos, además de otra información, entre diferentes nodos del cluster, además de replicar esta información.
- Transparencia: El sistema debe ser transparente, es decir, los clientes no deben saber los detalles internos del cluster, como la ubicación de los tópicos o colas. Además, el uso del sistema debe ser homogéneo, independientemente del nodo al que se conecte el cliente.
- Desempeño y Eficiencia: El sistema debe responder en tiempos aceptables ante operaciones de envío y recepción de mensajes.
- Mantenibilidad: La arquitectura debe permitir la inclusión de nuevas funcionalidades sin necesidad de una reestructuración completa.
- Multiusuario: El sistema debe soportar la conexión concurrente de múltiples usuarios, garantizando la correcta identificación y separación de sus recursos y mensajes.
- Modelo de Comunicación Distribuida: El sistema debe soportar interacciones sincrónicas y asincrónicas.

## 1.2. Que aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

### Funcionales

- Manejo de wildcards como "\*" y "#" para el manejo de grupos de mensajes por medio de expresiones regulares
- Implementacion de un ttl de los elementos
- Manejo del status de los mensajes de manera eficiente

### No Funcionales

- Mejora de kos tiempos de busqueda entre los servidores (no utilizar busqueda lineal)
- Uso de elementos como el ZooKeeper de manera mas eficiente
- Mayor calidad y cantidad de pruebas de integracion entre componentes

# 2. información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.

**IMAGEN ARQUITECTURA**

## Documentación Cliente

El cliente es el encargado del uso de los servidores MOM para el envío y recepción de mensajes tanto por colas como por tópicos, este cliente mantiene una comunicación API REST con los servidores donde se envían y/o reciben las peticiones pertinentes. El cliente mantiene un mecanismo de pull hacia el servidor donde le pide constantemente los mensajes al servidor.

El cliente va a tener la posibilidad de realizar distintas tareas, entre las más importantes tenemos el registro y logueo de nuevos usuarios, creación, envío y recepción de mensajes tanto de tópicos como de colas, esto a través de una interfaz por consola interactiva para el usuario.

Toda interacción que el cliente tiene con los distintos servidores se hace de manera transparente gracias a la implementación de un ZooKeeper y la correcta aplicación de los principios de los middleware.

Finalmente, el cliente presenta las siguientes funcionalidades:

Registro de usuario

- Permite a un nuevo usuario registrarse en el sistema.

Inicio de sesión

- Permite a un usuario autenticarse y obtener un token de acceso.

Listar todas las colas

- Muestra una lista de todas las colas disponibles en el servidor.

Crear una cola

- Permite crear una nueva cola de mensajes.

Eliminar una cola

- Elimina una cola específica del sistema.

Enviar mensaje a una cola

- Envia un mensaje a una cola seleccionada.

Recibir mensaje de una cola

- Recupera un mensaje de una cola, si hay mensajes disponibles.

Suscribirse a una cola

- Permite al usuario suscribirse a una cola para recibir mensajes automáticamente.

Cancelar suscripción a una cola

- Detiene la recepción automática de mensajes desde una cola suscrita.

Listar todos los tópicos

- Muestra una lista de todos los tópicos disponibles en el sistema.

Crear un tópico

- Permite crear un nuevo tópico de publicación.

Eliminar un tópico

- Elimina un tópico específico del sistema.

Ver mensajes recolectados de un tópico

- Muestra los mensajes almacenados que fueron publicados en un tópico.

Enviar mensaje a un tópico

- Publica un mensaje en un tópico específico.

Suscribirse a un tópico

- Permite al usuario suscribirse a un tópico para recibir mensajes publicados.

Salir del cliente

- Finaliza la ejecución del cliente y cierra la conexión con el middleware.

## Documentación Servidor

El servidor MOM (Message Oriented Middleware) es el encargado de la recepción de las peticiones para el registro y autenticación de usuarios, creación de colas y tópicos, envío y recepción de mensajes, entre otras muchas funcionalidades. Como base es un servidor web construido en FasApi de tal manera que los clientes se comuniquen a través de peticiones HTTP, mantiene una persistencia de datos en una base de datos MySQL y el uso de comunicación gRPC para comunicarse con los otros servidores existentes.

El servidor es quien aplica las distintas tareas que el cliente solicita a través de la consola, realiza el correcto manejo de los mensajes, colas y tópicos entre él y los distintos otros servidores existentes, esto con la gran ayuda del ZooKeeper del cual se hablará más adelante.

El sistema de servidores implementa varias características clave que garantizan un rendimiento eficiente, disponibilidad y robustez. En primer lugar, la escalabilidad permite agregar nuevos servidores de forma transparente, sin afectar la operación del sistema. Además, se implementa particionamiento de datos, lo que distribuye la información entre múltiples servidores para evitar cuellos de botella y mejorar la eficiencia. También se cuenta con replicación, asegurando que los datos estén disponibles en al menos dos servidores activos, lo que reduce el riesgo de pérdida de información. Por último, el sistema está diseñado con tolerancia a fallos, de modo que si un servidor se cae, el cliente no percibe interrupciones. En ese caso, el sistema replica y redistribuye automáticamente los datos, y cuenta con mecanismos para restaurar el estado del servidor al momento de la falla.

## Documentación del ZooKeeper

Como se dijo anteriormente se implementó el uso de un ZooKeeper (Apache) para el manejo del clúster de servidores, este software nos entrega muchas funcionalidades que ayudan para el correcto funcionamiento de los sistemas y de todas las características de los servidores mencionadas anteriormente. Entre sus principales ventajas se encuentran: la coordinación distribuida, que permite mantener una visión consistente del estado del sistema entre todos los nodos; la detección de fallos, que permite identificar rápidamente servidores inactivos y redirigir la carga de forma automática; y el descubrimiento de servicios, gracias al cual los clientes pueden conectarse siempre al servidor más adecuado sin intervención manual. Además, ZooKeeper facilita la gestión de la configuración centralizada, la sincronización de procesos distribuidos y la elección de líderes, aspectos fundamentales para garantizar alta disponibilidad, tolerancia a fallos y balanceo de carga en entornos distribuidos con múltiples servidores.

## Documentación API

Con el servidor iniciado la documentación se puede encontrar en la ruta http://{IP}:8000/docs

# 3. Descripción del ambiente de desarrollo y técnico:

- Lenguaje de programación: Python
- Base de datos: MySQL
- ZooKeeper: Apache ZooKeeper
- gRPC: Protobuf

## Paquetes Cliente

### 🔧 Utilidades y Core

- **annotated-types==0.7.0**  
  Tipos anotados con validaciones adicionales, usados junto a Pydantic.

- **typing_extensions==4.12.2**  
  Extensiones de tipado para versiones anteriores de Python que aún no tienen características más nuevas del sistema de tipos.

- **six==1.17.0**  
  Compatibilidad entre Python 2 y 3.

---

### 🌐 Web y APIs

- **fastapi==0.115.11**  
  Framework moderno para construir APIs web en Python con tipado estático basado en Pydantic.

- **starlette==0.46.1**  
  Framework ASGI ligero usado por FastAPI para el manejo de rutas, middleware, y más.

- **anyio==4.9.0**  
  Librería de concurrencia compatible con asyncio y trio, usada internamente por Starlette y FastAPI.

- **sniffio==1.3.1**  
  Detección de contexto de ejecución asincrónico, usado por AnyIO.

---

### 🛡️ Seguridad y Autenticación

- **bcrypt==4.3.0**  
  Algoritmo de hashing para contraseñas seguro.

- **passlib==1.7.4**  
  Framework de hashing de contraseñas que soporta múltiples algoritmos, incluyendo bcrypt.

- **PyJWT==2.10.1**  
  Implementación de JSON Web Tokens para Python.

- **python-jose==3.4.0**  
  Implementación de JOSE (JWT, JWE, JWS) para autenticación y autorización.

---

### 🔒 Criptografía

- **ecdsa==0.19.1**  
  Implementación de algoritmos de firma digital con curvas elípticas.

- **rsa==4.9**  
  Implementación de RSA para encriptación y firmas.

- **pyasn1==0.4.8**  
  Codificador/decodificador ASN.1, común en protocolos criptográficos.

---

### 🐘 ZooKeeper

- **kazoo==2.10.0**  
  Cliente de Python para Apache ZooKeeper. Útil para coordinación distribuida, replicación y particionamiento.

---

### 🔍 Validación y Parsing

- **pydantic==2.10.6**  
  Validación de datos mediante anotaciones de tipos, base de FastAPI.

- **pydantic_core==2.27.2**  
  Núcleo ultra rápido de Pydantic en Rust para validación de datos.

---

### 📡 HTTP y Requests

- **requests==2.32.3**  
  Librería HTTP simple y popular para realizar peticiones web.

- **urllib3==2.3.0**  
  Cliente HTTP con características avanzadas, usado por `requests`.

- **idna==3.10**  
  Soporte para dominios internacionales (IDNA).

- **certifi==2025.1.31**  
  Certificados raíz CA para validar conexiones TLS/SSL.

- **charset-normalizer==3.4.1**  
  Detección automática de codificación de texto (similar a chardet).

---

### 📝 Markdown y Consola

- **markdown-it-py==3.0.0**  
  Analizador de Markdown en Python compatible con Markdown-It.

- **mdurl==0.1.2**  
  Analizador de URLs usado por markdown-it-py.

- **Pygments==2.19.1**  
  Librería para resaltar sintaxis de código fuente.

- **rich==13.9.4**  
  Salida de consola con colores, tablas, trazas, logs y más.

---

### 🧪 Herramientas de Desarrollo

- **ruff==0.11.0**  
  Linter y formateador ultrarrápido para Python escrito en Rust.

- **python-dotenv==1.0.1**  
  Carga variables de entorno desde un archivo `.env`.

## Paquetes Servidor

### 🌐 APIs y Servidores Web

- **fastapi==0.115.11**  
  Framework web moderno y de alto rendimiento para construir APIs RESTful.

- **starlette==0.46.1**  
  Base ASGI para FastAPI que maneja rutas, middleware, WebSockets, y más.

- **uvicorn==0.34.0**  
  Servidor ASGI ligero y rápido ideal para correr aplicaciones FastAPI.

- **httpx==0.28.1**  
  Cliente HTTP asíncrono compatible con `async/await`, usado frecuentemente con FastAPI.

- **python-multipart==0.0.20**  
  Soporte para formularios con multipart/form-data (subida de archivos).

---

### 🔌 gRPC y Comunicación entre Servidores

- **grpcio-tools==1.71.0**  
  Herramientas necesarias para compilar archivos `.proto` y trabajar con gRPC en Python.

- **protobuf==5.29.4**  
  Librería oficial para trabajar con Google Protocol Buffers, base de gRPC.

---

### 🔐 Seguridad y Autenticación

- **passlib==1.7.4**  
  Manejo de contraseñas con múltiples algoritmos de hashing.

- **PyJWT==2.10.1**  
  Autenticación basada en JSON Web Tokens (JWT).

- **python-jose==3.4.0**  
  Soporte completo para JOSE (JWT, JWE, JWS) en Python.

---

### 🐘 Coordinación Distribuida

- **kazoo==2.10.0**  
  Cliente para Apache ZooKeeper, utilizado para coordinación de clústeres, replicación y failover.

---

### 🧠 Validación y Tipado

- **pydantic==2.10.6**  
  Validación de datos basada en anotaciones de tipos, clave en FastAPI.

- **pydantic_core==2.27.2**  
  Núcleo en Rust de Pydantic para validaciones rápidas y eficientes.

---

### 🧪 Testing y Desarrollo

- **pytest==8.3.5**  
  Framework de pruebas robusto y flexible para Python.

- **python-dotenv==1.0.1**  
  Carga variables de entorno desde archivos `.env`, útil para configuración.

- **rich==13.9.4**  
  Salida en consola con formato bonito: logs, tablas, traza de errores, etc.

---

### 🗄️ Base de Datos

- **SQLAlchemy==2.0.39**  
  ORM poderoso para manejo de bases de datos en Python.

- **PyMySQL==1.1.1**  
  Conector para trabajar con bases de datos MySQL desde Python.

---

### 🧬 Otros útiles

- **Jinja2==3.1.6**  
  Motor de plantillas usado por muchas apps web (ej. renderizado de HTML).

- **PyYAML==6.0.2**  
  Lectura y escritura de archivos YAML, útil para configuración.

- **watchfiles==1.0.4**  
  Observador de cambios en archivos, útil en desarrollo con recarga automática.

- **uvloop==0.21.0**  
  Reemplazo para el loop de eventos de asyncio, mejora el rendimiento de aplicaciones async.

## Justificación de las tecnologías usadas

Para la implementación del middleware MOM se seleccionaron tecnologías que permiten construir un sistema distribuido robusto, eficiente y escalable. FastAPI fue elegida como framework principal del servidor por su velocidad, soporte asincrónico nativo y facilidad para definir APIs REST, facilitando la interacción con los clientes. Para la comunicación entre servidores, se optó por gRPC debido a su eficiencia, bajo consumo de ancho de banda y soporte para transmisión binaria mediante protocolos Protobuf, lo cual es ideal para ambientes distribuidos de alto rendimiento. La persistencia de usuarios, colas, tópicos y mensajes se gestiona mediante MySQL, una base de datos relacional madura, confiable y ampliamente adoptada, lo cual garantiza integridad de datos y soporte para consultas complejas. Finalmente, se utilizó Apache ZooKeeper como mecanismo de coordinación y gestión del clúster de servidores, permitiendo detección de fallos, balanceo de carga, descubrimiento de servicios y almacenamiento distribuido de metadatos, funcionalidades esenciales para garantizar la disponibilidad y consistencia del sistema MOM.

## como se compila y ejecuta.

## detalles del desarrollo.

## detalles técnicos

## descripción y como se configura los parámetros del proyecto (ej: ip, puertos, conexión a bases de datos, variables de ambiente, parámetros, etc)

## opcional - detalles de la organización del código por carpetas o descripción de algún archivo. (ESTRUCTURA DE DIRECTORIOS Y ARCHIVOS IMPORTANTE DEL PROYECTO, comando 'tree' de linux)

### Estructura del ZooKeeper

Nuestro ZooKeeper tiene la siguiente estructura:

```
/
├── servers
│     ├──IP
├── servers-metadata
      ├──IP
    ├──Queues
      		├──ID
			├──…
    ├──Topics
      		├──ID
			├──…
    ├──Users
      		├──ID
			├──…
```

Encontramos la ruta servers donde se encuentran las direcciones IP de los servidores disponibles actualmente, son nodos efímeros los cuales desaparecen al momento que el server se desconecta, y es de esta lista de servers que se eligen para interactuar con el cliente. También encontramos la ruta de servers-metadata donde también se encuentran las IP de los servidores, pero estos no desaparecen si el servidor llega a caer de forma inesperada, cada una de estas direcciones IP tiene a su vez por dentro las colas, los tópicos y los usuarios locales de cada servidor (los ID de cada elemento almacenado).

Conociendo la estructura entonces podemos explicar el funcionamiento del sistema con el ZooKeeper:

**IMAGEN DIAGRAMA DE SECUENCIA**

## opcionalmente - si quiere mostrar resultados o pantallazos

# 4. Descripción del ambiente de EJECUCIÓN (en producción) lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.

# IP o nombres de dominio en nube o en la máquina servidor.

## descripción y como se configura los parámetros del proyecto (ej: ip, puertos, conexión a bases de datos, variables de ambiente, parámetros, etc)

## como se lanza el servidor.

## una mini guia de como un usuario utilizaría el software o la aplicación

## opcionalmente - si quiere mostrar resultados o pantallazos

# 5. otra información que considere relevante para esta actividad.

# referencias:

<debemos siempre reconocer los créditos de partes del código que reutilizaremos, así como referencias a youtube, o referencias bibliográficas utilizadas para desarrollar el proyecto o la actividad>

## sitio1-url

## sitio2-url

## url de donde tomo info para desarrollar este proyecto
