# functions.py
# ============================================================================
# Módulo con la **lógica de negocio** para la aplicación de estudio.
# Contiene modelos Pydantic y funciones CRUD que manipulan datos en memoria.
# ============================================================================

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, constr

# -------------------------
# ENUMS
# -------------------------
class EstadoTarea(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"

class RolTutoria(str, Enum):
    TUTOR = "tutor"
    ESTUDIANTE = "estudiante"

# -------------------------
# MODELOS PYDANTIC
# -------------------------

# Roles
class RolBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class RolCreate(RolBase):
    pass

class Rol(RolBase):
    id: int

    class Config:
        from_attributes = True

# Usuarios
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    rol_id: Optional[int] = None

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    rol_id: Optional[int] = None

class Usuario(UsuarioBase):
    id: int
    rol: Optional[Rol] = None

    class Config:
        from_attributes = True

# Tareas
class TareaBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_entrega: Optional[date] = None
    estado: EstadoTarea = EstadoTarea.PENDIENTE

class TareaCreate(TareaBase):
    usuario_id: int

class TareaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_entrega: Optional[date] = None
    estado: Optional[EstadoTarea] = None

class Tarea(TareaBase):
    id: int
    usuario_id: int
    usuario: Optional[Usuario] = None

    class Config:
        from_attributes = True

# Cronograma
class CronogramaBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_inicio: datetime
    fecha_fin: datetime

class CronogramaCreate(CronogramaBase):
    usuario_id: int

class CronogramaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None

class Cronograma(CronogramaBase):
    id: int
    usuario_id: int
    usuario: Optional[Usuario] = None

    class Config:
        from_attributes = True

# Estado de Ánimo
class EstadoAnimoBase(BaseModel):
    estado: str
    comentario: Optional[str] = None
    fecha: Optional[date] = None

class EstadoAnimoCreate(EstadoAnimoBase):
    usuario_id: int

class EstadoAnimoUpdate(BaseModel):
    estado: Optional[str] = None
    comentario: Optional[str] = None

class EstadoAnimo(EstadoAnimoBase):
    id: int
    usuario_id: int
    usuario: Optional[Usuario] = None

    class Config:
        from_attributes = True

# Tutorías
class TutoriaBase(BaseModel):
    tema: str
    descripcion: Optional[str] = None
    fecha: datetime

class TutoriaCreate(TutoriaBase):
    pass

class TutoriaUpdate(BaseModel):
    tema: Optional[str] = None
    descripcion: Optional[str] = None
    fecha: Optional[datetime] = None

class Tutoria(TutoriaBase):
    id: int
    participantes: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True

class UsuarioTutoriaCreate(BaseModel):
    usuario_id: int
    tutoria_id: int
    rol_en_tutoria: RolTutoria

# -------------------------
# ALMACENAMIENTO EN MEMORIA
# -------------------------
roles_db: List[Rol] = [
    Rol(id=1, nombre="Administrador", descripcion="Acceso completo al sistema"),
    Rol(id=2, nombre="Estudiante", descripcion="Usuario estudiante básico"),
    Rol(id=3, nombre="Tutor", descripcion="Usuario que puede dar tutorías"),
]

usuarios_db: List[Dict[str, Any]] = []
tareas_db: List[Dict[str, Any]] = []
cronograma_db: List[Dict[str, Any]] = []
estado_animo_db: List[Dict[str, Any]] = []
tutorias_db: List[Dict[str, Any]] = []
usuario_tutorias_db: List[Dict[str, Any]] = []

# Contadores para IDs
next_usuario_id = 1
next_tarea_id = 1
next_cronograma_id = 1
next_estado_animo_id = 1
next_tutoria_id = 1

# -------------------------
# FUNCIONES AUXILIARES
# -------------------------
def obtener_rol_por_id(rol_id: int) -> Optional[Rol]:
    return next((rol for rol in roles_db if rol.id == rol_id), None)

def usuario_dict_to_model(usuario_dict: Dict[str, Any]) -> Usuario:
    rol = obtener_rol_por_id(usuario_dict.get("rol_id")) if usuario_dict.get("rol_id") else None
    return Usuario(
        id=usuario_dict["id"],
        nombre=usuario_dict["nombre"],
        email=usuario_dict["email"],
        rol_id=usuario_dict.get("rol_id"),
        rol=rol
    )

# -------------------------
# FUNCIONES CRUD - ROLES
# -------------------------
def listar_roles() -> List[Rol]:
    return roles_db

def obtener_rol(rol_id: int) -> Optional[Rol]:
    return obtener_rol_por_id(rol_id)

# -------------------------
# FUNCIONES CRUD - USUARIOS
# -------------------------
def listar_usuarios() -> List[Usuario]:
    return [usuario_dict_to_model(u) for u in usuarios_db]

def obtener_usuario(usuario_id: int) -> Optional[Usuario]:
    usuario_dict = next((u for u in usuarios_db if u["id"] == usuario_id), None)
    return usuario_dict_to_model(usuario_dict) if usuario_dict else None

def crear_usuario(payload: UsuarioCreate) -> Usuario:
    global next_usuario_id
    
    # Validar que el email no exista
    if any(u["email"] == payload.email for u in usuarios_db):
        raise ValueError("El email ya está registrado")
    
    # Validar que el rol existe si se proporciona
    if payload.rol_id and not obtener_rol_por_id(payload.rol_id):
        raise KeyError("Rol no encontrado")
    
    usuario_dict = {
        "id": next_usuario_id,
        "nombre": payload.nombre,
        "email": payload.email,
        "password": payload.password,  # En producción, hashear la contraseña
        "rol_id": payload.rol_id
    }
    
    usuarios_db.append(usuario_dict)
    next_usuario_id += 1
    
    return usuario_dict_to_model(usuario_dict)

def actualizar_usuario(usuario_id: int, payload: UsuarioUpdate) -> Usuario:
    usuario_dict = next((u for u in usuarios_db if u["id"] == usuario_id), None)
    if not usuario_dict:
        raise KeyError("Usuario no encontrado")
    
    # Validar email único si se está actualizando
    if payload.email and any(u["email"] == payload.email and u["id"] != usuario_id for u in usuarios_db):
        raise ValueError("El email ya está registrado")
    
    # Validar que el rol existe si se proporciona
    if payload.rol_id and not obtener_rol_por_id(payload.rol_id):
        raise KeyError("Rol no encontrado")
    
    # Actualizar campos no nulos
    if payload.nombre is not None:
        usuario_dict["nombre"] = payload.nombre
    if payload.email is not None:
        usuario_dict["email"] = payload.email
    if payload.rol_id is not None:
        usuario_dict["rol_id"] = payload.rol_id
    
    return usuario_dict_to_model(usuario_dict)

def eliminar_usuario(usuario_id: int) -> None:
    usuario_dict = next((u for u in usuarios_db if u["id"] == usuario_id), None)
    if not usuario_dict:
        raise KeyError("Usuario no encontrado")
    
    # Eliminar tareas asociadas
    global tareas_db
    tareas_db = [t for t in tareas_db if t["usuario_id"] != usuario_id]
    
    # Eliminar cronograma asociado
    global cronograma_db
    cronograma_db = [c for c in cronograma_db if c["usuario_id"] != usuario_id]
    
    # Eliminar estados de ánimo asociados
    global estado_animo_db
    estado_animo_db = [e for e in estado_animo_db if e["usuario_id"] != usuario_id]
    
    # Eliminar participaciones en tutorías
    global usuario_tutorias_db
    usuario_tutorias_db = [ut for ut in usuario_tutorias_db if ut["usuario_id"] != usuario_id]
    
    # Eliminar usuario
    usuarios_db.remove(usuario_dict)

# -------------------------
# FUNCIONES CRUD - TAREAS
# -------------------------
def listar_tareas(usuario_id: Optional[int] = None, estado: Optional[EstadoTarea] = None) -> List[Tarea]:
    tareas_filtradas = tareas_db
    
    if usuario_id:
        tareas_filtradas = [t for t in tareas_filtradas if t["usuario_id"] == usuario_id]
    
    if estado:
        tareas_filtradas = [t for t in tareas_filtradas if t["estado"] == estado.value]
    
    result = []
    for tarea_dict in tareas_filtradas:
        usuario = obtener_usuario(tarea_dict["usuario_id"])
        tarea = Tarea(
            id=tarea_dict["id"],
            titulo=tarea_dict["titulo"],
            descripcion=tarea_dict.get("descripcion"),
            fecha_entrega=tarea_dict.get("fecha_entrega"),
            estado=tarea_dict["estado"],
            usuario_id=tarea_dict["usuario_id"],
            usuario=usuario
        )
        result.append(tarea)
    
    return result

def obtener_tarea(tarea_id: int) -> Optional[Tarea]:
    tarea_dict = next((t for t in tareas_db if t["id"] == tarea_id), None)
    if not tarea_dict:
        return None
    
    usuario = obtener_usuario(tarea_dict["usuario_id"])
    return Tarea(
        id=tarea_dict["id"],
        titulo=tarea_dict["titulo"],
        descripcion=tarea_dict.get("descripcion"),
        fecha_entrega=tarea_dict.get("fecha_entrega"),
        estado=tarea_dict["estado"],
        usuario_id=tarea_dict["usuario_id"],
        usuario=usuario
    )

def crear_tarea(payload: TareaCreate) -> Tarea:
    global next_tarea_id
    
    # Validar que el usuario existe
    if not obtener_usuario(payload.usuario_id):
        raise KeyError("Usuario no encontrado")
    
    tarea_dict = {
        "id": next_tarea_id,
        "titulo": payload.titulo,
        "descripcion": payload.descripcion,
        "fecha_entrega": payload.fecha_entrega,
        "estado": payload.estado.value,
        "usuario_id": payload.usuario_id
    }
    
    tareas_db.append(tarea_dict)
    next_tarea_id += 1
    
    return obtener_tarea(tarea_dict["id"])

def actualizar_tarea(tarea_id: int, payload: TareaUpdate) -> Tarea:
    tarea_dict = next((t for t in tareas_db if t["id"] == tarea_id), None)
    if not tarea_dict:
        raise KeyError("Tarea no encontrada")
    
    # Actualizar campos no nulos
    if payload.titulo is not None:
        tarea_dict["titulo"] = payload.titulo
    if payload.descripcion is not None:
        tarea_dict["descripcion"] = payload.descripcion
    if payload.fecha_entrega is not None:
        tarea_dict["fecha_entrega"] = payload.fecha_entrega
    if payload.estado is not None:
        tarea_dict["estado"] = payload.estado.value
    
    return obtener_tarea(tarea_id)

def eliminar_tarea(tarea_id: int) -> None:
    tarea_dict = next((t for t in tareas_db if t["id"] == tarea_id), None)
    if not tarea_dict:
        raise KeyError("Tarea no encontrada")
    
    tareas_db.remove(tarea_dict)

# -------------------------
# FUNCIONES CRUD - CRONOGRAMA
# -------------------------
def listar_cronograma(usuario_id: Optional[int] = None, fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None) -> List[Cronograma]:
    cronograma_filtrado = cronograma_db
    
    if usuario_id:
        cronograma_filtrado = [c for c in cronograma_filtrado if c["usuario_id"] == usuario_id]
    
    if fecha_inicio:
        cronograma_filtrado = [c for c in cronograma_filtrado if c["fecha_inicio"].date() >= fecha_inicio]
    
    if fecha_fin:
        cronograma_filtrado = [c for c in cronograma_filtrado if c["fecha_fin"].date() <= fecha_fin]
    
    result = []
    for cronograma_dict in cronograma_filtrado:
        usuario = obtener_usuario(cronograma_dict["usuario_id"])
        cronograma = Cronograma(
            id=cronograma_dict["id"],
            titulo=cronograma_dict["titulo"],
            descripcion=cronograma_dict.get("descripcion"),
            fecha_inicio=cronograma_dict["fecha_inicio"],
            fecha_fin=cronograma_dict["fecha_fin"],
            usuario_id=cronograma_dict["usuario_id"],
            usuario=usuario
        )
        result.append(cronograma)
    
    return result

def obtener_cronograma(cronograma_id: int) -> Optional[Cronograma]:
    cronograma_dict = next((c for c in cronograma_db if c["id"] == cronograma_id), None)
    if not cronograma_dict:
        return None
    
    usuario = obtener_usuario(cronograma_dict["usuario_id"])
    return Cronograma(
        id=cronograma_dict["id"],
        titulo=cronograma_dict["titulo"],
        descripcion=cronograma_dict.get("descripcion"),
        fecha_inicio=cronograma_dict["fecha_inicio"],
        fecha_fin=cronograma_dict["fecha_fin"],
        usuario_id=cronograma_dict["usuario_id"],
        usuario=usuario
    )

def crear_cronograma(payload: CronogramaCreate) -> Cronograma:
    global next_cronograma_id
    
    # Validar que el usuario existe
    if not obtener_usuario(payload.usuario_id):
        raise KeyError("Usuario no encontrado")
    
    # Validar fechas
    if payload.fecha_inicio >= payload.fecha_fin:
        raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
    
    cronograma_dict = {
        "id": next_cronograma_id,
        "titulo": payload.titulo,
        "descripcion": payload.descripcion,
        "fecha_inicio": payload.fecha_inicio,
        "fecha_fin": payload.fecha_fin,
        "usuario_id": payload.usuario_id
    }
    
    cronograma_db.append(cronograma_dict)
    next_cronograma_id += 1
    
    return obtener_cronograma(cronograma_dict["id"])

def actualizar_cronograma(cronograma_id: int, payload: CronogramaUpdate) -> Cronograma:
    cronograma_dict = next((c for c in cronograma_db if c["id"] == cronograma_id), None)
    if not cronograma_dict:
        raise KeyError("Evento de cronograma no encontrado")
    
    # Actualizar campos no nulos
    if payload.titulo is not None:
        cronograma_dict["titulo"] = payload.titulo
    if payload.descripcion is not None:
        cronograma_dict["descripcion"] = payload.descripcion
    if payload.fecha_inicio is not None:
        cronograma_dict["fecha_inicio"] = payload.fecha_inicio
    if payload.fecha_fin is not None:
        cronograma_dict["fecha_fin"] = payload.fecha_fin
    
    # Validar fechas después de la actualización
    if cronograma_dict["fecha_inicio"] >= cronograma_dict["fecha_fin"]:
        raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
    
    return obtener_cronograma(cronograma_id)

def eliminar_cronograma(cronograma_id: int) -> None:
    cronograma_dict = next((c for c in cronograma_db if c["id"] == cronograma_id), None)
    if not cronograma_dict:
        raise KeyError("Evento de cronograma no encontrado")
    
    cronograma_db.remove(cronograma_dict)

# -------------------------
# FUNCIONES CRUD - ESTADO DE ÁNIMO
# -------------------------
def listar_estados_animo(usuario_id: Optional[int] = None, fecha_desde: Optional[date] = None, fecha_hasta: Optional[date] = None) -> List[EstadoAnimo]:
    estados_filtrados = estado_animo_db
    
    if usuario_id:
        estados_filtrados = [e for e in estados_filtrados if e["usuario_id"] == usuario_id]
    
    if fecha_desde:
        estados_filtrados = [e for e in estados_filtrados if e["fecha"] >= fecha_desde]
    
    if fecha_hasta:
        estados_filtrados = [e for e in estados_filtrados if e["fecha"] <= fecha_hasta]
    
    result = []
    for estado_dict in estados_filtrados:
        usuario = obtener_usuario(estado_dict["usuario_id"])
        estado = EstadoAnimo(
            id=estado_dict["id"],
            usuario_id=estado_dict["usuario_id"],
            fecha=estado_dict["fecha"],
            estado=estado_dict["estado"],
            comentario=estado_dict.get("comentario"),
            usuario=usuario
        )
        result.append(estado)
    
    return result

def obtener_estado_animo(estado_id: int) -> Optional[EstadoAnimo]:
    estado_dict = next((e for e in estado_animo_db if e["id"] == estado_id), None)
    if not estado_dict:
        return None
    
    usuario = obtener_usuario(estado_dict["usuario_id"])
    return EstadoAnimo(
        id=estado_dict["id"],
        usuario_id=estado_dict["usuario_id"],
        fecha=estado_dict["fecha"],
        estado=estado_dict["estado"],
        comentario=estado_dict.get("comentario"),
        usuario=usuario
    )

def crear_estado_animo(payload: EstadoAnimoCreate) -> EstadoAnimo:
    global next_estado_animo_id
    
    # Validar que el usuario existe
    if not obtener_usuario(payload.usuario_id):
        raise KeyError("Usuario no encontrado")
    
    fecha_estado = payload.fecha if payload.fecha else date.today()
    
    estado_dict = {
        "id": next_estado_animo_id,
        "usuario_id": payload.usuario_id,
        "fecha": fecha_estado,
        "estado": payload.estado,
        "comentario": payload.comentario
    }
    
    estado_animo_db.append(estado_dict)
    next_estado_animo_id += 1
    
    return obtener_estado_animo(estado_dict["id"])

def actualizar_estado_animo(estado_id: int, payload: EstadoAnimoUpdate) -> EstadoAnimo:
    estado_dict = next((e for e in estado_animo_db if e["id"] == estado_id), None)
    if not estado_dict:
        raise KeyError("Estado de ánimo no encontrado")
    
    # Actualizar campos no nulos
    if payload.estado is not None:
        estado_dict["estado"] = payload.estado
    if payload.comentario is not None:
        estado_dict["comentario"] = payload.comentario
    
    return obtener_estado_animo(estado_id)

def eliminar_estado_animo(estado_id: int) -> None:
    estado_dict = next((e for e in estado_animo_db if e["id"] == estado_id), None)
    if not estado_dict:
        raise KeyError("Estado de ánimo no encontrado")
    
    estado_animo_db.remove(estado_dict)

# -------------------------
# FUNCIONES CRUD - TUTORÍAS
# -------------------------
def listar_tutorias() -> List[Tutoria]:
    result = []
    for tutoria_dict in tutorias_db:
        # Obtener participantes
        participantes = []
        for ut in usuario_tutorias_db:
            if ut["tutoria_id"] == tutoria_dict["id"]:
                usuario = obtener_usuario(ut["usuario_id"])
                if usuario:
                    participantes.append({
                        "usuario": usuario.dict(),
                        "rol": ut["rol_en_tutoria"]
                    })
        
        tutoria = Tutoria(
            id=tutoria_dict["id"],
            tema=tutoria_dict["tema"],
            descripcion=tutoria_dict.get("descripcion"),
            fecha=tutoria_dict["fecha"],
            participantes=participantes
        )
        result.append(tutoria)
    
    return result

def obtener_tutoria(tutoria_id: int) -> Optional[Tutoria]:
    tutoria_dict = next((t for t in tutorias_db if t["id"] == tutoria_id), None)
    if not tutoria_dict:
        return None
    
    # Obtener participantes
    participantes = []
    for ut in usuario_tutorias_db:
        if ut["tutoria_id"] == tutoria_id:
            usuario = obtener_usuario(ut["usuario_id"])
            if usuario:
                participantes.append({
                    "usuario": usuario.dict(),
                    "rol": ut["rol_en_tutoria"]
                })
    
    return Tutoria(
        id=tutoria_dict["id"],
        tema=tutoria_dict["tema"],
        descripcion=tutoria_dict.get("descripcion"),
        fecha=tutoria_dict["fecha"],
        participantes=participantes
    )

def crear_tutoria(payload: TutoriaCreate) -> Tutoria:
    global next_tutoria_id
    
    tutoria_dict = {
        "id": next_tutoria_id,
        "tema": payload.tema,
        "descripcion": payload.descripcion,
        "fecha": payload.fecha
    }
    
    tutorias_db.append(tutoria_dict)
    next_tutoria_id += 1
    
    return obtener_tutoria(tutoria_dict["id"])

def actualizar_tutoria(tutoria_id: int, payload: TutoriaUpdate) -> Tutoria:
    tutoria_dict = next((t for t in tutorias_db if t["id"] == tutoria_id), None)
    if not tutoria_dict:
        raise KeyError("Tutoría no encontrada")
    
    # Actualizar campos no nulos
    if payload.tema is not None:
        tutoria_dict["tema"] = payload.tema
    if payload.descripcion is not None:
        tutoria_dict["descripcion"] = payload.descripcion
    if payload.fecha is not None:
        tutoria_dict["fecha"] = payload.fecha
    
    return obtener_tutoria(tutoria_id)

def eliminar_tutoria(tutoria_id: int) -> None:
    tutoria_dict = next((t for t in tutorias_db if t["id"] == tutoria_id), None)
    if not tutoria_dict:
        raise KeyError("Tutoría no encontrada")
    
    # Eliminar participaciones asociadas
    global usuario_tutorias_db
    usuario_tutorias_db = [ut for ut in usuario_tutorias_db if ut["tutoria_id"] != tutoria_id]
    
    # Eliminar tutoría
    tutorias_db.remove(tutoria_dict)

def agregar_usuario_tutoria(payload: UsuarioTutoriaCreate) -> Dict[str, str]:
    # Validar que el usuario existe
    if not obtener_usuario(payload.usuario_id):
        raise KeyError("Usuario no encontrado")
    
    # Validar que la tutoría existe
    if not obtener_tutoria(payload.tutoria_id):
        raise KeyError("Tutoría no encontrada")
    
    # Validar que no existe ya esta combinación
    exists = any(
        ut["usuario_id"] == payload.usuario_id and 
        ut["tutoria_id"] == payload.tutoria_id and 
        ut["rol_en_tutoria"] == payload.rol_en_tutoria.value
        for ut in usuario_tutorias_db
    )
    
    if exists:
        raise ValueError("El usuario ya está registrado en esta tutoría con este rol")
    
    usuario_tutoria_dict = {
        "usuario_id": payload.usuario_id,
        "tutoria_id": payload.tutoria_id,
        "rol_en_tutoria": payload.rol_en_tutoria.value
    }
    
    usuario_tutorias_db.append(usuario_tutoria_dict)
    
    return {"message": "Usuario agregado a la tutoría exitosamente"}

def remover_usuario_tutoria(usuario_id: int, tutoria_id: int, rol_en_tutoria: RolTutoria) -> Dict[str, str]:
    usuario_tutoria = next(
        (ut for ut in usuario_tutorias_db 
         if ut["usuario_id"] == usuario_id and 
            ut["tutoria_id"] == tutoria_id and 
            ut["rol_en_tutoria"] == rol_en_tutoria.value), 
        None
    )
    
    if not usuario_tutoria:
        raise KeyError("Participación en tutoría no encontrada")
    
    usuario_tutorias_db.remove(usuario_tutoria)
    
    return {"message": "Usuario removido de la tutoría exitosamente"}
