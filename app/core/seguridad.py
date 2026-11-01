import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.repositories.rol_modulo_repo import RolModuloRepository
from app.repositories.usuario_repo import UsuarioRepository

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "cambia_esta_clave")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

ROL_ADMIN = 1
ROL_MODERADOR = 2
ROL_ANALISTA = 3
ROL_EMPLEADOR = 4
ROL_EMPLEADO = 5
ROLES_VALIDOS = (ROL_ADMIN, ROL_MODERADOR, ROL_ANALISTA, ROL_EMPLEADOR, ROL_EMPLEADO)
ROLES_REGISTRO = (ROL_EMPLEADOR, ROL_EMPLEADO)   # los que puede elegir alguien al registrarse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

usuario_repo = UsuarioRepository()
rol_modulo_repo = RolModuloRepository()

def encriptar_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, password_encriptada: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_encriptada.encode("utf-8"))
    except ValueError:
        return False


def crear_token(usuario: dict) -> str:
    """El token guarda el id, el rol y el correo (la API de pagos lee el rol y el correo)."""
    expira = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    datos = {"sub": str(usuario["id_usuario"]), "rol": usuario["id_rol"],
             "correo": usuario["correo"], "exp": expira}
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)


def crear_token_sistema() -> str:
    """Token corto con el que esta API se identifica ante la API de pagos (Express)."""
    expira = datetime.now(timezone.utc) + timedelta(minutes=5)
    datos = {"sub": "api_inwork", "rol": "sistema", "exp": expira}
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)


def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        datos = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = int(datos["sub"])
        id_rol = int(datos["rol"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token expiro, inicia sesion de nuevo")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")

    usuario = usuario_repo.obtener_por_id(id_usuario)
    if not usuario:
        raise HTTPException(status_code=401, detail="El usuario ya no existe")

    # Si el rol cambio (con el boton o porque el administrador lo cambio), el token viejo ya no sirve
    if id_rol != usuario["id_rol"]:
        raise HTTPException(status_code=401, detail="Tu rol cambio, inicia sesion de nuevo")
    return usuario


def es_admin(usuario: dict) -> bool:
    return usuario["id_rol"] == ROL_ADMIN


def es_staff(usuario: dict) -> bool:
    """Administrador o moderador: pueden modificar registros de otros usuarios."""
    return usuario["id_rol"] in (ROL_ADMIN, ROL_MODERADOR)


def ve_todo(usuario: dict) -> bool:
    """Administrador, moderador o analista: pueden VER la informacion de todos los usuarios."""
    return usuario["id_rol"] in (ROL_ADMIN, ROL_MODERADOR, ROL_ANALISTA)


def verificar_permiso(usuario: dict, modulo: str, accion: str):

    if es_admin(usuario):
        return
    permiso = rol_modulo_repo.obtener_permiso(usuario["id_rol"], modulo)
    if not permiso or not permiso["puede_" + accion]:
        raise HTTPException(status_code=403, detail=f"No tienes permiso para {accion} en {modulo}")


def verificar_dueno(usuario: dict, id_dueno: int, solo_lectura: bool = False):
    """Solo el dueno puede tocar su registro. El staff tambien; y si solo es para ver, el analista tambien."""
    if solo_lectura and ve_todo(usuario):
        return
    if usuario["id_usuario"] != id_dueno and not es_staff(usuario):
        raise HTTPException(status_code=403, detail="Este registro no te pertenece")


def solo_staff(usuario: dict):
    if not es_staff(usuario):
        raise HTTPException(status_code=403, detail="Solo un administrador o moderador puede hacer esto")
