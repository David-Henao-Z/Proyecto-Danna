# API Aplicación de Estudio

Una API REST desarrollada con FastAPI para gestionar una aplicación de estudio que permite a los usuarios administrar tareas, cronogramas, estados de ánimo y tutorías.

## Características

### 🧑‍🎓 Gestión de Usuarios
- Crear, leer, actualizar y eliminar usuarios
- Sistema de roles (Administrador, Estudiante, Tutor)
- Autenticación por email único

### 📝 Gestión de Tareas
- Crear y administrar tareas personales
- Estados: pendiente, en_progreso, completada
- Fechas de entrega opcionales
- Filtros por usuario y estado

### 📅 Cronograma Personal
- Eventos con fecha y hora de inicio/fin
- Gestión completa CRUD
- Filtros por usuario y rango de fechas

### 😊 Estado de Ánimo
- Registro diario del estado emocional
- Comentarios opcionales
- Seguimiento histórico

### 👥 Sistema de Tutorías
- Programación de sesiones de tutoría
- Participantes con roles (tutor/estudiante)
- Gestión de inscripciones

### 📊 Estadísticas
- Estadísticas por usuario
- Reportes generales del sistema

## Estructura de la Base de Datos

El sistema maneja las siguientes entidades:

- **roles**: Roles de usuario del sistema
- **usuarios**: Información personal y credenciales
- **tareas**: Tareas personales de cada usuario
- **cronograma**: Eventos programados por usuario
- **estado_animo**: Registros diarios de estado emocional
- **tutorias**: Sesiones de tutoría programadas
- **usuario_tutorias**: Relación muchos-a-muchos entre usuarios y tutorías

## 🚀 Instalación y Ejecución

### Prerrequisitos
- **Python 3.8+** instalado
- **pip** (gestor de paquetes de Python)
- **Git** (para clonar el repositorio)

### 📦 Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/David-Henao-Z/Proyecto-Danna.git
cd Proyecto-Danna
```

### 🔧 Paso 2: Configurar Variables de Entorno

1. **Copia el archivo de ejemplo de variables de entorno:**
```bash
copy .env.example .env
```

2. **Edita el archivo `.env`** y actualiza la cadena de conexión a tu base de datos:
```properties
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_db?sslmode=require
```

### 📚 Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**O instalar cada dependencia individualmente:**
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv email-validator alembic
```

### 🗄️ Paso 4: Inicializar la Base de Datos

```bash
python database.py
```
Este comando creará todas las tablas necesarias y los roles por defecto.

### 🎯 Paso 5: Ejecutar la Aplicación

**Opción 1: Desarrollo (con recarga automática)**
```bash
python -m uvicorn crud:app --reload
```

**Opción 2: Desarrollo con host y puerto específicos**
```bash
python -m uvicorn crud:app --reload --host 127.0.0.1 --port 8000
```

**Opción 3: Producción**
```bash
python -m uvicorn crud:app --host 0.0.0.0 --port 8000
```

### 🌐 Acceder a la Aplicación

Una vez ejecutada la aplicación, estará disponible en:

- **API Principal**: `http://127.0.0.1:8000/`
- **Documentación Swagger UI**: `http://127.0.0.1:8000/docs`
- **Documentación ReDoc**: `http://127.0.0.1:8000/redoc`
- **Schema OpenAPI**: `http://127.0.0.1:8000/openapi.json`

### 🔍 Verificar que Todo Funciona

1. **Healthcheck**: Visita `http://127.0.0.1:8000/` 
   - Deberías ver: `{"status": "ok", "msg": "API Aplicación de Estudio funcionando correctamente"}`

2. **Ver roles por defecto**: Visita `http://127.0.0.1:8000/roles`
   - Deberías ver la lista de roles (Administrador, Estudiante, Tutor)

3. **Documentación interactiva**: Ve a `http://127.0.0.1:8000/docs`
   - Explora todos los endpoints disponibles

### 🛠️ Comandos Útiles

**Detener la aplicación:**
- Presiona `Ctrl + C` en la terminal

**Verificar la instalación de dependencias:**
```bash
pip list
```

**Ver logs en tiempo real:**
```bash
python -m uvicorn crud:app --reload --log-level debug
```

**Ejecutar en un puerto diferente:**
```bash
python -m uvicorn crud:app --reload --port 3000
```

## Endpoints Principales

### Usuarios
- `GET /usuarios` - Listar usuarios
- `POST /usuarios` - Crear usuario
- `GET /usuarios/{id}` - Obtener usuario
- `PUT /usuarios/{id}` - Actualizar usuario
- `DELETE /usuarios/{id}` - Eliminar usuario

### Tareas
- `GET /tareas` - Listar tareas (filtrable)
- `POST /tareas` - Crear tarea
- `GET /tareas/{id}` - Obtener tarea
- `PUT /tareas/{id}` - Actualizar tarea
- `DELETE /tareas/{id}` - Eliminar tarea

### Cronograma
- `GET /cronograma` - Listar eventos (filtrable)
- `POST /cronograma` - Crear evento
- `GET /cronograma/{id}` - Obtener evento
- `PUT /cronograma/{id}` - Actualizar evento
- `DELETE /cronograma/{id}` - Eliminar evento

### Estado de Ánimo
- `GET /estados-animo` - Listar registros (filtrable)
- `POST /estados-animo` - Crear registro
- `GET /estados-animo/{id}` - Obtener registro
- `PUT /estados-animo/{id}` - Actualizar registro
- `DELETE /estados-animo/{id}` - Eliminar registro

