# crud.py
# ============================================================================
# Módulo con el **CRUD (endpoints FastAPI)** para aplicación de estudio.
# Usa SQLAlchemy y PostgreSQL para persistencia de datos. Ejecuta la API con:
#    python -m uvicorn crud:app --reload
# ============================================================================

from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db, init_db
import db_functions as svc
from functions import (
    # Modelos de datos
    Rol, Usuario, UsuarioCreate, UsuarioUpdate,
    Tarea, TareaCreate, TareaUpdate, EstadoTarea,
    Cronograma, CronogramaCreate, CronogramaUpdate,
    EstadoAnimo, EstadoAnimoCreate, EstadoAnimoUpdate,
    Tutoria, TutoriaCreate, TutoriaUpdate,
    UsuarioTutoriaCreate, RolTutoria
)

# Importar funciones de autenticación
from auth import (
    authenticate_user, create_access_token, get_current_active_user,
    get_password_hash, Token, UserLogin, ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(
    title="API Aplicación de Estudio",
    description="Sistema de gestión para estudiantes con tareas, cronograma, estado de ánimo y tutorías",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "*"  # Para desarrollo, permite todos los orígenes
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Inicializar la base de datos al iniciar la aplicación
@app.on_event("startup")
def startup_event():
    init_db()

# -------------------------
# Salud
# -------------------------
@app.get("/", summary="Healthcheck")
def root():
    return {"status": "ok", "msg": "API Aplicación de Estudio funcionando correctamente"}


# -------------------------
# ROLES
# -------------------------
@app.get("/roles", response_model=List[Rol], tags=["Roles"], summary="Listar roles")
def listar_roles(db: Session = Depends(get_db)):
    """Obtiene la lista de todos los roles disponibles en el sistema."""
    return svc.get_roles(db)


@app.get("/roles/{rol_id}", response_model=Rol, tags=["Roles"], summary="Obtener rol por ID")  
def obtener_rol(rol_id: int, db: Session = Depends(get_db)):
    """Obtiene un rol específico por su ID."""
    rol = svc.get_rol_by_id(db, rol_id)
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol


# -------------------------
# AUTENTICACIÓN
# -------------------------
@app.post("/auth/register", response_model=Usuario, status_code=201, tags=["Autenticación"], summary="Registrar usuario")
def registrar_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario (igual que crear usuario pero con hash de contraseña)
    
    **Campos requeridos:**
    - nombre: Nombre completo del usuario
    - email: Email único del usuario  
    - password: Contraseña (será hasheada automáticamente)
    - rol_id: ID del rol (1=Administrador, 2=Estudiante, 3=Tutor)
    """
    try:
        # Verificar si el email ya existe
        existing_user = svc.obtener_usuario_por_email(db, payload.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email ya registrado")
        
        # Hash de la contraseña
        hashed_password = get_password_hash(payload.password)
        
        # Crear usuario con contraseña hasheada
        return svc.crear_usuario_con_hash(db, payload, hashed_password)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=Token, tags=["Autenticación"], summary="Iniciar sesión")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint para login con email y contraseña
    
    **Campos requeridos:**
    - email: Email del usuario registrado
    - password: Contraseña del usuario
    
    **Respuesta:**
    - access_token: Token JWT para autenticación
    - token_type: Tipo de token (bearer)
    - user_info: Información básica del usuario
    """
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "id": user.id,
            "nombre": user.nombre,
            "email": user.email,
            "rol_id": user.rol_id
        }
    }


@app.post("/auth/login-form", response_model=Token, tags=["Autenticación"], summary="Login con formulario")
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint para login compatible con OAuth2 (username/password form)
    
    **Para usar con Swagger UI:**
    - username: Email del usuario (no nombre de usuario)
    - password: Contraseña del usuario
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "id": user.id,
            "nombre": user.nombre,
            "email": user.email,
            "rol_id": user.rol_id
        }
    }


@app.get("/auth/me", response_model=Usuario, tags=["Autenticación"], summary="Obtener usuario actual")
def obtener_usuario_actual(current_user = Depends(get_current_active_user)):
    """
    Obtener información del usuario autenticado
    
    **Requiere:** Token JWT válido en el header Authorization
    **Formato:** Authorization: Bearer <token>
    """
    return current_user


