# Instrucciones para configurar la base de datos

## Paso 1: Configurar variables de entorno

Necesitas actualizar el archivo `.env` con la cadena de conexión real de tu base de datos Neon.

Basándose en la imagen que proporcionaste, la cadena de conexión tiene esta estructura:

```
postgresql://neondb_owner:[PASSWORD]@ep-frosty-math-a860wmo7-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require
```

## Paso 2: Reemplazar [PASSWORD]

En el archivo `.env`, reemplaza la parte de la contraseña con la contraseña real que aparece en tu interfaz de Neon.

## Paso 3: Ejecutar la inicialización

Una vez configurada la contraseña correcta, ejecuta:

```bash
python database.py
```

Esto creará todas las tablas necesarias en tu base de datos PostgreSQL.

## Paso 4: Ejecutar la aplicación

```bash
python -m uvicorn crud:app --reload
```

La API estará disponible en http://localhost:8000

## Estructura de tablas que se crearán:

1. **roles** - Roles del sistema (Administrador, Estudiante, Tutor)
2. **usuarios** - Información de usuarios con autenticación
3. **tareas** - Tareas personales de cada usuario
4. **cronograma** - Eventos programados por usuario  
5. **estado_animo** - Registros diarios de estado emocional
6. **tutorias** - Sesiones de tutoría programadas
7. **usuario_tutorias** - Relación N:M entre usuarios y tutorías

## Endpoints disponibles:

- **Usuarios**: CRUD completo para gestión de usuarios
- **Tareas**: Gestión de tareas con filtros por estado
- **Cronograma**: Eventos personales con fechas
- **Estado de ánimo**: Seguimiento emocional diario  
- **Tutorías**: Sistema de tutorías con participantes
- **Estadísticas**: Reportes y métricas del sistema
