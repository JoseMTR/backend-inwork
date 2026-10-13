
CREATE OR REPLACE FUNCTION fn_set_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TABLE roles (
    id_rol SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE modulos (
    id_modulo SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE rol_modulo (
    id_rol_modulo SERIAL PRIMARY KEY,

    id_rol INTEGER NOT NULL,
    id_modulo INTEGER NOT NULL,

    -- Permisos por accion
    puede_crear BOOLEAN NOT NULL DEFAULT FALSE,
    puede_leer BOOLEAN NOT NULL DEFAULT TRUE,
    puede_editar BOOLEAN NOT NULL DEFAULT FALSE,
    puede_eliminar BOOLEAN NOT NULL DEFAULT FALSE,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_rol_modulo_rol
        FOREIGN KEY (id_rol) REFERENCES roles(id_rol) ON DELETE CASCADE,

    CONSTRAINT fk_rol_modulo_modulo
        FOREIGN KEY (id_modulo) REFERENCES modulos(id_modulo) ON DELETE CASCADE,

    CONSTRAINT uq_rol_modulo UNIQUE (id_rol, id_modulo)
);


CREATE TABLE pais (
    id_pais SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE ciudades (
    id_ciudad SERIAL PRIMARY KEY,
    id_pais INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_ciudad_pais
        FOREIGN KEY (id_pais) REFERENCES pais(id_pais) ON DELETE RESTRICT,

    CONSTRAINT uq_ciudad_pais_nombre UNIQUE (id_pais, nombre)
);


CREATE TABLE categorias (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE habilidades (
    id_habilidad SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE
);


CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    id_rol INTEGER NOT NULL DEFAULT 3, 
    id_ciudad INTEGER,

    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,    
    foto_perfil TEXT,
    correo VARCHAR(150) NOT NULL,
    correo_verificado BOOLEAN NOT NULL DEFAULT FALSE,
    telefono VARCHAR(20) NOT NULL,

    tipo_identificacion VARCHAR(30) NOT NULL,
    numero_identificacion VARCHAR(20) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    descripcion TEXT,
    direccion VARCHAR(255),

    promedio_calificacion NUMERIC(3,2) NOT NULL DEFAULT 0,
    total_calificaciones INTEGER NOT NULL DEFAULT 0,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_usuario_rol
        FOREIGN KEY (id_rol) REFERENCES roles(id_rol) ON DELETE RESTRICT,

    CONSTRAINT fk_usuario_ciudad
        FOREIGN KEY (id_ciudad) REFERENCES ciudades(id_ciudad) ON DELETE SET NULL,

    CONSTRAINT uq_usuario_correo UNIQUE (correo),
    CONSTRAINT uq_usuario_telefono UNIQUE (telefono),
    CONSTRAINT uq_usuario_identificacion UNIQUE (tipo_identificacion, numero_identificacion),

    CONSTRAINT chk_usuario_correo
        CHECK (correo ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),

    CONSTRAINT chk_usuario_tipo_identificacion
        CHECK (tipo_identificacion IN
            ('cedula','pasaporte','permiso de residencia','cedula de extranjeria'))
);

CREATE TABLE usuarios_habilidades (
    id_usuario_habilidad SERIAL PRIMARY KEY,

    id_usuario INTEGER NOT NULL,
    id_habilidad INTEGER NOT NULL,
    anios_experiencia INTEGER NOT NULL CHECK (anios_experiencia >= 0),

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_uh_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,

    CONSTRAINT fk_uh_habilidad
        FOREIGN KEY (id_habilidad) REFERENCES habilidades(id_habilidad) ON DELETE RESTRICT,

    CONSTRAINT uq_usuario_habilidad UNIQUE (id_usuario, id_habilidad)
);


CREATE TABLE trabajos (
    id_trabajo SERIAL PRIMARY KEY,

    id_cliente INTEGER NOT NULL,
    id_categoria INTEGER NOT NULL,
    id_ciudad INTEGER NOT NULL,      

    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT NOT NULL,
    direccion VARCHAR(255),
    latitud DECIMAL(9,6) NOT NULL,
    longitud DECIMAL(9,6) NOT NULL,

    fecha_trabajo DATE NOT NULL,       
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,

    presupuesto NUMERIC(12,2) NOT NULL CHECK (presupuesto > 0),
    moneda CHAR(3) NOT NULL DEFAULT 'COP',

    estado_trabajo VARCHAR(20) NOT NULL DEFAULT 'publicado',

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_trabajo_cliente
        FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,

    CONSTRAINT fk_trabajo_categoria
        FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE RESTRICT,

    CONSTRAINT fk_trabajo_ciudad
        FOREIGN KEY (id_ciudad) REFERENCES ciudades(id_ciudad) ON DELETE RESTRICT,

    CONSTRAINT chk_trabajo_estado
        CHECK (estado_trabajo IN ('publicado','asignado','finalizado','cancelado')),

    CONSTRAINT chk_hora_trabajo CHECK (hora_fin > hora_inicio),
    CONSTRAINT chk_latitud CHECK (latitud BETWEEN -90 AND 90),
    CONSTRAINT chk_longitud CHECK (longitud BETWEEN -180 AND 180)
);

CREATE TABLE trabajos_habilidades (
    id_trabajo_habilidad SERIAL PRIMARY KEY,

    id_trabajo INTEGER NOT NULL,
    id_habilidad INTEGER NOT NULL,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_th_trabajo
        FOREIGN KEY (id_trabajo) REFERENCES trabajos(id_trabajo) ON DELETE CASCADE,

    CONSTRAINT fk_th_habilidad
        FOREIGN KEY (id_habilidad) REFERENCES habilidades(id_habilidad) ON DELETE RESTRICT,

    CONSTRAINT uq_trabajo_habilidad UNIQUE (id_trabajo, id_habilidad)
);


CREATE TABLE ofertas (
    id_oferta SERIAL PRIMARY KEY,

    id_trabajo INTEGER NOT NULL,
    id_trabajador INTEGER NOT NULL,

    valor_oferta NUMERIC(12,2) NOT NULL CHECK (valor_oferta > 0),
    moneda CHAR(3) NOT NULL DEFAULT 'COP',
    mensaje TEXT,
    fecha_oferta TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    estado_oferta VARCHAR(20) NOT NULL DEFAULT 'pendiente',

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_oferta_trabajo
        FOREIGN KEY (id_trabajo) REFERENCES trabajos(id_trabajo) ON DELETE RESTRICT,

    CONSTRAINT fk_oferta_trabajador
        FOREIGN KEY (id_trabajador) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,

    CONSTRAINT chk_oferta_estado
        CHECK (estado_oferta IN ('pendiente','aceptada','rechazada','retirada')),

    CONSTRAINT uq_oferta_trabajo_trabajador UNIQUE (id_trabajo, id_trabajador)
);

CREATE TABLE contrataciones (
    id_contratacion SERIAL PRIMARY KEY,

    id_trabajo INTEGER NOT NULL,
    id_cliente INTEGER NOT NULL,
    id_trabajador INTEGER NOT NULL,
    id_oferta INTEGER NOT NULL,

    fecha_contratacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado_contratacion VARCHAR(20) NOT NULL DEFAULT 'activa',

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_contratacion_trabajo
        FOREIGN KEY (id_trabajo) REFERENCES trabajos(id_trabajo) ON DELETE RESTRICT,

    CONSTRAINT fk_contratacion_cliente
        FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,

    CONSTRAINT fk_contratacion_trabajador
        FOREIGN KEY (id_trabajador) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,

    CONSTRAINT fk_contratacion_oferta
        FOREIGN KEY (id_oferta) REFERENCES ofertas(id_oferta) ON DELETE RESTRICT,

    CONSTRAINT chk_contratacion_estado
        CHECK (estado_contratacion IN ('activa','finalizada','cancelada')),

    CONSTRAINT chk_contratacion_usuarios CHECK (id_cliente <> id_trabajador),
    CONSTRAINT uq_contratacion_oferta UNIQUE (id_oferta)
);

CREATE UNIQUE INDEX uq_contratacion_activa
    ON contrataciones (id_trabajo)
    WHERE estado_contratacion = 'activa';


CREATE TABLE calificacion (
    id_calificacion SERIAL PRIMARY KEY,

    id_calificador INTEGER NOT NULL,
    id_calificado INTEGER NOT NULL,
    id_trabajo INTEGER NOT NULL,

    puntuacion INTEGER NOT NULL,
    comentario TEXT,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_calificacion_calificador
        FOREIGN KEY (id_calificador) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,

    CONSTRAINT fk_calificacion_calificado
        FOREIGN KEY (id_calificado) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,

    CONSTRAINT fk_calificacion_trabajo
        FOREIGN KEY (id_trabajo) REFERENCES trabajos(id_trabajo) ON DELETE RESTRICT,

    CONSTRAINT chk_calificacion_puntuacion CHECK (puntuacion BETWEEN 1 AND 5),
    CONSTRAINT chk_calificacion_usuarios CHECK (id_calificador <> id_calificado),
    CONSTRAINT uq_calificacion UNIQUE (id_calificador, id_trabajo)
);


CREATE TABLE chat (
    id_chat SERIAL PRIMARY KEY,

    id_trabajo INTEGER NOT NULL,
    id_cliente INTEGER NOT NULL,
    id_trabajador INTEGER NOT NULL,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_chat_trabajo
        FOREIGN KEY (id_trabajo) REFERENCES trabajos(id_trabajo) ON DELETE RESTRICT,

    CONSTRAINT fk_chat_cliente
        FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,

    CONSTRAINT fk_chat_trabajador
        FOREIGN KEY (id_trabajador) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,

    CONSTRAINT chk_chat_usuarios CHECK (id_cliente <> id_trabajador),

    -- Un chat por (trabajo, trabajador): permite negociar con varios trabajadores
    CONSTRAINT uq_chat_trabajo_trabajador UNIQUE (id_trabajo, id_trabajador)
);

CREATE TABLE mensajes (
    id_mensaje SERIAL PRIMARY KEY,

    id_chat INTEGER NOT NULL,
    id_remitente INTEGER NOT NULL,

    mensaje TEXT NOT NULL,
    leido BOOLEAN NOT NULL DEFAULT FALSE,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_mensaje_chat
        FOREIGN KEY (id_chat) REFERENCES chat(id_chat) ON DELETE CASCADE,

    CONSTRAINT fk_mensaje_usuario
        FOREIGN KEY (id_remitente) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
);


CREATE TABLE reportes (
    id_reporte SERIAL PRIMARY KEY,

    id_reportante INTEGER NOT NULL,
    id_reportado INTEGER NOT NULL,
    id_trabajo INTEGER NOT NULL,

    motivo VARCHAR(50) NOT NULL,
    descripcion TEXT NOT NULL,

    estado_reporte VARCHAR(20) NOT NULL DEFAULT 'pendiente',

    -- Gestion por parte del administrador
    id_admin_revisor INTEGER,
    resolucion TEXT,
    fecha_resolucion TIMESTAMPTZ,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_reporte_reportante
        FOREIGN KEY (id_reportante) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,

    CONSTRAINT fk_reporte_reportado
        FOREIGN KEY (id_reportado) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,

    CONSTRAINT fk_reporte_trabajo
        FOREIGN KEY (id_trabajo) REFERENCES trabajos(id_trabajo) ON DELETE RESTRICT,

    CONSTRAINT fk_reporte_admin
        FOREIGN KEY (id_admin_revisor) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,

    CONSTRAINT chk_reporte_motivo
        CHECK (motivo IN ('fraude','incumplimiento','lenguaje_inapropiado',
                          'estafa','suplantacion','otro')),

    CONSTRAINT chk_reporte_estado
        CHECK (estado_reporte IN ('pendiente','en_revision','resuelto','rechazado')),

    CONSTRAINT chk_reporte_usuario CHECK (id_reportante <> id_reportado),

    CONSTRAINT uq_reporte UNIQUE (id_reportante, id_reportado, id_trabajo)
);


CREATE TABLE notificaciones (
    id_notificacion SERIAL PRIMARY KEY,

    id_usuario INTEGER NOT NULL,
    tipo VARCHAR(50) NOT NULL,           
    titulo VARCHAR(150) NOT NULL,
    contenido TEXT,
    id_referencia INTEGER,                
    leida BOOLEAN NOT NULL DEFAULT FALSE,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_notificacion_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE dispositivos (
    id_dispositivo SERIAL PRIMARY KEY,

    id_usuario INTEGER NOT NULL,
    token_push VARCHAR(500) NOT NULL UNIQUE,
    plataforma VARCHAR(20) NOT NULL,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_dispositivo_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,

    CONSTRAINT chk_dispositivo_plataforma
        CHECK (plataforma IN ('android','ios','web'))
);



CREATE TABLE tokens_usuario (
    id_token SERIAL PRIMARY KEY,

    id_usuario INTEGER NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,     
    expira TIMESTAMPTZ NOT NULL,
    usado BOOLEAN NOT NULL DEFAULT FALSE,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_token_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,

    CONSTRAINT chk_token_tipo
        CHECK (tipo IN ('verificacion_correo','recuperar_password','refresh'))
);



CREATE TABLE adjuntos (
    id_adjunto SERIAL PRIMARY KEY,

    tipo_entidad VARCHAR(20) NOT NULL,
    id_entidad INTEGER NOT NULL,         
    id_subido_por INTEGER NOT NULL,

    url TEXT NOT NULL,
    tipo_mime VARCHAR(100),

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_adjunto_usuario
        FOREIGN KEY (id_subido_por) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,

    CONSTRAINT chk_adjunto_entidad
        CHECK (tipo_entidad IN ('trabajo','mensaje','reporte'))
);


CREATE TABLE verificacion_identidad (
    id_verificacion SERIAL PRIMARY KEY,

    id_usuario INTEGER NOT NULL,
    url_documento_frente TEXT NOT NULL,
    url_documento_reverso TEXT,
    url_selfie TEXT NOT NULL,

    estado_verificacion VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    id_admin_revisor INTEGER,
    observacion TEXT,
    fecha_revision TIMESTAMPTZ,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_verif_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,

    CONSTRAINT fk_verif_admin
        FOREIGN KEY (id_admin_revisor) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,

    CONSTRAINT chk_verif_estado
        CHECK (estado_verificacion IN ('pendiente','aprobada','rechazada'))
);



CREATE TABLE auditoria (
    id_auditoria BIGSERIAL PRIMARY KEY,

    id_usuario INTEGER,
    tabla VARCHAR(63) NOT NULL,
    id_registro INTEGER,
    accion VARCHAR(10) NOT NULL,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    ip VARCHAR(45),

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_auditoria_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,

    CONSTRAINT chk_auditoria_accion CHECK (accion IN ('INSERT','UPDATE','DELETE'))
);



CREATE INDEX idx_ciudades_pais            ON ciudades(id_pais);
CREATE INDEX idx_usuarios_rol             ON usuarios(id_rol);
CREATE INDEX idx_usuarios_ciudad          ON usuarios(id_ciudad);
CREATE INDEX idx_uh_habilidad             ON usuarios_habilidades(id_habilidad);

CREATE INDEX idx_trabajos_cliente         ON trabajos(id_cliente);
CREATE INDEX idx_trabajos_cat_ciudad      ON trabajos(id_categoria, id_ciudad);
CREATE INDEX idx_trabajos_estado_fecha    ON trabajos(estado_trabajo, fecha_trabajo);
CREATE INDEX idx_trabajos_coordenadas     ON trabajos(latitud, longitud);
CREATE INDEX idx_th_habilidad             ON trabajos_habilidades(id_habilidad);

CREATE INDEX idx_ofertas_trabajador       ON ofertas(id_trabajador);
CREATE INDEX idx_ofertas_trabajo_estado   ON ofertas(id_trabajo, estado_oferta);

CREATE INDEX idx_contrataciones_cliente   ON contrataciones(id_cliente);
CREATE INDEX idx_contrataciones_trabajador ON contrataciones(id_trabajador);
CREATE INDEX idx_contrataciones_trabajo   ON contrataciones(id_trabajo);

CREATE INDEX idx_calificacion_calificado  ON calificacion(id_calificado);
CREATE INDEX idx_calificacion_trabajo     ON calificacion(id_trabajo);

CREATE INDEX idx_chat_cliente             ON chat(id_cliente);
CREATE INDEX idx_chat_trabajador          ON chat(id_trabajador);
CREATE INDEX idx_mensajes_chat_created    ON mensajes(id_chat, created);
CREATE INDEX idx_mensajes_remitente       ON mensajes(id_remitente);

CREATE INDEX idx_reportes_reportado       ON reportes(id_reportado);
CREATE INDEX idx_reportes_trabajo         ON reportes(id_trabajo);
CREATE INDEX idx_reportes_estado          ON reportes(estado_reporte);


CREATE INDEX idx_notif_usuario_leida      ON notificaciones(id_usuario, leida);
CREATE INDEX idx_dispositivos_usuario     ON dispositivos(id_usuario);
CREATE INDEX idx_tokens_usuario           ON tokens_usuario(id_usuario, tipo);
CREATE INDEX idx_adjuntos_entidad         ON adjuntos(tipo_entidad, id_entidad);
CREATE INDEX idx_verif_usuario            ON verificacion_identidad(id_usuario);
CREATE INDEX idx_auditoria_tabla_registro ON auditoria(tabla, id_registro);



DO $$
DECLARE
    t RECORD;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND column_name = 'updated'
    LOOP
        EXECUTE format(
            'CREATE TRIGGER trg_%I_updated
             BEFORE UPDATE ON %I
             FOR EACH ROW EXECUTE FUNCTION fn_set_updated()',
            t.table_name, t.table_name);
    END LOOP;
END $$;




CREATE OR REPLACE FUNCTION fn_validar_mayoria_edad()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.fecha_nacimiento > (CURRENT_DATE - INTERVAL '18 years') THEN
        RAISE EXCEPTION 'El usuario debe ser mayor de 18 anios';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_usuarios_mayoria_edad
BEFORE INSERT ON usuarios
FOR EACH ROW EXECUTE FUNCTION fn_validar_mayoria_edad();


CREATE OR REPLACE FUNCTION fn_validar_fecha_trabajo()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.fecha_trabajo < CURRENT_DATE THEN
        RAISE EXCEPTION 'La fecha del trabajo no puede ser anterior a hoy';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_trabajos_fecha
BEFORE INSERT ON trabajos
FOR EACH ROW EXECUTE FUNCTION fn_validar_fecha_trabajo();


CREATE OR REPLACE FUNCTION fn_validar_oferta()
RETURNS TRIGGER AS $$
DECLARE
    v_cliente INTEGER;
BEGIN
    SELECT id_cliente INTO v_cliente FROM trabajos WHERE id_trabajo = NEW.id_trabajo;
    IF v_cliente = NEW.id_trabajador THEN
        RAISE EXCEPTION 'No puedes ofertar en tu propio trabajo';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ofertas_validar
BEFORE INSERT ON ofertas
FOR EACH ROW EXECUTE FUNCTION fn_validar_oferta();


CREATE OR REPLACE FUNCTION fn_validar_contratacion()
RETURNS TRIGGER AS $$
DECLARE
    v_of_trabajo INTEGER;
    v_of_trabajador INTEGER;
    v_tr_cliente INTEGER;
BEGIN
    SELECT id_trabajo, id_trabajador
      INTO v_of_trabajo, v_of_trabajador
      FROM ofertas WHERE id_oferta = NEW.id_oferta;

    SELECT id_cliente INTO v_tr_cliente
      FROM trabajos WHERE id_trabajo = NEW.id_trabajo;

    IF v_of_trabajo IS DISTINCT FROM NEW.id_trabajo THEN
        RAISE EXCEPTION 'La oferta no pertenece a ese trabajo';
    END IF;
    IF v_of_trabajador IS DISTINCT FROM NEW.id_trabajador THEN
        RAISE EXCEPTION 'El trabajador no coincide con el de la oferta';
    END IF;
    IF v_tr_cliente IS DISTINCT FROM NEW.id_cliente THEN
        RAISE EXCEPTION 'El cliente no coincide con el dueno del trabajo';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_contrataciones_validar
BEFORE INSERT ON contrataciones
FOR EACH ROW EXECUTE FUNCTION fn_validar_contratacion();


CREATE OR REPLACE FUNCTION fn_validar_chat()
RETURNS TRIGGER AS $$
DECLARE
    v_cliente INTEGER;
BEGIN
    SELECT id_cliente INTO v_cliente FROM trabajos WHERE id_trabajo = NEW.id_trabajo;
    IF v_cliente IS DISTINCT FROM NEW.id_cliente THEN
        RAISE EXCEPTION 'El cliente del chat no es el dueno del trabajo';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_chat_validar
BEFORE INSERT ON chat
FOR EACH ROW EXECUTE FUNCTION fn_validar_chat();


CREATE OR REPLACE FUNCTION fn_validar_mensaje()
RETURNS TRIGGER AS $$
DECLARE
    v_cliente INTEGER;
    v_trabajador INTEGER;
BEGIN
    SELECT id_cliente, id_trabajador INTO v_cliente, v_trabajador
      FROM chat WHERE id_chat = NEW.id_chat;

    IF NEW.id_remitente NOT IN (v_cliente, v_trabajador) THEN
        RAISE EXCEPTION 'El remitente no pertenece a este chat';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_mensajes_validar
BEFORE INSERT ON mensajes
FOR EACH ROW EXECUTE FUNCTION fn_validar_mensaje();


CREATE OR REPLACE FUNCTION fn_validar_calificacion()
RETURNS TRIGGER AS $$
DECLARE
    v_cliente INTEGER;
    v_trabajador INTEGER;
BEGIN
    SELECT id_cliente, id_trabajador
      INTO v_cliente, v_trabajador
      FROM contrataciones
     WHERE id_trabajo = NEW.id_trabajo
       AND estado_contratacion = 'finalizada'
     LIMIT 1;

    IF v_cliente IS NULL THEN
        RAISE EXCEPTION 'Solo se puede calificar un trabajo con contratacion finalizada';
    END IF;

    IF NOT (
        (NEW.id_calificador = v_cliente AND NEW.id_calificado = v_trabajador) OR
        (NEW.id_calificador = v_trabajador AND NEW.id_calificado = v_cliente)
    ) THEN
        RAISE EXCEPTION 'Calificador y calificado deben ser cliente y trabajador del trabajo';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calificacion_validar
BEFORE INSERT ON calificacion
FOR EACH ROW EXECUTE FUNCTION fn_validar_calificacion();


CREATE OR REPLACE FUNCTION fn_actualizar_reputacion()
RETURNS TRIGGER AS $$
DECLARE
    v_usuario INTEGER;
BEGIN
    v_usuario := COALESCE(NEW.id_calificado, OLD.id_calificado);

    UPDATE usuarios u
       SET promedio_calificacion = COALESCE((
               SELECT ROUND(AVG(c.puntuacion)::numeric, 2)
                 FROM calificacion c
                WHERE c.id_calificado = v_usuario AND c.estado = TRUE), 0),
           total_calificaciones = (
               SELECT COUNT(*)
                 FROM calificacion c
                WHERE c.id_calificado = v_usuario AND c.estado = TRUE)
     WHERE u.id_usuario = v_usuario;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calificacion_reputacion
AFTER INSERT OR UPDATE OR DELETE ON calificacion
FOR EACH ROW EXECUTE FUNCTION fn_actualizar_reputacion();


CREATE OR REPLACE FUNCTION fn_validar_reporte()
RETURNS TRIGGER AS $$
DECLARE
    v_cliente INTEGER;
    v_ok_reportante BOOLEAN;
    v_ok_reportado BOOLEAN;
BEGIN
    SELECT id_cliente INTO v_cliente FROM trabajos WHERE id_trabajo = NEW.id_trabajo;

    v_ok_reportante := (NEW.id_reportante = v_cliente) OR EXISTS (
        SELECT 1 FROM ofertas
         WHERE id_trabajo = NEW.id_trabajo AND id_trabajador = NEW.id_reportante);

    v_ok_reportado := (NEW.id_reportado = v_cliente) OR EXISTS (
        SELECT 1 FROM ofertas
         WHERE id_trabajo = NEW.id_trabajo AND id_trabajador = NEW.id_reportado);

    IF NOT (v_ok_reportante AND v_ok_reportado) THEN
        RAISE EXCEPTION 'Ambos usuarios deben estar relacionados con el trabajo reportado';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_reportes_validar
BEFORE INSERT ON reportes
FOR EACH ROW EXECUTE FUNCTION fn_validar_reporte();


INSERT INTO roles (id_rol, nombre, descripcion) VALUES
    (1, 'Administrador', 'Acceso total a la plataforma'),
    (2, 'Moderador',     'Revisa reportes y verificaciones'),
    (3, 'Usuario',       'Puede publicar trabajos y ofertar en ellos')
ON CONFLICT DO NOTHING;

SELECT setval(pg_get_serial_sequence('roles','id_rol'),
              (SELECT MAX(id_rol) FROM roles));


INSERT INTO modulos (nombre, descripcion) VALUES
    ('roles',          'Roles, modulos y permisos'),
    ('ubicacion',      'Paises y ciudades'),
    ('categorias',     'Categorias y habilidades'),
    ('usuarios',       'Usuarios y sus habilidades'),
    ('verificaciones', 'Verificacion de identidad'),
    ('trabajos',       'Trabajos y habilidades requeridas'),
    ('ofertas',        'Ofertas de trabajadores'),
    ('contrataciones', 'Contrataciones'),
    ('calificaciones', 'Calificaciones entre usuarios'),
    ('chat',           'Chats y mensajes'),
    ('notificaciones', 'Notificaciones y dispositivos'),
    ('adjuntos',       'Archivos adjuntos'),
    ('reportes',       'Reportes de usuarios'),
    ('seguridad',      'Tokens de usuario'),
    ('auditoria',      'Registro de auditoria')
ON CONFLICT DO NOTHING;

INSERT INTO rol_modulo (id_rol, id_modulo, puede_crear, puede_leer, puede_editar, puede_eliminar)
SELECT 1, id_modulo, TRUE, TRUE, TRUE, TRUE FROM modulos
ON CONFLICT DO NOTHING;

INSERT INTO rol_modulo (id_rol, id_modulo, puede_crear, puede_leer, puede_editar, puede_eliminar)
SELECT 2, m.id_modulo, p.crear, p.leer, p.editar, p.eliminar
FROM modulos m
JOIN (VALUES
    -- modulo            crear  leer  editar eliminar
    ('ubicacion',        FALSE, TRUE, FALSE, FALSE),
    ('categorias',       FALSE, TRUE, FALSE, FALSE),
    ('usuarios',         FALSE, TRUE, FALSE, FALSE),
    ('verificaciones',   FALSE, TRUE, TRUE,  FALSE),
    ('trabajos',         FALSE, TRUE, FALSE, FALSE),
    ('ofertas',          FALSE, TRUE, FALSE, FALSE),
    ('contrataciones',   FALSE, TRUE, FALSE, FALSE),
    ('calificaciones',   FALSE, TRUE, FALSE, FALSE),
    ('chat',             FALSE, TRUE, FALSE, FALSE),
    ('notificaciones',   TRUE,  TRUE, FALSE, FALSE),
    ('adjuntos',         FALSE, TRUE, FALSE, TRUE ),
    ('reportes',         FALSE, TRUE, TRUE,  FALSE)
) AS p(modulo, crear, leer, editar, eliminar) ON p.modulo = m.nombre
ON CONFLICT DO NOTHING;

INSERT INTO rol_modulo (id_rol, id_modulo, puede_crear, puede_leer, puede_editar, puede_eliminar)
SELECT 3, m.id_modulo, p.crear, p.leer, p.editar, p.eliminar
FROM modulos m
JOIN (VALUES
    ('ubicacion',        FALSE, TRUE, FALSE, FALSE),
    ('categorias',       FALSE, TRUE, FALSE, FALSE),
    ('usuarios',         TRUE,  TRUE, TRUE,  TRUE ),
    ('verificaciones',   TRUE,  TRUE, TRUE,  FALSE),
    ('trabajos',         TRUE,  TRUE, TRUE,  TRUE ),
    ('ofertas',          TRUE,  TRUE, TRUE,  TRUE ),
    ('contrataciones',   TRUE,  TRUE, TRUE,  FALSE),
    ('calificaciones',   TRUE,  TRUE, TRUE,  TRUE ),
    ('chat',             TRUE,  TRUE, TRUE,  TRUE ),
    ('notificaciones',   TRUE,  TRUE, TRUE,  TRUE ),
    ('adjuntos',         TRUE,  TRUE, TRUE,  TRUE ),
    ('reportes',         TRUE,  TRUE, TRUE,  FALSE)
) AS p(modulo, crear, leer, editar, eliminar) ON p.modulo = m.nombre
ON CONFLICT DO NOTHING;

INSERT INTO pais (nombre) VALUES ('Colombia') ON CONFLICT DO NOTHING;

INSERT INTO ciudades (id_pais, nombre)
SELECT p.id_pais, c.nombre
FROM pais p,
     (VALUES ('Barranquilla'), ('Bogota'), ('Medellin'), ('Cali'),
             ('Cartagena'), ('Bucaramanga'), ('Santa Marta'), ('Soledad')) AS c(nombre)
WHERE p.nombre = 'Colombia'
ON CONFLICT DO NOTHING;

INSERT INTO categorias (nombre, descripcion) VALUES
    ('Hogar y reparaciones', 'Plomeria, electricidad, pintura, carpinteria'),
    ('Limpieza',             'Limpieza de casas, oficinas y vehiculos'),
    ('Transporte y mudanzas','Fletes, mudanzas y domicilios'),
    ('Jardineria',           'Mantenimiento de jardines y zonas verdes'),
    ('Tecnologia',           'Soporte tecnico, instalacion de equipos'),
    ('Eventos',              'Apoyo logistico y servicio en eventos'),
    ('Cuidado de personas',  'Cuidado de ninos, adultos mayores y mascotas'),
    ('Otros',                'Otros servicios')
ON CONFLICT DO NOTHING;

INSERT INTO habilidades (nombre, descripcion) VALUES
    ('Plomeria',       'Instalacion y reparacion de tuberias'),
    ('Electricidad',   'Instalaciones y reparaciones electricas'),
    ('Pintura',        'Pintura de interiores y exteriores'),
    ('Carpinteria',    'Trabajos en madera'),
    ('Limpieza',       'Limpieza general'),
    ('Jardineria',     'Poda y mantenimiento de jardines'),
    ('Conduccion',     'Transporte y mudanzas'),
    ('Soporte tecnico','Reparacion y configuracion de equipos')
ON CONFLICT DO NOTHING;
