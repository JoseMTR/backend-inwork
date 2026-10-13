import psycopg2
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    rutas_adjuntos,
    rutas_auditoria,
    rutas_auth,
    rutas_calificaciones,
    rutas_categorias,
    rutas_chats,
    rutas_ciudades,
    rutas_contrataciones,
    rutas_dispositivos,
    rutas_habilidades,
    rutas_mensajes,
    rutas_modulos,
    rutas_notificaciones,
    rutas_ofertas,
    rutas_paises,
    rutas_reportes,
    rutas_rol_modulo,
    rutas_roles,
    rutas_tokens_usuario,
    rutas_trabajos,
    rutas_trabajos_habilidades,
    rutas_usuarios,
    rutas_usuarios_habilidades,
    rutas_verificaciones,
)

app = FastAPI(
    title="API InWork",
    description="Backend de InWork, FastAPI y PostgreSQL",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(psycopg2.Error)
def error_base_de_datos(request: Request, error: psycopg2.Error):
    mensaje = error.diag.message_primary if error.diag and error.diag.message_primary else str(error)
    return JSONResponse(status_code=400, content={"detail": f"Error en la base de datos: {mensaje}"})


app.include_router(rutas_auth.router)
app.include_router(rutas_roles.router)
app.include_router(rutas_modulos.router)
app.include_router(rutas_rol_modulo.router)
app.include_router(rutas_paises.router)
app.include_router(rutas_ciudades.router)
app.include_router(rutas_categorias.router)
app.include_router(rutas_habilidades.router)
app.include_router(rutas_usuarios.router)
app.include_router(rutas_usuarios_habilidades.router)
app.include_router(rutas_verificaciones.router)
app.include_router(rutas_trabajos.router)
app.include_router(rutas_trabajos_habilidades.router)
app.include_router(rutas_ofertas.router)
app.include_router(rutas_contrataciones.router)
app.include_router(rutas_calificaciones.router)
app.include_router(rutas_chats.router)
app.include_router(rutas_mensajes.router)
app.include_router(rutas_notificaciones.router)
app.include_router(rutas_dispositivos.router)
app.include_router(rutas_adjuntos.router)
app.include_router(rutas_reportes.router)
app.include_router(rutas_tokens_usuario.router)
app.include_router(rutas_auditoria.router)


@app.get("/")
def estado_api():
    return {"mensaje": "La API de InWork se encuentra en linea y funcional"}
