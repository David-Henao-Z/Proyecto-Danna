# crud.py
# ============================================================================
# Módulo con el **CRUD (endpoints FastAPI)** para aplicación de estudio.
# Usa SQLAlchemy y PostgreSQL para persistencia de datos. Ejecuta la API con:
#    python -m uvicorn crud:app --reload
# ============================================================================

from datetime import date, datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Depends
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

app = FastAPI(
    title="API Aplicación de Estudio",
    description="Sistema de gestión para estudiantes con tareas, cronograma, estado de ánimo y tutorías",
    version="1.0.0",
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
# USUARIOS
# -------------------------
@app.get("/usuarios", response_model=List[Usuario], tags=["Usuarios"], summary="Listar usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    """Obtiene la lista de todos los usuarios registrados."""
    return svc.get_usuarios(db)


@app.get("/usuarios/{usuario_id}", response_model=Usuario, tags=["Usuarios"], summary="Obtener usuario por ID")
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtiene un usuario específico por su ID."""
    usuario = svc.get_usuario_by_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.post("/usuarios", response_model=Usuario, status_code=201, tags=["Usuarios"], summary="Crear usuario")
def crear_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en el sistema.
    
    - **nombre**: Nombre completo del usuario (requerido)
    - **email**: Email único del usuario (requerido)
    - **password**: Contraseña del usuario (requerido, mínimo 6 caracteres)
    - **rol_id**: ID del rol asignado (opcional)
    """
    try:
        return svc.create_usuario(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/usuarios/{usuario_id}", response_model=Usuario, tags=["Usuarios"], summary="Actualizar usuario")
def actualizar_usuario(usuario_id: int, payload: UsuarioUpdate, db: Session = Depends(get_db)):
    """
    Actualiza la información de un usuario existente.
    
    Solo se actualizarán los campos proporcionados (no nulos).
    """
    try:
        return svc.update_usuario(db, usuario_id, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/usuarios/{usuario_id}", tags=["Usuarios"], summary="Eliminar usuario")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Elimina un usuario del sistema.
    
    **ATENCIÓN**: Esta operación también eliminará:
    - Todas las tareas del usuario
    - Todo el cronograma del usuario
    - Todos los registros de estado de ánimo del usuario
    - Todas las participaciones en tutorías del usuario
    """
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
    db: Session = Depends(get_db)
):
    """Obtiene la lista de tareas con filtros opcionales."""
    return svc.get_tareas(db, usuario_id=usuario_id, estado=estado)


@app.get("/tareas/{tarea_id}", response_model=Tarea, tags=["Tareas"], summary="Obtener tarea por ID")
def obtener_tarea(tarea_id: int, db: Session = Depends(get_db)):
    """Obtiene una tarea específica por su ID."""
    tarea = svc.get_tarea_by_id(db, tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea


@app.post("/tareas", response_model=Tarea, status_code=201, tags=["Tareas"], summary="Crear tarea")
def crear_tarea(payload: TareaCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva tarea para un usuario.
    
    - **titulo**: Título de la tarea (requerido)
    - **descripcion**: Descripción detallada (opcional)
    - **fecha_entrega**: Fecha límite de entrega (opcional)
    - **estado**: Estado inicial (por defecto: pendiente)
    - **usuario_id**: ID del usuario propietario (requerido)
    """
    try:
        return svc.create_tarea(db, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/tareas/{tarea_id}", response_model=Tarea, tags=["Tareas"], summary="Actualizar tarea")
def actualizar_tarea(tarea_id: int, payload: TareaUpdate, db: Session = Depends(get_db)):
    """
    Actualiza una tarea existente.
    
    Solo se actualizarán los campos proporcionados (no nulos).
    """
    try:
        return svc.update_tarea(db, tarea_id, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/tareas/{tarea_id}", tags=["Tareas"], summary="Eliminar tarea")
def eliminar_tarea(tarea_id: int, db: Session = Depends(get_db)):
    """Elimina una tarea del sistema."""
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
    db: Session = Depends(get_db)
):
    """Obtiene la lista de eventos del cronograma con filtros opcionales."""
    return svc.get_cronograma(db, usuario_id=usuario_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@app.get("/cronograma/{cronograma_id}", response_model=Cronograma, tags=["Cronograma"], summary="Obtener evento por ID")
def obtener_cronograma(cronograma_id: int, db: Session = Depends(get_db)):
    """Obtiene un evento específico del cronograma por su ID."""
    cronograma = svc.get_cronograma_by_id(db, cronograma_id)
    if not cronograma:
        raise HTTPException(status_code=404, detail="Evento de cronograma no encontrado")
    return cronograma


@app.post("/cronograma", response_model=Cronograma, status_code=201, tags=["Cronograma"], summary="Crear evento")
def crear_cronograma(payload: CronogramaCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo evento en el cronograma.
    
    - **titulo**: Título del evento (requerido)
    - **descripcion**: Descripción del evento (opcional)
    - **fecha_inicio**: Fecha y hora de inicio (requerido)
    - **fecha_fin**: Fecha y hora de fin (requerido)
    - **usuario_id**: ID del usuario propietario (requerido)
    """
    try:
        return svc.create_cronograma(db, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/cronograma/{cronograma_id}", response_model=Cronograma, tags=["Cronograma"], summary="Actualizar evento")
def actualizar_cronograma(cronograma_id: int, payload: CronogramaUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un evento del cronograma.
    
    Solo se actualizarán los campos proporcionados (no nulos).
    """
    try:
        return svc.update_cronograma(db, cronograma_id, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/cronograma/{cronograma_id}", tags=["Cronograma"], summary="Eliminar evento")
def eliminar_cronograma(cronograma_id: int, db: Session = Depends(get_db)):
    """Elimina un evento del cronograma."""
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
    db: Session = Depends(get_db)
):
    """Obtiene la lista de estados de ánimo con filtros opcionales."""
    return svc.get_estados_animo(db, usuario_id=usuario_id, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)


@app.get("/estados-animo/{estado_id}", response_model=EstadoAnimo, tags=["Estado de Ánimo"], summary="Obtener estado por ID")
def obtener_estado_animo(estado_id: int, db: Session = Depends(get_db)):
    """Obtiene un registro específico de estado de ánimo por su ID."""
    estado = svc.get_estado_animo_by_id(db, estado_id)
    if not estado:
        raise HTTPException(status_code=404, detail="Estado de ánimo no encontrado")
    return estado


@app.post("/estados-animo", response_model=EstadoAnimo, status_code=201, tags=["Estado de Ánimo"], summary="Registrar estado")
def crear_estado_animo(payload: EstadoAnimoCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo estado de ánimo.
    
    - **estado**: Descripción del estado (ej: feliz, triste, motivado, cansado)
    - **comentario**: Comentario adicional (opcional)
    - **fecha**: Fecha del registro (opcional, por defecto hoy)
    - **usuario_id**: ID del usuario (requerido)
    """
    try:
        return svc.create_estado_animo(db, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/estados-animo/{estado_id}", response_model=EstadoAnimo, tags=["Estado de Ánimo"], summary="Actualizar estado")
def actualizar_estado_animo(estado_id: int, payload: EstadoAnimoUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un registro de estado de ánimo.
    
    Solo se actualizarán los campos proporcionados (no nulos).
    """
    try:
        return svc.update_estado_animo(db, estado_id, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/estados-animo/{estado_id}", tags=["Estado de Ánimo"], summary="Eliminar estado")
def eliminar_estado_animo(estado_id: int, db: Session = Depends(get_db)):
    """Elimina un registro de estado de ánimo."""
    try:
        svc.delete_estado_animo(db, estado_id)
        return {"message": "Estado de ánimo eliminado exitosamente"}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))





# -------------------------
# TUTORÍAS
# -------------------------
@app.get("/tutorias", response_model=List[Tutoria], tags=["Tutorías"], summary="Listar tutorías")
def listar_tutorias(db: Session = Depends(get_db)):
    """Obtiene la lista de todas las tutorías programadas."""
    return svc.get_tutorias(db)


@app.get("/tutorias/{tutoria_id}", response_model=Tutoria, tags=["Tutorías"], summary="Obtener tutoría por ID")
def obtener_tutoria(tutoria_id: int, db: Session = Depends(get_db)):
    """Obtiene una tutoría específica por su ID, incluyendo sus participantes."""
    tutoria = svc.get_tutoria_by_id(db, tutoria_id)
    if not tutoria:
        raise HTTPException(status_code=404, detail="Tutoría no encontrada")
    return tutoria


@app.post("/tutorias", response_model=Tutoria, status_code=201, tags=["Tutorías"], summary="Crear tutoría")
def crear_tutoria(payload: TutoriaCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva tutoría.
    
    - **tema**: Tema de la tutoría (requerido)
    - **descripcion**: Descripción detallada (opcional)
    - **fecha**: Fecha y hora programada (requerido)
    """
    return svc.create_tutoria(db, payload)


@app.put("/tutorias/{tutoria_id}", response_model=Tutoria, tags=["Tutorías"], summary="Actualizar tutoría")
def actualizar_tutoria(tutoria_id: int, payload: TutoriaUpdate, db: Session = Depends(get_db)):
    """
    Actualiza una tutoría existente.
    
    Solo se actualizarán los campos proporcionados (no nulos).
    """
    try:
        return svc.update_tutoria(db, tutoria_id, payload)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/tutorias/{tutoria_id}", tags=["Tutorías"], summary="Eliminar tutoría")
def eliminar_tutoria(tutoria_id: int, db: Session = Depends(get_db)):
    """
    Elimina una tutoría del sistema.
    
    **ATENCIÓN**: Esta operación también eliminará todas las participaciones asociadas.
    """
    try:
        svc.delete_tutoria(db, tutoria_id)
        return {"message": "Tutoría eliminada exitosamente"}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -------------------------
# PARTICIPACIONES EN TUTORÍAS
# -------------------------
@app.post("/tutorias/participantes", tags=["Tutorías"], summary="Agregar participante a tutoría")
def agregar_usuario_tutoria(payload: UsuarioTutoriaCreate, db: Session = Depends(get_db)):
    """
    Agrega un usuario como participante de una tutoría.
    
    - **usuario_id**: ID del usuario participante
    - **tutoria_id**: ID de la tutoría
    - **rol_en_tutoria**: Rol del usuario (tutor o estudiante)
    """
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
    db: Session = Depends(get_db)
):
    """
    Remueve un usuario de una tutoría específica.
    
    - **tutoria_id**: ID de la tutoría
    - **usuario_id**: ID del usuario a remover
    - **rol_en_tutoria**: Rol específico a remover (tutor o estudiante)
    """
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
