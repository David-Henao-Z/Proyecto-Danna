# update_remaining_endpoints.py
# Script para completar la actualización de los endpoints restantes

# Este archivo contiene el resto de los endpoints actualizados para usar la base de datos

# ESTADO DE ÁNIMO
estados_animo_endpoints = '''
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
'''

print("Los endpoints restantes han sido definidos. Ahora necesitas copiar este código al archivo crud.py")
