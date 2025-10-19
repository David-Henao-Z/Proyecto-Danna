"""
Script temporal para actualizar contraseñas en texto plano a hash bcrypt
"""

import os
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from auth import get_password_hash

# Cargar variables de entorno
load_dotenv()

def update_plain_passwords():
    """Actualizar contraseñas que están en texto plano"""
    
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Buscar usuarios con contraseñas que NO empiecen con $2b$ (no son bcrypt)
            result = conn.execute(
                text("SELECT id, email, password FROM usuarios WHERE password NOT LIKE '$2b$%'")
            )
            
            users_to_update = result.fetchall()
            
            if not users_to_update:
                print("✅ Todas las contraseñas ya están hasheadas correctamente")
                return
            
            print(f"🔄 Encontrados {len(users_to_update)} usuarios con contraseñas en texto plano")
            
            for user in users_to_update:
                user_id, email, plain_password = user
                
                print(f"📝 Actualizando usuario: {email}")
                
                # Hash de la contraseña
                try:
                    hashed_password = get_password_hash(plain_password)
                    
                    # Actualizar en la base de datos
                    conn.execute(
                        text("UPDATE usuarios SET password = :password WHERE id = :user_id"),
                        {"password": hashed_password, "user_id": user_id}
                    )
                    
                    print(f"✅ Usuario {email} actualizado correctamente")
                    
                except Exception as e:
                    print(f"❌ Error actualizando {email}: {e}")
            
            # Confirmar cambios
            conn.commit()
            print(f"🎉 Actualizacion completada para {len(users_to_update)} usuarios")
            
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")

if __name__ == "__main__":
    update_plain_passwords()