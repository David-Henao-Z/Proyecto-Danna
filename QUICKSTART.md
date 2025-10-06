# 🚀 Inicio Rápido - API Aplicación de Estudio

## ⚡ Configuración Express (5 minutos)

### 1. Clonar y navegar al proyecto
```bash
git clone https://github.com/David-Henao-Z/Proyecto-Danna.git
cd Proyecto-Danna
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar base de datos
- Edita el archivo `.env` con tu cadena de conexión PostgreSQL
- Ejecuta: `python database.py`

### 4. Ejecutar la aplicación
```bash
python -m uvicorn crud:app --reload
```

### 5. ¡Listo! 🎉
- **API**: http://127.0.0.1:8000/
- **Documentación**: http://127.0.0.1:8000/docs

---

## 📋 Comandos Principales

| Acción | Comando |
|--------|---------|
| Ejecutar app | `python -m uvicorn crud:app --reload` |
| Ejecutar en puerto específico | `python -m uvicorn crud:app --reload --port 3000` |
| Inicializar DB | `python database.py` |
| Ver documentación | http://127.0.0.1:8000/docs |
| Ver esquema API | http://127.0.0.1:8000/openapi.json |
| Detener app | `Ctrl + C` |

## 🎯 Primeros Pasos

1. **Ver roles disponibles**: GET `/roles`
2. **Crear un usuario**: POST `/usuarios`
3. **Crear una tarea**: POST `/tareas`  
4. **Ver estadísticas**: GET `/estadisticas/generales`

## 🔗 Enlaces Útiles

- [Documentación completa](README.md)
- [Swagger UI](http://127.0.0.1:8000/docs) (después de ejecutar)
- [ReDoc](http://127.0.0.1:8000/redoc) (después de ejecutar)
