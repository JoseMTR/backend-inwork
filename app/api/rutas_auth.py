from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core.seguridad import (
    ROLES_REGISTRO,
    crear_token,
    encriptar_password,
    obtener_usuario_actual,
    verificar_password,
)
from app.models.usuario import CambiarPassword, CambiarRol, Login, UsuarioRegistro
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.rol_modulo_repo import RolModuloRepository
from app.repositories.usuario_repo import UsuarioRepository

router = APIRouter(prefix="/auth", tags=["Autenticacion"])
repo = UsuarioRepository()
rol_modulo_repo = RolModuloRepository()
auditoria = AuditoriaRepository()


def respuesta_sesion(usuario: dict):
    """Lo que recibe el frontend al iniciar sesion o al cambiar de rol."""
    return {
        "access_token": crear_token(usuario),
        "token_type": "bearer",
        "id_usuario": usuario["id_usuario"],
        "nombre": f"{usuario['nombre']} {usuario['apellido']}",
        "id_rol": usuario["id_rol"],
        "rol": usuario["rol"],
    }


def hacer_login(correo: str, password: str):
    usuario = repo.obtener_por_correo(correo.lower())
    if not usuario or not verificar_password(password, usuario["password"]):
        raise HTTPException(status_code=401, detail="Correo o contrasena incorrectos")
    if not usuario["estado"]:
        raise HTTPException(status_code=403, detail="La cuenta esta desactivada")
    return respuesta_sesion(usuario)


@router.post("/registro")
def registro(usuario: UsuarioRegistro):
    if len(usuario.password) < 8:
        raise HTTPException(status_code=400, detail="La contrasena debe tener minimo 8 caracteres")
    if usuario.id_rol not in ROLES_REGISTRO:
        raise HTTPException(status_code=400, detail="Al registrarte solo puedes ser empleador (4) o empleado (5)")
    nuevo_id = repo.crear(usuario, encriptar_password(usuario.password), usuario.id_rol)
    return {"mensaje": "Usuario registrado exitosamente", "id": nuevo_id}


@router.post("/login")
def login(datos: Login):
    """Login con JSON: {"correo": "...", "password": "..."}"""
    return hacer_login(datos.correo, datos.password)


@router.post("/token")
def login_swagger(formulario: OAuth2PasswordRequestForm = Depends()):
    """Lo usa el boton Authorize de Swagger. En 'username' se escribe el correo."""
    return hacer_login(formulario.username, formulario.password)


@router.post("/cambiar-rol")
def cambiar_mi_rol(datos: CambiarRol, usuario: dict = Depends(obtener_usuario_actual)):
    """Boton "Cambiarme a empleador / empleado": {"id_rol": 4} o {"id_rol": 5}.
    Cambia el rol en la base de datos y devuelve un token nuevo con el rol nuevo."""
    if usuario["id_rol"] not in ROLES_REGISTRO or datos.id_rol not in ROLES_REGISTRO:
        raise HTTPException(status_code=403, detail="Solo puedes cambiar entre empleador (4) y empleado (5)")
    if datos.id_rol != usuario["id_rol"]:
        repo.cambiar_rol(usuario["id_usuario"], datos.id_rol)
        auditoria.registrar(usuario["id_usuario"], "usuarios", usuario["id_usuario"], "UPDATE")
    return respuesta_sesion(repo.obtener_por_id(usuario["id_usuario"]))


@router.get("/me")
def mi_perfil(usuario: dict = Depends(obtener_usuario_actual)):
    return usuario


@router.get("/mis-modulos")
def mis_modulos(usuario: dict = Depends(obtener_usuario_actual)):
    """Menu del usuario que inicio sesion: los modulos de su rol segun la tabla rol_modulo."""
    return rol_modulo_repo.obtener_modulos_por_rol(usuario["id_rol"])


@router.put("/cambiar-password")
def cambiar_password(datos: CambiarPassword, usuario: dict = Depends(obtener_usuario_actual)):
    completo = repo.obtener_por_correo(usuario["correo"])
    if not verificar_password(datos.password_actual, completo["password"]):
        raise HTTPException(status_code=400, detail="La contrasena actual no es correcta")
    if len(datos.password_nueva) < 8:
        raise HTTPException(status_code=400, detail="La contrasena debe tener minimo 8 caracteres")
    repo.cambiar_password(usuario["id_usuario"], encriptar_password(datos.password_nueva))
    return {"mensaje": "Contrasena actualizada correctamente"}