### Tutorías
- `GET /tutorias` - Listar tutorías
- `POST /tutorias` - Crear tutoría
- `GET /tutorias/{id}` - Obtener tutoría
- `PUT /tutorias/{id}` - Actualizar tutoría
- `DELETE /tutorias/{id}` - Eliminar tutoría
- `POST /tutorias/participantes` - Agregar participante
- `DELETE /tutorias/{tutoria_id}/participantes/{usuario_id}` - Remover participante

### Estadísticas
- `GET /estadisticas/usuario/{id}` - Estadísticas de usuario
- `GET /estadisticas/generales` - Estadísticas generales

## Arquitectura

La aplicación sigue una arquitectura modular:

- **`crud.py`**: Endpoints de la API FastAPI
- **`functions.py`**: Lógica de negocio y modelos Pydantic
- **Almacenamiento**: En memoria (para desarrollo/demo)

## Estados de Tarea

- `pendiente`: Tarea recién creada
- `en_progreso`: Tarea en desarrollo
- `completada`: Tarea finalizada

## Roles de Usuario

- **Administrador**: Acceso completo al sistema
- **Estudiante**: Usuario básico
- **Tutor**: Usuario que puede dar tutorías

## 📖 Ejemplos de Uso

Una vez que la aplicación esté ejecutándose, puedes probar los endpoints desde la documentación interactiva en `http://127.0.0.1:8000/docs` o usando herramientas como curl o Postman.

### 🧑‍💼 Crear un usuario:
```bash
curl -X POST "http://127.0.0.1:8000/usuarios" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez",
    "email": "juan@ejemplo.com", 
    "password": "mi_password_seguro",
    "rol_id": 2
  }'
```

### 📝 Crear una tarea:
```bash
curl -X POST "http://127.0.0.1:8000/tareas" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Estudiar para examen de matemáticas",
    "descripcion": "Repasar capítulos 1-5", 
    "fecha_entrega": "2024-12-15",
    "usuario_id": 1
  }'
```

### 😊 Registrar estado de ánimo:
```bash
curl -X POST "http://127.0.0.1:8000/estados-animo" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "motivado",
    "comentario": "Me siento bien preparado para el examen",
    "usuario_id": 1
  }'
```

### 📅 Crear evento en cronograma:
```bash
curl -X POST "http://127.0.0.1:8000/cronograma" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Clase de Matemáticas",
    "descripcion": "Tema: Álgebra Lineal",
    "fecha_inicio": "2024-12-10T09:00:00",
    "fecha_fin": "2024-12-10T11:00:00",
    "usuario_id": 1
  }'
```

## 🚨 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'xxx'"
```bash
pip install -r requirements.txt
```

### Error: "Connection refused" o problemas de base de datos
1. Verifica que tu cadena de conexión en `.env` sea correcta
2. Asegúrate que tu base de datos PostgreSQL esté accesible
3. Ejecuta: `python database.py` para inicializar las tablas

### Error: "Port already in use"
```bash
# Usar un puerto diferente
python -m uvicorn crud:app --reload --port 8001
```

### La aplicación se cierra inesperadamente
```bash
# Ejecutar con logs detallados
python -m uvicorn crud:app --reload --log-level debug
```

### Error: "email-validator is not installed"
```bash
pip install email-validator
```

## 🔄 Reiniciar desde Cero

Si necesitas reiniciar completamente:

1. **Eliminar todas las tablas de la base de datos**
2. **Ejecutar de nuevo:**
```bash
python database.py
python -m uvicorn crud:app --reload
```

## 👨‍💻 Desarrollo y Contribución

### Estructura del Proyecto
```
Proyecto-Danna/
├── crud.py              # Endpoints FastAPI
├── database.py          # Configuración SQLAlchemy
├── db_functions.py      # Funciones CRUD con base de datos
├── functions.py         # Modelos Pydantic
├── requirements.txt     # Dependencias
├── .env                 # Variables de entorno (no incluir en git)
├── .env.example         # Ejemplo de variables de entorno
└── README.md           # Este archivo
```

### 🔧 Agregar Nuevas Funcionalidades

1. **Definir modelo de datos**:
   - Agregar modelo Pydantic en `functions.py`
   - Agregar modelo SQLAlchemy en `database.py`

2. **Crear funciones CRUD**:
   - Implementar funciones en `db_functions.py`

3. **Crear endpoints**:
   - Agregar endpoints en `crud.py`

### 🧪 Entorno de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install pytest httpx

# Ejecutar con recarga automática
python -m uvicorn crud:app --reload --log-level debug

# Ver documentación interactiva
# http://127.0.0.1:8000/docs
```

### 📁 Variables de Entorno

Crear archivo `.env` basado en `.env.example`:
```properties
DATABASE_URL=postgresql://usuario:password@host:puerto/database
DEBUG=True
SECRET_KEY=tu-clave-secreta
```

## 🔒 Seguridad

- ✅ Conexión SSL a base de datos
- ✅ Validación de datos con Pydantic
- ✅ Variables de entorno para credenciales
- ⚠️ **TODO**: Hashear contraseñas (para producción)
- ⚠️ **TODO**: Implementar autenticación JWT
- ⚠️ **TODO**: Rate limiting

## 📊 Características Técnicas

- **Framework**: FastAPI 0.104.1
- **Base de datos**: PostgreSQL con SQLAlchemy 2.0
- **Validación**: Pydantic con validación de emails
- **Documentación**: OpenAPI/Swagger automática
- **Despliegue**: Uvicorn ASGI server

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📝 Notas

- **Entorno actual**: Desarrollo con PostgreSQL
- **Producción**: Configurar variables de entorno apropiadas
- **Seguridad**: Las contraseñas están en texto plano (solo para desarrollo)
- **Logging**: Logs disponibles en la terminal de uvicorn