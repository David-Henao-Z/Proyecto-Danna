# db_functions.py
# ============================================================================
# Funciones CRUD usando SQLAlchemy para interactuar con PostgreSQL
# ============================================================================

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database import get_db, Rol as RolDB, Usuario as UsuarioDB, Tarea as TareaDB
from database import Cronograma as CronogramaDB, EstadoAnimo as EstadoAnimoDB
from database import Tutoria as TutoriaDB, UsuarioTutoria as UsuarioTutoriaDB

from functions import (
    Rol, Usuario, UsuarioCreate, UsuarioUpdate,
    Tarea, TareaCreate, TareaUpdate, EstadoTarea,
    Cronograma, CronogramaCreate, CronogramaUpdate,
    EstadoAnimo, EstadoAnimoCreate, EstadoAnimoUpdate,
    Tutoria, TutoriaCreate, TutoriaUpdate,
    UsuarioTutoriaCreate, RolTutoria
)

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def db_rol_to_pydantic(db_rol: RolDB) -> Rol:
    """Convierte un modelo SQLAlchemy Rol a Pydantic"""
    return Rol(
        id=db_rol.id,
        nombre=db_rol.nombre,
        descripcion=db_rol.descripcion
    )

def db_usuario_to_pydantic(db_usuario: UsuarioDB) -> Usuario:
    """Convierte un modelo SQLAlchemy Usuario a Pydantic"""
    rol = db_rol_to_pydantic(db_usuario.rol) if db_usuario.rol else None
    return Usuario(
        id=db_usuario.id,
        nombre=db_usuario.nombre,
        email=db_usuario.email,
        rol_id=db_usuario.rol_id,
        rol=rol
    )

def db_tarea_to_pydantic(db_tarea: TareaDB) -> Tarea:
    """Convierte un modelo SQLAlchemy Tarea a Pydantic"""
    usuario = db_usuario_to_pydantic(db_tarea.usuario) if db_tarea.usuario else None
    return Tarea(
        id=db_tarea.id,
        titulo=db_tarea.titulo,
        descripcion=db_tarea.descripcion,
        fecha_entrega=db_tarea.fecha_entrega,
        estado=EstadoTarea(db_tarea.estado),
        usuario_id=db_tarea.usuario_id,
        usuario=usuario
    )

def db_cronograma_to_pydantic(db_cronograma: CronogramaDB) -> Cronograma:
    """Convierte un modelo SQLAlchemy Cronograma a Pydantic"""
    usuario = db_usuario_to_pydantic(db_cronograma.usuario) if db_cronograma.usuario else None
    return Cronograma(
        id=db_cronograma.id,
        titulo=db_cronograma.titulo,
        descripcion=db_cronograma.descripcion,
        fecha_inicio=db_cronograma.fecha_inicio,
        fecha_fin=db_cronograma.fecha_fin,
        usuario_id=db_cronograma.usuario_id,
        usuario=usuario
    )

def db_estado_animo_to_pydantic(db_estado: EstadoAnimoDB) -> EstadoAnimo:
    """Convierte un modelo SQLAlchemy EstadoAnimo a Pydantic"""
    usuario = db_usuario_to_pydantic(db_estado.usuario) if db_estado.usuario else None
    return EstadoAnimo(
        id=db_estado.id,
        usuario_id=db_estado.usuario_id,
        fecha=db_estado.fecha,
        estado=db_estado.estado,
        comentario=db_estado.comentario,
        usuario=usuario
    )

def db_tutoria_to_pydantic(db_tutoria: TutoriaDB) -> Tutoria:
    """Convierte un modelo SQLAlchemy Tutoria a Pydantic"""
    participantes = []
    for participante in db_tutoria.participantes:
        usuario = db_usuario_to_pydantic(participante.usuario)
        participantes.append({
            "usuario": usuario.dict(),
            "rol": participante.rol_en_tutoria
        })
    
    return Tutoria(
        id=db_tutoria.id,
        tema=db_tutoria.tema,
        descripcion=db_tutoria.descripcion,
        fecha=db_tutoria.fecha,
        participantes=participantes
    )

# ============================================================================
# FUNCIONES CRUD - ROLES
# ============================================================================

def get_roles(db: Session) -> List[Rol]:
    """Obtiene todos los roles"""
    db_roles = db.query(RolDB).all()
    return [db_rol_to_pydantic(rol) for rol in db_roles]

