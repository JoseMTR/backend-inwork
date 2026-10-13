from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.seguridad import (
    crear_token,
    encriptar_password,
    obtener_usuario_actual,
    verificar_password,
)
from app.models.usuario import CambiarPassword, Login, UsuarioRegistro
from app.repositories.usuario_repo import UsuarioRepository

router = APIRouter(prefix="/auth", tags=["Autenticacion"])
repo = UsuarioRepository()


def hacer_login(correo: str, password: str):
    usuario = repo.obtener_por_correo(correo.lower())
    if not usuario or not verificar_password(password, usuario["password"]):
        raise HTTPException(status_code=401, detail="Correo o contrasena incorrectos")
    if not usuario["estado"]:
        raise HTTPException(status_code=403, detail="La cuenta esta desactivada")
    return {
        "access_token": crear_token(usuario),
        "token_type": "bearer",
        "id_usuario": usuario["id_usuario"],
        "id_rol": usuario["id_rol"],
    }


@router.post("/registro")
def registro(usuario: UsuarioRegistro):
    if len(usuario.password) < 8:
        raise HTTPException(status_code=400, detail="La contrasena debe tener minimo 8 caracteres")
    nuevo_id = repo.crear(usuario, encriptar_password(usuario.password))
    return {"mensaje": "Usuario registrado exitosamente", "id": nuevo_id}


@router.post("/login")
def login(datos: Login):
    """Login con JSON: {"correo": "...", "password": "..."}"""
    return hacer_login(datos.correo, datos.password)


@router.post("/token")
def login_swagger(formulario: OAuth2PasswordRequestForm = Depends()):
    """Lo usa el boton Authorize de Swagger. En 'username' se escribe el correo."""
    return hacer_login(formulario.username, formulario.password)


@router.get("/me")
def mi_perfil(usuario: dict = Depends(obtener_usuario_actual)):
    return usuario


@router.put("/cambiar-password")
def cambiar_password(datos: CambiarPassword, usuario: dict = Depends(obtener_usuario_actual)):
    completo = repo.obtener_por_correo(usuario["correo"])
    if not verificar_password(datos.password_actual, completo["password"]):
        raise HTTPException(status_code=400, detail="La contrasena actual no es correcta")
    if len(datos.password_nueva) < 8:
        raise HTTPException(status_code=400, detail="La contrasena debe tener minimo 8 caracteres")
    repo.cambiar_password(usuario["id_usuario"], encriptar_password(datos.password_nueva))
    return {"mensaje": "Contrasena actualizada correctamente"}