# -------------------------
# USUARIOS
# -------------------------
@app.get("/usuarios", response_model=List[Usuario], tags=["Usuarios"], summary="Listar usuarios")
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtiene la lista de todos los usuarios registrados.
    
    **Requiere:** Token JWT válido
    **Solo administradores** pueden ver todos los usuarios
    """
    # Solo los administradores (rol_id = 1) pueden ver todos los usuarios
    if current_user.rol_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver todos los usuarios"
        )
    return svc.get_usuarios(db)


@app.get("/usuarios/{usuario_id}", response_model=Usuario, tags=["Usuarios"], summary="Obtener usuario por ID")
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtiene un usuario específico por su ID.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes ver tu propio perfil o ser administrador
    """
    # Solo puedes ver tu propio perfil o ser administrador
    if current_user.rol_id != 1 and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este usuario"
        )
    
    usuario = svc.get_usuario_by_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.post("/usuarios", response_model=Usuario, status_code=201, tags=["Usuarios"], summary="Crear usuario")
def crear_usuario(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Crea un nuevo usuario en el sistema.
    
    **Requiere:** Token JWT válido
    **Solo administradores** pueden crear usuarios
    
    - **nombre**: Nombre completo del usuario (requerido)
    - **email**: Email único del usuario (requerido)
    - **password**: Contraseña del usuario (requerido, mínimo 6 caracteres)
    - **rol_id**: ID del rol asignado (opcional)
    
    **Nota:** Este endpoint hashea automáticamente la contraseña.
    """
    # Solo los administradores pueden crear usuarios
    if current_user.rol_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear usuarios"
        )
    
    try:
        # Verificar si el email ya existe
        existing_user = svc.obtener_usuario_por_email(db, payload.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email ya registrado")
        
        # Hash de la contraseña
        hashed_password = get_password_hash(payload.password)
        
        # Crear usuario con contraseña hasheada
        return svc.crear_usuario_con_hash(db, payload, hashed_password)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/usuarios/{usuario_id}", response_model=Usuario, tags=["Usuarios"], summary="Actualizar usuario")
def actualizar_usuario(
    usuario_id: int,
    payload: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Actualiza la información de un usuario existente.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes actualizar tu propio perfil o ser administrador
    
    Solo se actualizarán los campos proporcionados (no nulos).
    """
    # Solo puedes actualizar tu propio perfil o ser administrador
    if current_user.rol_id != 1 and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este usuario"
        )
    
    try:
        return svc.update_usuario(db, usuario_id, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/usuarios/{usuario_id}", tags=["Usuarios"], summary="Eliminar usuario")
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Elimina un usuario del sistema.
    
    **Requiere:** Token JWT válido
    **Solo administradores** pueden eliminar usuarios
    
    **ATENCIÓN**: Esta operación también eliminará:
    - Todas las tareas del usuario
    - Todo el cronograma del usuario
    - Todos los registros de estado de ánimo del usuario
    - Todas las participaciones en tutorías del usuario
    """
    # Solo los administradores pueden eliminar usuarios
    if current_user.rol_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar usuarios"
        )
    
    try:
        svc.delete_usuario(db, usuario_id)
        return {"message": "Usuario eliminado exitosamente"}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -------------------------
# TAREAS
# -------------------------
@app.get(
    "/tareas",
    response_model=List[Tarea],
    tags=["Tareas"],
    summary="Listar tareas (filtrable)",
    description="Obtiene la lista de tareas. Permite filtrar por usuario y estado.",
)
def listar_tareas(
    usuario_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    estado: Optional[EstadoTarea] = Query(None, description="Filtrar por estado de la tarea"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtiene la lista de tareas con filtros opcionales.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes ver tus propias tareas, excepto si eres administrador
    """
    # Si no es administrador, solo puede ver sus propias tareas
    if current_user.rol_id != 1:
        usuario_id = current_user.id  # Forzar filtro por el usuario actual
    
    return svc.get_tareas(db, usuario_id=usuario_id, estado=estado)


@app.get("/tareas/{tarea_id}", response_model=Tarea, tags=["Tareas"], summary="Obtener tarea por ID")
def obtener_tarea(
    tarea_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtiene una tarea específica por su ID.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes ver tus propias tareas, excepto si eres administrador
    """
    tarea = svc.get_tarea_by_id(db, tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # Verificar permisos: solo el propietario o administrador puede ver la tarea
    if current_user.rol_id != 1 and tarea.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver esta tarea"
        )
    
    return tarea


@app.post("/tareas", response_model=Tarea, status_code=201, tags=["Tareas"], summary="Crear tarea")
def crear_tarea(
    payload: TareaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Crea una nueva tarea para un usuario.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes crear tareas para ti mismo, excepto si eres administrador
    
    - **titulo**: Título de la tarea (requerido)
    - **descripcion**: Descripción detallada (opcional)
    - **fecha_entrega**: Fecha límite de entrega (opcional)
    - **estado**: Estado inicial (por defecto: pendiente)
    - **usuario_id**: ID del usuario propietario (requerido)
    """
    # Si no es administrador, solo puede crear tareas para sí mismo
    if current_user.rol_id != 1 and payload.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes crear tareas para otros usuarios"
        )
    
    try:
        return svc.create_tarea(db, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/tareas/{tarea_id}", response_model=Tarea, tags=["Tareas"], summary="Actualizar tarea")
def actualizar_tarea(
    tarea_id: int,
    payload: TareaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Actualiza una tarea existente.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes actualizar tus propias tareas, excepto si eres administrador
    
    Solo se actualizarán los campos proporcionados (no nulos).
    """
    # Verificar que la tarea existe y obtener el propietario
    tarea_existente = svc.get_tarea_by_id(db, tarea_id)
    if not tarea_existente:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # Verificar permisos: solo el propietario o administrador puede actualizar
    if current_user.rol_id != 1 and tarea_existente.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar esta tarea"
        )
    
    try:
        return svc.update_tarea(db, tarea_id, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/tareas/{tarea_id}", tags=["Tareas"], summary="Eliminar tarea")
def eliminar_tarea(
    tarea_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Elimina una tarea del sistema.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes eliminar tus propias tareas, excepto si eres administrador
    """
    # Verificar que la tarea existe y obtener el propietario
    tarea_existente = svc.get_tarea_by_id(db, tarea_id)
    if not tarea_existente:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # Verificar permisos: solo el propietario o administrador puede eliminar
    if current_user.rol_id != 1 and tarea_existente.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar esta tarea"
        )
    
    try:
        svc.delete_tarea(db, tarea_id)
        return {"message": "Tarea eliminada exitosamente"}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -------------------------
# CRONOGRAMA
# -------------------------
@app.get(
    "/cronograma",
    response_model=List[Cronograma],
    tags=["Cronograma"],
    summary="Listar eventos del cronograma (filtrable)",
    description="Obtiene la lista de eventos del cronograma. Permite filtrar por usuario y rango de fechas.",
)
def listar_cronograma(
    usuario_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha mínima (YYYY-MM-DD)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha máxima (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtiene la lista de eventos del cronograma con filtros opcionales.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes ver tu propio cronograma, excepto si eres administrador
    """
    # Si no es administrador, solo puede ver su propio cronograma
    if current_user.rol_id != 1:
        usuario_id = current_user.id
    
    return svc.get_cronograma(db, usuario_id=usuario_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@app.get("/cronograma/{cronograma_id}", response_model=Cronograma, tags=["Cronograma"], summary="Obtener evento por ID")
def obtener_cronograma(cronograma_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Obtiene un evento específico del cronograma por su ID.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes ver tu propio cronograma, excepto si eres administrador
    """
    cronograma = svc.get_cronograma_by_id(db, cronograma_id)
    if not cronograma:
        raise HTTPException(status_code=404, detail="Evento de cronograma no encontrado")
    
    # Verificar permisos
    if current_user.rol_id != 1 and cronograma.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para ver este evento")
    
    return cronograma


@app.post("/cronograma", response_model=Cronograma, status_code=201, tags=["Cronograma"], summary="Crear evento")
def crear_cronograma(payload: CronogramaCreate, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Crea un nuevo evento en el cronograma.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes crear eventos para ti mismo, excepto si eres administrador
    
    - **titulo**: Título del evento (requerido)
    - **descripcion**: Descripción del evento (opcional)
    - **fecha_inicio**: Fecha y hora de inicio (requerido)
    - **fecha_fin**: Fecha y hora de fin (requerido)
    - **usuario_id**: ID del usuario propietario (requerido)
    """
    # Si no es administrador, solo puede crear eventos para sí mismo
    if current_user.rol_id != 1 and payload.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes crear eventos para otros usuarios")
    
    try:
        return svc.create_cronograma(db, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/cronograma/{cronograma_id}", response_model=Cronograma, tags=["Cronograma"], summary="Actualizar evento")
def actualizar_cronograma(cronograma_id: int, payload: CronogramaUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Actualiza un evento del cronograma.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes actualizar tus propios eventos, excepto si eres administrador
    
    Solo se actualizarán los campos proporcionados (no nulos).
    """
    # Verificar que el evento existe y obtener el propietario
    cronograma_existente = svc.get_cronograma_by_id(db, cronograma_id)
    if not cronograma_existente:
        raise HTTPException(status_code=404, detail="Evento de cronograma no encontrado")
    
    # Verificar permisos
    if current_user.rol_id != 1 and cronograma_existente.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para actualizar este evento")
    
    try:
        return svc.update_cronograma(db, cronograma_id, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/cronograma/{cronograma_id}", tags=["Cronograma"], summary="Eliminar evento")
def eliminar_cronograma(cronograma_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Elimina un evento del cronograma.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes eliminar tus propios eventos, excepto si eres administrador
    """
    # Verificar que el evento existe y obtener el propietario
    cronograma_existente = svc.get_cronograma_by_id(db, cronograma_id)
    if not cronograma_existente:
        raise HTTPException(status_code=404, detail="Evento de cronograma no encontrado")
    
    # Verificar permisos
    if current_user.rol_id != 1 and cronograma_existente.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para eliminar este evento")
    
    try:
        svc.delete_cronograma(db, cronograma_id)
        return {"message": "Evento eliminado exitosamente"}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -------------------------
# ESTADO DE ÁNIMO
# -------------------------
@app.get(
    "/estados-animo",
    response_model=List[EstadoAnimo],
    tags=["Estado de Ánimo"],
    summary="Listar estados de ánimo (filtrable)",
    description="Obtiene la lista de registros de estado de ánimo. Permite filtrar por usuario y rango de fechas.",
)
def listar_estados_animo(
    usuario_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    fecha_desde: Optional[date] = Query(None, description="Fecha mínima (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha máxima (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Obtiene la lista de estados de ánimo con filtros opcionales.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes ver tus propios estados de ánimo, excepto si eres administrador
    """
    # Si no es administrador, solo puede ver sus propios estados
    if current_user.rol_id != 1:
        usuario_id = current_user.id
    
    return svc.get_estados_animo(db, usuario_id=usuario_id, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)


@app.get("/estados-animo/{estado_id}", response_model=EstadoAnimo, tags=["Estado de Ánimo"], summary="Obtener estado por ID")
def obtener_estado_animo(estado_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Obtiene un registro específico de estado de ánimo por su ID.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes ver tus propios estados de ánimo, excepto si eres administrador
    """
    estado = svc.get_estado_animo_by_id(db, estado_id)
    if not estado:
        raise HTTPException(status_code=404, detail="Estado de ánimo no encontrado")
    
    # Verificar permisos
    if current_user.rol_id != 1 and estado.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para ver este estado")
    
    return estado


@app.post("/estados-animo", response_model=EstadoAnimo, status_code=201, tags=["Estado de Ánimo"], summary="Registrar estado")
def crear_estado_animo(payload: EstadoAnimoCreate, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Registra un nuevo estado de ánimo.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes crear estados para ti mismo, excepto si eres administrador
    
    - **estado**: Descripción del estado (ej: feliz, triste, motivado, cansado)
    - **comentario**: Comentario adicional (opcional)
    - **fecha**: Fecha del registro (opcional, por defecto hoy)
    - **usuario_id**: ID del usuario (requerido)
    """
    # Si no es administrador, solo puede crear estados para sí mismo
    if current_user.rol_id != 1 and payload.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes crear estados para otros usuarios")
    
    try:
        return svc.create_estado_animo(db, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/estados-animo/{estado_id}", response_model=EstadoAnimo, tags=["Estado de Ánimo"], summary="Actualizar estado")
def actualizar_estado_animo(estado_id: int, payload: EstadoAnimoUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Actualiza un registro de estado de ánimo.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes actualizar tus propios estados, excepto si eres administrador
    
    Solo se actualizarán los campos proporcionados (no nulos).
    """
    # Verificar que el estado existe y obtener el propietario
    estado_existente = svc.get_estado_animo_by_id(db, estado_id)
    if not estado_existente:
        raise HTTPException(status_code=404, detail="Estado de ánimo no encontrado")
    
    # Verificar permisos
    if current_user.rol_id != 1 and estado_existente.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para actualizar este estado")
    
    try:
        return svc.update_estado_animo(db, estado_id, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/estados-animo/{estado_id}", tags=["Estado de Ánimo"], summary="Eliminar estado")
def eliminar_estado_animo(estado_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Elimina un registro de estado de ánimo.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes eliminar tus propios estados, excepto si eres administrador
    """
    # Verificar que el estado existe y obtener el propietario
    estado_existente = svc.get_estado_animo_by_id(db, estado_id)
    if not estado_existente:
        raise HTTPException(status_code=404, detail="Estado de ánimo no encontrado")
    
    # Verificar permisos
    if current_user.rol_id != 1 and estado_existente.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para eliminar este estado")
    
    try:
        svc.delete_estado_animo(db, estado_id)
        return {"message": "Estado de ánimo eliminado exitosamente"}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))





# -------------------------
# TUTORÍAS
# -------------------------
@app.get("/tutorias", response_model=List[Tutoria], tags=["Tutorías"], summary="Listar tutorías")
def listar_tutorias(db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Obtiene la lista de todas las tutorías programadas.
    
    **Requiere:** Token JWT válido
    **Permisos:** Todos los usuarios autenticados pueden ver las tutorías
    """
    return svc.get_tutorias(db)


@app.get("/tutorias/{tutoria_id}", response_model=Tutoria, tags=["Tutorías"], summary="Obtener tutoría por ID")
def obtener_tutoria(tutoria_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Obtiene una tutoría específica por su ID, incluyendo sus participantes.
    
    **Requiere:** Token JWT válido
    **Permisos:** Todos los usuarios autenticados pueden ver las tutorías
    """
    tutoria = svc.get_tutoria_by_id(db, tutoria_id)
    if not tutoria:
        raise HTTPException(status_code=404, detail="Tutoría no encontrada")
    return tutoria


@app.post("/tutorias", response_model=Tutoria, status_code=201, tags=["Tutorías"], summary="Crear tutoría")
def crear_tutoria(payload: TutoriaCreate, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Crea una nueva tutoría.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo administradores y tutores pueden crear tutorías
    
    - **tema**: Tema de la tutoría (requerido)
    - **descripcion**: Descripción detallada (opcional)
    - **fecha**: Fecha y hora programada (requerido)
    """
    # Solo administradores (rol_id=1) y tutores (rol_id=3) pueden crear tutorías
    if current_user.rol_id not in [1, 3]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores y tutores pueden crear tutorías")
    
    return svc.create_tutoria(db, payload)


@app.put("/tutorias/{tutoria_id}", response_model=Tutoria, tags=["Tutorías"], summary="Actualizar tutoría")
def actualizar_tutoria(tutoria_id: int, payload: TutoriaUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Actualiza una tutoría existente.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo administradores y tutores pueden actualizar tutorías
    
    Solo se actualizarán los campos proporcionados (no nulos).
    """
    # Solo administradores (rol_id=1) y tutores (rol_id=3) pueden actualizar tutorías
    if current_user.rol_id not in [1, 3]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores y tutores pueden actualizar tutorías")
    
    try:
        return svc.update_tutoria(db, tutoria_id, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/tutorias/{tutoria_id}", tags=["Tutorías"], summary="Eliminar tutoría")
def eliminar_tutoria(tutoria_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Elimina una tutoría del sistema.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo administradores pueden eliminar tutorías
    
    **ATENCIÓN**: Esta operación también eliminará todas las participaciones asociadas.
    """
    # Solo administradores pueden eliminar tutorías
    if current_user.rol_id != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores pueden eliminar tutorías")
    try:
        svc.delete_tutoria(db, tutoria_id)
        return {"message": "Tutoría eliminada exitosamente"}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -------------------------
# PARTICIPACIONES EN TUTORÍAS
# -------------------------
@app.post("/tutorias/participantes", tags=["Tutorías"], summary="Agregar participante a tutoría")
def agregar_usuario_tutoria(payload: UsuarioTutoriaCreate, db: Session = Depends(get_db), current_user = Depends(get_current_active_user)):
    """
    Agrega un usuario como participante de una tutoría.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes inscribirte a ti mismo, excepto si eres administrador
    
    - **usuario_id**: ID del usuario participante
    - **tutoria_id**: ID de la tutoría
    - **rol_en_tutoria**: Rol del usuario (tutor o estudiante)
    """
    # Si no es administrador, solo puede inscribirse a sí mismo
    if current_user.rol_id != 1 and payload.usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes inscribirte a ti mismo en las tutorías")
    
    try:
        return svc.add_usuario_tutoria(db, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/tutorias/{tutoria_id}/participantes/{usuario_id}", tags=["Tutorías"], summary="Remover participante")
def remover_usuario_tutoria(
    tutoria_id: int, 
    usuario_id: int,
    rol_en_tutoria: RolTutoria = Query(..., description="Rol del usuario en la tutoría"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Remueve un usuario de una tutoría específica.
    
    **Requiere:** Token JWT válido
    **Permisos:** Solo puedes removerte a ti mismo, excepto si eres administrador
    
    - **tutoria_id**: ID de la tutoría
    - **usuario_id**: ID del usuario a remover
    - **rol_en_tutoria**: Rol específico a remover (tutor o estudiante)
    """
    # Si no es administrador, solo puede removerse a sí mismo
    if current_user.rol_id != 1 and usuario_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes removerte a ti mismo de las tutorías")
    
    try:
        return svc.remove_usuario_tutoria(db, usuario_id, tutoria_id, rol_en_tutoria)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -------------------------
# ESTADÍSTICAS Y REPORTES
# -------------------------
@app.get("/estadisticas/usuario/{usuario_id}", tags=["Estadísticas"], summary="Estadísticas de usuario")
def estadisticas_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales de un usuario específico.
    """
    usuario = svc.get_usuario_by_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    tareas = svc.get_tareas(db, usuario_id=usuario_id)
    cronograma = svc.get_cronograma(db, usuario_id=usuario_id)
    estados_animo = svc.get_estados_animo(db, usuario_id=usuario_id)
    
    tareas_por_estado = {}
    for estado in EstadoTarea:
        tareas_por_estado[estado.value] = len([t for t in tareas if t.estado == estado])
    
    return {
        "usuario": usuario,
        "total_tareas": len(tareas),
        "tareas_por_estado": tareas_por_estado,
        "eventos_cronograma": len(cronograma),
        "registros_estado_animo": len(estados_animo)
    }


@app.get("/estadisticas/generales", tags=["Estadísticas"], summary="Estadísticas generales")
def estadisticas_generales(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales del sistema.
    """
    usuarios = svc.get_usuarios(db)
    tareas = svc.get_tareas(db)
    cronograma = svc.get_cronograma(db)
    tutorias = svc.get_tutorias(db)
    estados_animo = svc.get_estados_animo(db)
    
    return {
        "total_usuarios": len(usuarios),
        "total_tareas": len(tareas),
        "total_eventos_cronograma": len(cronograma),
        "total_tutorias": len(tutorias),
        "total_registros_estado_animo": len(estados_animo)
    }
