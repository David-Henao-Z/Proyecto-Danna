"""
Módulo de autenticación y seguridad
=====================================

Este módulo contiene todas las funciones relacionadas con:
- Encriptación y verificación de contraseñas
- Generación y validación de tokens JWT
- Autenticación de usuarios
- Middleware de seguridad
"""

from datetime import datetime, timedelta
from typing import Optional
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
import db_functions as db_svc

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-super-segura-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de encriptación de contraseñas (usar PBKDF2 para evitar problemas de compatibilidad)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# OAuth2 scheme - Define la URL del endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login-form")

# ========================
# MODELOS PYDANTIC
# ========================

class Token(BaseModel):
    """Modelo para la respuesta del token JWT"""
    access_token: str
    token_type: str
    user_info: dict

class TokenData(BaseModel):
    """Modelo para los datos del token JWT"""
    email: Optional[str] = None

class UserLogin(BaseModel):
    """Modelo para el login con email y contraseña"""
    email: str
    password: str

# ========================
# FUNCIONES DE CONTRASEÑAS
# ========================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar que la contraseña en texto plano coincida con el hash
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Contraseña hasheada
        
    Returns:
        bool: True si coinciden, False si no
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generar hash de la contraseña usando PBKDF2
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Hash de la contraseña
    """
    return pwd_context.hash(password)

# ========================
# FUNCIONES JWT
# ========================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Crear token JWT con datos del usuario
    
    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración del token
        
    Returns:
        str: Token JWT codificado
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ========================
# FUNCIONES DE AUTENTICACIÓN
# ========================

def authenticate_user(db: Session, email: str, password: str):
    """
    Autenticar usuario con email y contraseña
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        password: Contraseña en texto plano
        
    Returns:
        Usuario si la autenticación es exitosa, False si falla
    """
    user = db_svc.obtener_usuario_por_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Obtener usuario actual desde el token JWT
    
    Args:
        token: Token JWT del header Authorization
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db_svc.obtener_usuario_por_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Verificar que el usuario actual esté activo
    
    Args:
        current_user: Usuario actual obtenido del token
        
    Returns:
        Usuario activo
        
    Note:
        Aquí puedes agregar lógica adicional para verificar si el usuario está activo,
        suspendido, etc.
    """
    # Aquí puedes agregar lógica adicional para verificar si el usuario está activo
    # Por ejemplo: if not current_user.is_active: raise HTTPException(...)
    return current_user