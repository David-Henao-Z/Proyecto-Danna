# database.py
# ============================================================================
# Configuración de la base de datos PostgreSQL y modelos SQLAlchemy
# ============================================================================

from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime, date

# Configuración de la base de datos
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:your_password@ep-frosty-math-a860wmo7-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require")

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# ============================================================================
# MODELOS SQLALCHEMY
# ============================================================================

class Rol(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)
    
    # Relación con usuarios
    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(Text, nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"))
    
    # Relaciones
    rol = relationship("Rol", back_populates="usuarios")
    tareas = relationship("Tarea", back_populates="usuario", cascade="all, delete-orphan")
    cronograma = relationship("Cronograma", back_populates="usuario", cascade="all, delete-orphan")
    estados_animo = relationship("EstadoAnimo", back_populates="usuario", cascade="all, delete-orphan")
    participaciones_tutorias = relationship("UsuarioTutoria", back_populates="usuario", cascade="all, delete-orphan")


class Tarea(Base):
    __tablename__ = "tareas"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha_entrega = Column(Date)
    estado = Column(String(20), nullable=False, default='pendiente')
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    
    # Constraint para validar estados
    __table_args__ = (
        CheckConstraint("estado IN ('pendiente', 'en_progreso', 'completada')", name='check_estado_tarea'),
    )
    
    # Relación
    usuario = relationship("Usuario", back_populates="tareas")


class Cronograma(Base):
    __tablename__ = "cronograma"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    
    # Relación
    usuario = relationship("Usuario", back_populates="cronograma")


class EstadoAnimo(Base):
    __tablename__ = "estado_animo"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    fecha = Column(Date, nullable=False, default=date.today)
    estado = Column(String(50), nullable=False)
    comentario = Column(Text)
    
    # Relación
    usuario = relationship("Usuario", back_populates="estados_animo")


class Tutoria(Base):
    __tablename__ = "tutorias"
    
    id = Column(Integer, primary_key=True, index=True)
    tema = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha = Column(DateTime, nullable=False)
    
    # Relación
    participantes = relationship("UsuarioTutoria", back_populates="tutoria", cascade="all, delete-orphan")


class UsuarioTutoria(Base):
    __tablename__ = "usuario_tutorias"
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    tutoria_id = Column(Integer, ForeignKey("tutorias.id", ondelete="CASCADE"), primary_key=True)
    rol_en_tutoria = Column(String(20), nullable=False, primary_key=True)
    
    # Constraint para validar roles en tutoría
    __table_args__ = (
        CheckConstraint("rol_en_tutoria IN ('tutor', 'estudiante')", name='check_rol_tutoria'),
    )
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="participaciones_tutorias")
    tutoria = relationship("Tutoria", back_populates="participantes")


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_db():
    """
    Generador que proporciona una sesión de base de datos.
    Asegura que la sesión se cierre correctamente.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas
    e insertando roles por defecto si no existen.
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Insertar roles por defecto
    db = SessionLocal()
    try:
        # Verificar si ya existen roles
        existing_roles = db.query(Rol).count()
        
        if existing_roles == 0:
            roles_default = [
                Rol(nombre="Administrador", descripcion="Acceso completo al sistema"),
                Rol(nombre="Estudiante", descripcion="Usuario estudiante básico"),
                Rol(nombre="Tutor", descripcion="Usuario que puede dar tutorías"),
            ]
            
            for rol in roles_default:
                db.add(rol)
            
            db.commit()
            print("Roles por defecto creados exitosamente")
        else:
            print("Los roles ya existen en la base de datos")
            
    except Exception as e:
        db.rollback()
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Inicializando base de datos...")
    init_db()
    print("Base de datos inicializada correctamente")
