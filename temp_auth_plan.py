# Script para agregar autenticación a todos los endpoints restantes

# Lista de funciones que necesitan protección:
# 1. Cronograma: listar_cronograma, obtener_cronograma, crear_cronograma, actualizar_cronograma, eliminar_cronograma
# 2. Estado de ánimo: listar_estados_animo, obtener_estado_animo, crear_estado_animo, actualizar_estado_animo, eliminar_estado_animo  
# 3. Tutorías: listar_tutorias, obtener_tutoria, crear_tutoria, actualizar_tutoria, eliminar_tutoria
# 4. Usuario-Tutorías: listar_usuario_tutorias, crear_usuario_tutoria, eliminar_usuario_tutoria

# Cada función necesita:
# 1. Agregar `current_user = Depends(get_current_active_user)` a los parámetros
# 2. Agregar lógica de permisos según el tipo de operación:
#    - Listar: Solo administradores pueden ver todo, usuarios normales solo sus datos
#    - Obtener: Solo propietario o administrador
#    - Crear: Solo para sí mismo, excepto administradores
#    - Actualizar: Solo propietario o administrador  
#    - Eliminar: Solo propietario o administrador

print("Endpoints que necesitan protección identificados")