def get_rol_by_id(db: Session, rol_id: int) -> Optional[Rol]:
    """Obtiene un rol por ID"""
    db_rol = db.query(RolDB).filter(RolDB.id == rol_id).first()
    return db_rol_to_pydantic(db_rol) if db_rol else None

# ============================================================================
# FUNCIONES CRUD - USUARIOS
# ============================================================================

def get_usuarios(db: Session) -> List[Usuario]:
    """Obtiene todos los usuarios"""
    db_usuarios = db.query(UsuarioDB).all()
    return [db_usuario_to_pydantic(usuario) for usuario in db_usuarios]

def get_usuario_by_id(db: Session, usuario_id: int) -> Optional[Usuario]:
    """Obtiene un usuario por ID"""
    db_usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    return db_usuario_to_pydantic(db_usuario) if db_usuario else None

def get_usuario_by_email(db: Session, email: str) -> Optional[UsuarioDB]:
    """Obtiene un usuario por email (retorna modelo SQLAlchemy)"""
    return db.query(UsuarioDB).filter(UsuarioDB.email == email).first()

def obtener_usuario_por_email(db: Session, email: str) -> Optional[UsuarioDB]:
    """Obtiene un usuario por email - alias para autenticación"""
    return get_usuario_by_email(db, email)

def create_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
    """Crea un nuevo usuario"""
    # Verificar que el email no exista
    if get_usuario_by_email(db, usuario.email):
        raise ValueError("El email ya está registrado")
    
    # Verificar que el rol existe si se proporciona
    if usuario.rol_id and not db.query(RolDB).filter(RolDB.id == usuario.rol_id).first():
        raise KeyError("Rol no encontrado")
    
    db_usuario = UsuarioDB(
        nombre=usuario.nombre,
        email=usuario.email,
        password=usuario.password,  # En producción, hashear la contraseña
        rol_id=usuario.rol_id
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario_to_pydantic(db_usuario)

def crear_usuario_con_hash(db: Session, usuario: UsuarioCreate, password_hash: str) -> Usuario:
    """Crea un nuevo usuario con contraseña ya hasheada"""
    # Verificar que el email no exista
    if get_usuario_by_email(db, usuario.email):
        raise ValueError("El email ya está registrado")
    
    # Verificar que el rol existe si se proporciona
    if usuario.rol_id and not db.query(RolDB).filter(RolDB.id == usuario.rol_id).first():
        raise KeyError("Rol no encontrado")
    
    db_usuario = UsuarioDB(
        nombre=usuario.nombre,
        email=usuario.email,
        password=password_hash,  # Usar el hash proporcionado
        rol_id=usuario.rol_id
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario_to_pydantic(db_usuario)

def update_usuario(db: Session, usuario_id: int, usuario_update: UsuarioUpdate) -> Usuario:
    """Actualiza un usuario existente"""
    db_usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not db_usuario:
        raise KeyError("Usuario no encontrado")
    
    # Verificar email único si se está actualizando
    if usuario_update.email:
        existing_user = get_usuario_by_email(db, usuario_update.email)
        if existing_user and existing_user.id != usuario_id:
            raise ValueError("El email ya está registrado")
    
    # Verificar que el rol existe si se proporciona
    if usuario_update.rol_id and not db.query(RolDB).filter(RolDB.id == usuario_update.rol_id).first():
        raise KeyError("Rol no encontrado")
    
    # Actualizar campos no nulos
    if usuario_update.nombre is not None:
        db_usuario.nombre = usuario_update.nombre
    if usuario_update.email is not None:
        db_usuario.email = usuario_update.email
    if usuario_update.rol_id is not None:
        db_usuario.rol_id = usuario_update.rol_id
    
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario_to_pydantic(db_usuario)

def delete_usuario(db: Session, usuario_id: int) -> None:
    """Elimina un usuario"""
    db_usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not db_usuario:
        raise KeyError("Usuario no encontrado")
    
    db.delete(db_usuario)
    db.commit()

# ============================================================================
# FUNCIONES CRUD - TAREAS
# ============================================================================

def get_tareas(db: Session, usuario_id: Optional[int] = None, estado: Optional[EstadoTarea] = None) -> List[Tarea]:
    """Obtiene tareas con filtros opcionales"""
    query = db.query(TareaDB)
    
    if usuario_id:
        query = query.filter(TareaDB.usuario_id == usuario_id)
    
    if estado:
        query = query.filter(TareaDB.estado == estado.value)
    
    db_tareas = query.all()
    return [db_tarea_to_pydantic(tarea) for tarea in db_tareas]

def get_tarea_by_id(db: Session, tarea_id: int) -> Optional[Tarea]:
    """Obtiene una tarea por ID"""
    db_tarea = db.query(TareaDB).filter(TareaDB.id == tarea_id).first()
    return db_tarea_to_pydantic(db_tarea) if db_tarea else None

def create_tarea(db: Session, tarea: TareaCreate) -> Tarea:
    """Crea una nueva tarea"""
    # Verificar que el usuario existe
    if not db.query(UsuarioDB).filter(UsuarioDB.id == tarea.usuario_id).first():
        raise KeyError("Usuario no encontrado")
    
    db_tarea = TareaDB(
        titulo=tarea.titulo,
        descripcion=tarea.descripcion,
        fecha_entrega=tarea.fecha_entrega,
        estado=tarea.estado.value,
        usuario_id=tarea.usuario_id
    )
    
    db.add(db_tarea)
    db.commit()
    db.refresh(db_tarea)
    
    return db_tarea_to_pydantic(db_tarea)

def update_tarea(db: Session, tarea_id: int, tarea_update: TareaUpdate) -> Tarea:
    """Actualiza una tarea existente"""
    db_tarea = db.query(TareaDB).filter(TareaDB.id == tarea_id).first()
    if not db_tarea:
        raise KeyError("Tarea no encontrada")
    
    # Actualizar campos no nulos
    if tarea_update.titulo is not None:
        db_tarea.titulo = tarea_update.titulo
    if tarea_update.descripcion is not None:
        db_tarea.descripcion = tarea_update.descripcion
    if tarea_update.fecha_entrega is not None:
        db_tarea.fecha_entrega = tarea_update.fecha_entrega
    if tarea_update.estado is not None:
        db_tarea.estado = tarea_update.estado.value
    
    db.commit()
    db.refresh(db_tarea)
    
    return db_tarea_to_pydantic(db_tarea)

def delete_tarea(db: Session, tarea_id: int) -> None:
    """Elimina una tarea"""
    db_tarea = db.query(TareaDB).filter(TareaDB.id == tarea_id).first()
    if not db_tarea:
        raise KeyError("Tarea no encontrada")
    
    db.delete(db_tarea)
    db.commit()

# ============================================================================
# FUNCIONES CRUD - CRONOGRAMA
# ============================================================================

def get_cronograma(db: Session, usuario_id: Optional[int] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None) -> List[Cronograma]:
    """Obtiene eventos del cronograma con filtros opcionales"""
    query = db.query(CronogramaDB)
    
    if usuario_id:
        query = query.filter(CronogramaDB.usuario_id == usuario_id)
    
    if fecha_inicio:
        query = query.filter(CronogramaDB.fecha_inicio >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(CronogramaDB.fecha_fin <= fecha_fin)
    
    db_cronograma = query.all()
    return [db_cronograma_to_pydantic(evento) for evento in db_cronograma]

def get_cronograma_by_id(db: Session, cronograma_id: int) -> Optional[Cronograma]:
    """Obtiene un evento del cronograma por ID"""
    db_cronograma = db.query(CronogramaDB).filter(CronogramaDB.id == cronograma_id).first()
    return db_cronograma_to_pydantic(db_cronograma) if db_cronograma else None

def create_cronograma(db: Session, cronograma: CronogramaCreate) -> Cronograma:
    """Crea un nuevo evento en el cronograma"""
    # Verificar que el usuario existe
    if not db.query(UsuarioDB).filter(UsuarioDB.id == cronograma.usuario_id).first():
        raise KeyError("Usuario no encontrado")
    
    # Validar fechas
    if cronograma.fecha_inicio >= cronograma.fecha_fin:
        raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
    
    db_cronograma = CronogramaDB(
        titulo=cronograma.titulo,
        descripcion=cronograma.descripcion,
        fecha_inicio=cronograma.fecha_inicio,
        fecha_fin=cronograma.fecha_fin,
        usuario_id=cronograma.usuario_id
    )
    
    db.add(db_cronograma)
    db.commit()
    db.refresh(db_cronograma)
    
    return db_cronograma_to_pydantic(db_cronograma)

def update_cronograma(db: Session, cronograma_id: int, cronograma_update: CronogramaUpdate) -> Cronograma:
    """Actualiza un evento del cronograma"""
    db_cronograma = db.query(CronogramaDB).filter(CronogramaDB.id == cronograma_id).first()
    if not db_cronograma:
        raise KeyError("Evento de cronograma no encontrado")
    
    # Actualizar campos no nulos
    if cronograma_update.titulo is not None:
        db_cronograma.titulo = cronograma_update.titulo
    if cronograma_update.descripcion is not None:
        db_cronograma.descripcion = cronograma_update.descripcion
    if cronograma_update.fecha_inicio is not None:
        db_cronograma.fecha_inicio = cronograma_update.fecha_inicio
    if cronograma_update.fecha_fin is not None:
        db_cronograma.fecha_fin = cronograma_update.fecha_fin
    
    # Validar fechas después de la actualización
    if db_cronograma.fecha_inicio >= db_cronograma.fecha_fin:
        raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
    
    db.commit()
    db.refresh(db_cronograma)
    
    return db_cronograma_to_pydantic(db_cronograma)

def delete_cronograma(db: Session, cronograma_id: int) -> None:
    """Elimina un evento del cronograma"""
    db_cronograma = db.query(CronogramaDB).filter(CronogramaDB.id == cronograma_id).first()
    if not db_cronograma:
        raise KeyError("Evento de cronograma no encontrado")
    
    db.delete(db_cronograma)
    db.commit()

# ============================================================================
# FUNCIONES CRUD - ESTADO DE ÁNIMO
# ============================================================================

def get_estados_animo(db: Session, usuario_id: Optional[int] = None, fecha_desde: Optional[date] = None, fecha_hasta: Optional[date] = None) -> List[EstadoAnimo]:
    """Obtiene estados de ánimo con filtros opcionales"""
    query = db.query(EstadoAnimoDB)
    
    if usuario_id:
        query = query.filter(EstadoAnimoDB.usuario_id == usuario_id)
    
    if fecha_desde:
        query = query.filter(EstadoAnimoDB.fecha >= fecha_desde)
    
    if fecha_hasta:
        query = query.filter(EstadoAnimoDB.fecha <= fecha_hasta)
    
    db_estados = query.all()
    return [db_estado_animo_to_pydantic(estado) for estado in db_estados]

def get_estado_animo_by_id(db: Session, estado_id: int) -> Optional[EstadoAnimo]:
    """Obtiene un estado de ánimo por ID"""
    db_estado = db.query(EstadoAnimoDB).filter(EstadoAnimoDB.id == estado_id).first()
    return db_estado_animo_to_pydantic(db_estado) if db_estado else None

def create_estado_animo(db: Session, estado_animo: EstadoAnimoCreate) -> EstadoAnimo:
    """Crea un nuevo registro de estado de ánimo"""
    # Verificar que el usuario existe
    if not db.query(UsuarioDB).filter(UsuarioDB.id == estado_animo.usuario_id).first():
        raise KeyError("Usuario no encontrado")
    
    fecha_estado = estado_animo.fecha if estado_animo.fecha else date.today()
    
    db_estado = EstadoAnimoDB(
        usuario_id=estado_animo.usuario_id,
        fecha=fecha_estado,
        estado=estado_animo.estado,
        comentario=estado_animo.comentario
    )
    
    db.add(db_estado)
    db.commit()
    db.refresh(db_estado)
    
    return db_estado_animo_to_pydantic(db_estado)

def update_estado_animo(db: Session, estado_id: int, estado_update: EstadoAnimoUpdate) -> EstadoAnimo:
    """Actualiza un registro de estado de ánimo"""
    db_estado = db.query(EstadoAnimoDB).filter(EstadoAnimoDB.id == estado_id).first()
    if not db_estado:
        raise KeyError("Estado de ánimo no encontrado")
    
    # Actualizar campos no nulos
    if estado_update.estado is not None:
        db_estado.estado = estado_update.estado
    if estado_update.comentario is not None:
        db_estado.comentario = estado_update.comentario
    
    db.commit()
    db.refresh(db_estado)
    
    return db_estado_animo_to_pydantic(db_estado)

def delete_estado_animo(db: Session, estado_id: int) -> None:
    """Elimina un registro de estado de ánimo"""
    db_estado = db.query(EstadoAnimoDB).filter(EstadoAnimoDB.id == estado_id).first()
    if not db_estado:
        raise KeyError("Estado de ánimo no encontrado")
    
    db.delete(db_estado)
    db.commit()

# ============================================================================
# FUNCIONES CRUD - TUTORÍAS
# ============================================================================

def get_tutorias(db: Session) -> List[Tutoria]:
    """Obtiene todas las tutorías"""
    db_tutorias = db.query(TutoriaDB).all()
    return [db_tutoria_to_pydantic(tutoria) for tutoria in db_tutorias]

def get_tutoria_by_id(db: Session, tutoria_id: int) -> Optional[Tutoria]:
    """Obtiene una tutoría por ID"""
    db_tutoria = db.query(TutoriaDB).filter(TutoriaDB.id == tutoria_id).first()
    return db_tutoria_to_pydantic(db_tutoria) if db_tutoria else None

def create_tutoria(db: Session, tutoria: TutoriaCreate) -> Tutoria:
    """Crea una nueva tutoría"""
    db_tutoria = TutoriaDB(
        tema=tutoria.tema,
        descripcion=tutoria.descripcion,
        fecha=tutoria.fecha
    )
    
    db.add(db_tutoria)
    db.commit()
    db.refresh(db_tutoria)
    
    return db_tutoria_to_pydantic(db_tutoria)

def update_tutoria(db: Session, tutoria_id: int, tutoria_update: TutoriaUpdate) -> Tutoria:
    """Actualiza una tutoría existente"""
    db_tutoria = db.query(TutoriaDB).filter(TutoriaDB.id == tutoria_id).first()
    if not db_tutoria:
        raise KeyError("Tutoría no encontrada")
    
    # Actualizar campos no nulos
    if tutoria_update.tema is not None:
        db_tutoria.tema = tutoria_update.tema
    if tutoria_update.descripcion is not None:
        db_tutoria.descripcion = tutoria_update.descripcion
    if tutoria_update.fecha is not None:
        db_tutoria.fecha = tutoria_update.fecha
    
    db.commit()
    db.refresh(db_tutoria)
    
    return db_tutoria_to_pydantic(db_tutoria)

def delete_tutoria(db: Session, tutoria_id: int) -> None:
    """Elimina una tutoría"""
    db_tutoria = db.query(TutoriaDB).filter(TutoriaDB.id == tutoria_id).first()
    if not db_tutoria:
        raise KeyError("Tutoría no encontrada")
    
    db.delete(db_tutoria)
    db.commit()

def add_usuario_tutoria(db: Session, usuario_tutoria: UsuarioTutoriaCreate) -> Dict[str, str]:
    """Agrega un usuario a una tutoría"""
    # Verificar que el usuario existe
    if not db.query(UsuarioDB).filter(UsuarioDB.id == usuario_tutoria.usuario_id).first():
        raise KeyError("Usuario no encontrado")
    
    # Verificar que la tutoría existe
    if not db.query(TutoriaDB).filter(TutoriaDB.id == usuario_tutoria.tutoria_id).first():
        raise KeyError("Tutoría no encontrada")
    
    # Verificar que no existe ya esta combinación
    existing = db.query(UsuarioTutoriaDB).filter(
        and_(
            UsuarioTutoriaDB.usuario_id == usuario_tutoria.usuario_id,
            UsuarioTutoriaDB.tutoria_id == usuario_tutoria.tutoria_id,
            UsuarioTutoriaDB.rol_en_tutoria == usuario_tutoria.rol_en_tutoria.value
        )
    ).first()
    
    if existing:
        raise ValueError("El usuario ya está registrado en esta tutoría con este rol")
    
    db_usuario_tutoria = UsuarioTutoriaDB(
        usuario_id=usuario_tutoria.usuario_id,
        tutoria_id=usuario_tutoria.tutoria_id,
        rol_en_tutoria=usuario_tutoria.rol_en_tutoria.value
    )
    
    db.add(db_usuario_tutoria)
    db.commit()
    
    return {"message": "Usuario agregado a la tutoría exitosamente"}

def remove_usuario_tutoria(db: Session, usuario_id: int, tutoria_id: int, rol_en_tutoria: RolTutoria) -> Dict[str, str]:
    """Remueve un usuario de una tutoría"""
    db_usuario_tutoria = db.query(UsuarioTutoriaDB).filter(
        and_(
            UsuarioTutoriaDB.usuario_id == usuario_id,
            UsuarioTutoriaDB.tutoria_id == tutoria_id,
            UsuarioTutoriaDB.rol_en_tutoria == rol_en_tutoria.value
        )
    ).first()
    
    if not db_usuario_tutoria:
        raise KeyError("Participación en tutoría no encontrada")
    
    db.delete(db_usuario_tutoria)
    db.commit()
    
    return {"message": "Usuario removido de la tutoría exitosamente"}
