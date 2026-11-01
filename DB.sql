
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
    ruta VARCHAR(100),  -- pagina del frontend a la que lleva el menu (ej: /trabajos)

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
    -- Rol actual: 1 Administrador, 2 Moderador, 3 Analista, 4 Empleador, 5 Empleado.
    -- El empleado y el empleador pueden cambiarse entre 4 y 5 con un boton.
    id_rol INTEGER NOT NULL DEFAULT 5,
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
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

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
    -- Equipo de InWork
    (1, 'Administrador', 'Acceso total: usuarios, roles, permisos, contrasenas y toda la informacion'),
    (2, 'Moderador',     'Revisa reportes y verificaciones, avisa a los usuarios y maneja los catalogos'),
    (3, 'Analista',      'Solo lectura: consulta informes y estadisticas de la plataforma'),
    -- Usuarios de la plataforma (pueden cambiarse entre empleador y empleado)
    (4, 'Empleador',     'Publica trabajos, contrata trabajadores y paga en custodia'),
    (5, 'Empleado',      'Ofrece sus servicios, envia ofertas y recibe los pagos')
ON CONFLICT DO NOTHING;

SELECT setval(pg_get_serial_sequence('roles','id_rol'),
              (SELECT MAX(id_rol) FROM roles));


INSERT INTO modulos (nombre, descripcion, ruta) VALUES
    ('roles',          'Roles, modulos y permisos',         '/roles'),
    ('ubicacion',      'Paises y ciudades',                 '/ubicacion'),
    ('categorias',     'Categorias y habilidades',          '/categorias'),
    ('usuarios',       'Usuarios y sus habilidades',        '/usuarios'),
    ('verificaciones', 'Verificacion de identidad',         '/verificaciones'),
    ('trabajos',       'Trabajos y habilidades requeridas', '/trabajos'),
    ('ofertas',        'Ofertas de trabajadores',           '/ofertas'),
    ('contrataciones', 'Contrataciones',                    '/contrataciones'),
    ('calificaciones', 'Calificaciones entre usuarios',     '/calificaciones'),
    ('chat',           'Chats y mensajes',                  '/chat'),
    ('notificaciones', 'Notificaciones y dispositivos',     '/notificaciones'),
    ('adjuntos',       'Archivos adjuntos',                 '/adjuntos'),
    ('reportes',       'Reportes de usuarios',              '/reportes'),
    ('seguridad',      'Tokens de usuario',                 '/seguridad'),
    ('auditoria',      'Registro de auditoria',             '/auditoria'),
    ('pagos',          'Pagos en custodia (API de pagos)',  '/pagos'),
    ('informes',       'Informes y estadisticas',           '/informes')
ON CONFLICT DO NOTHING;

-- PERMISOS DE CADA ROL (tabla rol_modulo). Con esto se arma el menu de cada rol.

-- 1. Administrador: todo
INSERT INTO rol_modulo (id_rol, id_modulo, puede_crear, puede_leer, puede_editar, puede_eliminar)
SELECT 1, id_modulo, TRUE, TRUE, TRUE, TRUE FROM modulos
ON CONFLICT DO NOTHING;

-- 2. Moderador: reportes, verificaciones, avisos a usuarios y catalogos
INSERT INTO rol_modulo (id_rol, id_modulo, puede_crear, puede_leer, puede_editar, puede_eliminar)
SELECT 2, m.id_modulo, p.crear, p.leer, p.editar, p.eliminar
FROM modulos m
JOIN (VALUES
    -- modulo            crear  leer  editar eliminar
    ('ubicacion',        TRUE,  TRUE, TRUE,  TRUE ),
    ('categorias',       TRUE,  TRUE, TRUE,  TRUE ),
    ('usuarios',         FALSE, TRUE, FALSE, FALSE),
    ('verificaciones',   FALSE, TRUE, TRUE,  TRUE ),
    ('trabajos',         FALSE, TRUE, FALSE, FALSE),
    ('ofertas',          FALSE, TRUE, FALSE, FALSE),
    ('contrataciones',   FALSE, TRUE, FALSE, FALSE),
    ('calificaciones',   FALSE, TRUE, FALSE, FALSE),
    ('chat',             FALSE, TRUE, FALSE, FALSE),
    ('notificaciones',   TRUE,  TRUE, TRUE,  TRUE ),
    ('adjuntos',         FALSE, TRUE, FALSE, TRUE ),
    ('reportes',         FALSE, TRUE, TRUE,  TRUE ),
    ('pagos',            FALSE, TRUE, TRUE,  FALSE)
) AS p(modulo, crear, leer, editar, eliminar) ON p.modulo = m.nombre
ON CONFLICT DO NOTHING;

-- 3. Analista: solo lectura
INSERT INTO rol_modulo (id_rol, id_modulo, puede_crear, puede_leer, puede_editar, puede_eliminar)
SELECT 3, m.id_modulo, FALSE, TRUE, FALSE, FALSE
FROM modulos m
WHERE m.nombre IN ('ubicacion', 'categorias', 'usuarios', 'verificaciones', 'trabajos', 'ofertas',
                   'contrataciones', 'calificaciones', 'notificaciones', 'reportes', 'pagos', 'informes')
ON CONFLICT DO NOTHING;

-- 4. Empleador: publica trabajos, acepta ofertas (crea la contratacion), paga y califica
INSERT INTO rol_modulo (id_rol, id_modulo, puede_crear, puede_leer, puede_editar, puede_eliminar)
SELECT 4, m.id_modulo, p.crear, p.leer, p.editar, p.eliminar
FROM modulos m
JOIN (VALUES
    ('ubicacion',        FALSE, TRUE, FALSE, FALSE),
    ('categorias',       FALSE, TRUE, FALSE, FALSE),
    ('usuarios',         FALSE, TRUE, TRUE,  TRUE ),
    ('verificaciones',   TRUE,  TRUE, TRUE,  FALSE),
    ('trabajos',         TRUE,  TRUE, TRUE,  TRUE ),
    ('ofertas',          FALSE, TRUE, FALSE, FALSE),
    ('contrataciones',   TRUE,  TRUE, TRUE,  FALSE),
    ('calificaciones',   TRUE,  TRUE, TRUE,  TRUE ),
    ('chat',             TRUE,  TRUE, TRUE,  TRUE ),
    ('notificaciones',   FALSE, TRUE, TRUE,  TRUE ),
    ('adjuntos',         TRUE,  TRUE, TRUE,  TRUE ),
    ('reportes',         TRUE,  TRUE, TRUE,  FALSE),
    ('pagos',            TRUE,  TRUE, TRUE,  FALSE)
) AS p(modulo, crear, leer, editar, eliminar) ON p.modulo = m.nombre
ON CONFLICT DO NOTHING;

-- 5. Empleado: envia ofertas, registra sus habilidades, cobra y califica
INSERT INTO rol_modulo (id_rol, id_modulo, puede_crear, puede_leer, puede_editar, puede_eliminar)
SELECT 5, m.id_modulo, p.crear, p.leer, p.editar, p.eliminar
FROM modulos m
JOIN (VALUES
    ('ubicacion',        FALSE, TRUE, FALSE, FALSE),
    ('categorias',       FALSE, TRUE, FALSE, FALSE),
    ('usuarios',         TRUE,  TRUE, TRUE,  TRUE ),
    ('verificaciones',   TRUE,  TRUE, TRUE,  FALSE),
    ('trabajos',         FALSE, TRUE, FALSE, FALSE),
    ('ofertas',          TRUE,  TRUE, TRUE,  TRUE ),
    ('contrataciones',   FALSE, TRUE, TRUE,  FALSE),
    ('calificaciones',   TRUE,  TRUE, TRUE,  TRUE ),
    ('chat',             TRUE,  TRUE, TRUE,  TRUE ),
    ('notificaciones',   FALSE, TRUE, TRUE,  TRUE ),
    ('adjuntos',         TRUE,  TRUE, TRUE,  TRUE ),
    ('reportes',         TRUE,  TRUE, TRUE,  FALSE),
    ('pagos',            TRUE,  TRUE, TRUE,  FALSE)
) AS p(modulo, crear, leer, editar, eliminar) ON p.modulo = m.nombre
ON CONFLICT DO NOTHING;

INSERT INTO pais (nombre) VALUES
    ('Colombia'),     -- id 1
    ('Venezuela'),    -- id 2
    ('Ecuador'),      -- id 3
    ('Peru'),         -- id 4
    ('Panama'),       -- id 5
    ('Mexico'),       -- id 6
    ('Chile'),        -- id 7
    ('Argentina'),    -- id 8
    ('Costa Rica'),   -- id 9
    ('Republica Dominicana') -- id 10
ON CONFLICT DO NOTHING;

-- Todas las ciudades son de Colombia (id_pais = 1)
INSERT INTO ciudades (id_pais, nombre) VALUES
    (1, 'Barranquilla'),  -- id 1
    (1, 'Bogota'),        -- id 2
    (1, 'Medellin'),      -- id 3
    (1, 'Cali'),          -- id 4
    (1, 'Cartagena'),     -- id 5
    (1, 'Bucaramanga'),   -- id 6
    (1, 'Santa Marta'),   -- id 7
    (1, 'Soledad'),       -- id 8
    (1, 'Monteria'),      -- id 9
    (1, 'Valledupar')     -- id 10
ON CONFLICT DO NOTHING;

INSERT INTO categorias (nombre, descripcion) VALUES
    ('Hogar y reparaciones', 'Plomeria, electricidad, pintura, carpinteria'),
    ('Limpieza',             'Limpieza de casas, oficinas y vehiculos'),
    ('Transporte y mudanzas','Fletes, mudanzas y domicilios'),
    ('Jardineria',           'Mantenimiento de jardines y zonas verdes'),
    ('Tecnologia',           'Soporte tecnico, instalacion de equipos'),
    ('Eventos',              'Apoyo logistico y servicio en eventos'),
    ('Cuidado de personas',  'Cuidado de ninos, adultos mayores y mascotas'),
    ('Otros',                'Otros servicios'),
    ('Clases y tutorias',    'Refuerzo escolar, clases de idiomas y de musica'),
    ('Belleza y cuidado personal', 'Peluqueria, manicure y maquillaje a domicilio')
ON CONFLICT DO NOTHING;

INSERT INTO habilidades (nombre, descripcion) VALUES
    ('Plomeria',       'Instalacion y reparacion de tuberias'),
    ('Electricidad',   'Instalaciones y reparaciones electricas'),
    ('Pintura',        'Pintura de interiores y exteriores'),
    ('Carpinteria',    'Trabajos en madera'),
    ('Limpieza',       'Limpieza general'),
    ('Jardineria',     'Poda y mantenimiento de jardines'),
    ('Conduccion',     'Transporte y mudanzas'),
    ('Soporte tecnico','Reparacion y configuracion de equipos'),
    ('Refrigeracion',  'Mantenimiento de aires acondicionados y neveras'),
    ('Tutorias academicas', 'Refuerzo en matematicas, ingles y otras materias')
ON CONFLICT DO NOTHING;

-- =====================================================================
-- DATOS DE PRUEBA
-- Tablas principales: 20 registros o mas. Tablas secundarias: 10 o mas.
-- Todos los usuarios tienen la contrasena: Inwork2026*
--   Administrador: sebastian.rojas@inwork.com.co
--   Moderadora:    mariana.castro@inwork.com.co
--   Analista:      jorge.pertuz@inwork.com.co
--   Empleador:     valentina.mendoza93@gmail.com   Empleado: kevin.escorcia.elec@gmail.com
-- Los IDs de los comentarios (-- id N) son los que quedan al correr el script en una BD nueva.
-- =====================================================================

-- USUARIOS (20): 1 administrador, 1 moderadora, 1 analista y 17 usuarios
-- Del 4 al 11 publican trabajos (empleadores). Del 12 al 20 ofrecen servicios (empleados).
-- id_rol: 1 Administrador, 2 Moderador, 3 Analista, 4 Empleador, 5 Empleado
INSERT INTO usuarios (id_rol, id_ciudad, nombre, apellido, password, correo, correo_verificado, telefono, tipo_identificacion, numero_identificacion, fecha_nacimiento, descripcion, direccion) VALUES
    (1, 1, 'Sebastian', 'Rojas Molina', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'sebastian.rojas@inwork.com.co', TRUE, '3005124789', 'cedula', '1140825613', '1992-03-14', 'Administrador general de la plataforma InWork', 'Carrera 53 #79-120, Alto Prado'),  -- id 1
    (2, 1, 'Mariana', 'Castro Vega', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'mariana.castro@inwork.com.co', TRUE, '3014587236', 'cedula', '1143162087', '1996-07-22', 'Moderadora: revisa reportes y verificaciones de identidad', 'Calle 76 #44-31, El Prado'),  -- id 2
    (3, 8, 'Jorge Luis', 'Pertuz Ruiz', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'jorge.pertuz@inwork.com.co', TRUE, '3216650941', 'cedula', '1048276354', '1990-11-05', 'Analista de datos: revisa informes y estadisticas de la plataforma', 'Calle 30 #19-45, Soledad 2000'),  -- id 3
    (4, 1, 'Valentina', 'Mendoza Rios', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'valentina.mendoza93@gmail.com', TRUE, '3007841256', 'cedula', '1140863521', '1993-02-18', 'Odontologa. Publico trabajos de mantenimiento para mi apartamento y mi consultorio', 'Calle 98 #52-115, Riomar'),  -- id 4
    (4, 1, 'Ricardo', 'Barrios Fonseca', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'ricardo.barrios@hotmail.com', TRUE, '3104528897', 'cedula', '72215634', '1978-09-30', 'Comerciante, dueno de una ferreteria en el centro', 'Carrera 44 #34-12, Centro'),  -- id 5
    (4, 1, 'Paola Andrea', 'Charris Lopez', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'paola.charris@gmail.com', TRUE, '3152367841', 'cedula', '1129574382', '1988-12-03', 'Madre de dos ninos, busco apoyo con la casa y el cuidado de mi mama', 'Calle 85 #47-60, Villa Country'),  -- id 6
    (4, 1, 'Luis Fernando', 'De la Hoz Pacheco', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'luisf.delahoz@gmail.com', TRUE, '3005897412', 'cedula', '8754123', '1969-04-11', 'Pensionado. Necesito ayuda con reparaciones de la casa', 'Carrera 21B #63-14, Boston'),  -- id 7
    (4, 8, 'Natalia', 'Ospino Marquez', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'natalia.ospino@outlook.com', TRUE, '3017452369', 'cedula', '1042451873', '1997-06-25', 'Contadora independiente, trabajo desde la casa', 'Calle 63 #13-28, Villa Katanga'),  -- id 8
    (4, 1, 'Hernan', 'Polo Gutierrez', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'hernan.polo@gmail.com', TRUE, '3126985471', 'cedula', '72189456', '1975-01-19', 'Administrador de un edificio residencial', 'Calle 79 #42F-35, Ciudad Jardin'),  -- id 9
    (4, 1, 'Camila', 'Ariza Bolano', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'camila.ariza@gmail.com', TRUE, '3045896321', 'cedula', '1082945612', '1995-10-08', 'Duena de una panaderia en Las Delicias', 'Calle 61 #27-35, Las Delicias'),  -- id 10
    (4, 1, 'Daniela', 'Orozco Mejia', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'daniela.orozcom@gmail.com', FALSE, '3008527413', 'cedula', '1143258796', '1999-05-12', 'Organizo eventos y celebraciones familiares', 'Calle 47 #22-18, Los Andes'),  -- id 11
    (5, 1, 'Kevin', 'Escorcia Rada', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'kevin.escorcia.elec@gmail.com', TRUE, '3016548923', 'cedula', '1140812349', '1994-08-02', 'Tecnico electricista certificado RETIE, 8 anos de experiencia', 'Carrera 8 #45-23, Rebolo'),  -- id 12
    (5, 8, 'Yesid', 'Cantillo Barraza', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'yesid.cantillo@gmail.com', TRUE, '3135478962', 'cedula', '1048932156', '1987-03-27', 'Plomero. Reparo fugas, instalo sanitarios y calentadores', 'Calle 18 #25-40, Soledad'),  -- id 13
    (5, 1, 'Wilmer', 'Navarro Fruto', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'wilmer.navarro.pintor@gmail.com', TRUE, '3002145698', 'cedula', '72298741', '1980-12-15', 'Pintor y carpintero para casas y locales comerciales', 'Carrera 6 #50-12, La Chinita'),  -- id 14
    (5, 1, 'Luz Marina', 'Arrieta Julio', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'luzmarina.arrieta@gmail.com', TRUE, '3205874123', 'cedula', '32745896', '1976-07-09', 'Limpieza de casas y oficinas, tambien mantenimiento de jardines', 'Carrera 9G #52-30, La Victoria'),  -- id 15
    (5, 1, 'Edinson', 'Ballestas Mercado', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'edinson.refrigeracion@gmail.com', TRUE, '3017856942', 'cedula', '1129896574', '1991-01-23', 'Tecnico en refrigeracion: instalacion y mantenimiento de aires acondicionados', 'Calle 54 #9-80, Las Nieves'),  -- id 16
    (5, 1, 'Jesus Alberto', 'Marquez Sulbaran', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'jesus.marquez.fletes@gmail.com', TRUE, '3229654781', 'cedula de extranjeria', '5874129', '1985-09-14', 'Conductor con camion propio para mudanzas y fletes', 'Carrera 38 #69C-21, Los Alpes'),  -- id 17
    (5, 1, 'Sandra Milena', 'Cervantes Ortega', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'sandra.cervantes@gmail.com', TRUE, '3114785236', 'cedula', '22658974', '1972-04-30', 'Auxiliar de enfermeria, cuido adultos mayores y ninos', 'Carrera 14 #45-60, San Jose'),  -- id 18
    (5, 1, 'Julian David', 'Salcedo Montero', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'julian.salcedo.tech@gmail.com', TRUE, '3043256987', 'cedula', '1143789652', '1998-11-11', 'Tecnologo en sistemas. Reparo computadores, redes y camaras', 'Calle 74 #38-52, Bellavista'),  -- id 19
    (5, 1, 'Andrea Carolina', 'Padilla Torres', '$2b$12$LYPbPquWHw2FxwwvwCESIOHzpuad5UX0vu9ehJelIYix51o52OGCC', 'andrea.padilla.tutora@gmail.com', TRUE, '3157896412', 'cedula', '1140896325', '2000-02-28', 'Estudiante de licenciatura en matematicas, doy clases de refuerzo e ingles', 'Carrera 46 #91-20, Paraiso');  -- id 20

-- HABILIDADES DE CADA TRABAJADOR
-- habilidades: 1 Plomeria, 2 Electricidad, 3 Pintura, 4 Carpinteria, 5 Limpieza, 6 Jardineria,
--              7 Conduccion, 8 Soporte tecnico, 9 Refrigeracion, 10 Tutorias academicas
INSERT INTO usuarios_habilidades (id_usuario, id_habilidad, anios_experiencia) VALUES
    (12, 2, 8),  -- Kevin Escorcia
    (12, 8, 2),  -- Kevin Escorcia
    (13, 1, 10),  -- Yesid Cantillo
    (13, 3, 3),  -- Yesid Cantillo
    (14, 3, 15),  -- Wilmer Navarro
    (14, 4, 12),  -- Wilmer Navarro
    (14, 6, 4),  -- Wilmer Navarro
    (15, 5, 12),  -- Luz Marina Arrieta
    (15, 6, 5),  -- Luz Marina Arrieta
    (16, 9, 7),  -- Edinson Ballestas
    (16, 2, 4),  -- Edinson Ballestas
    (17, 7, 11),  -- Jesus Alberto Marquez
    (18, 5, 6),  -- Sandra Milena Cervantes
    (19, 8, 5),  -- Julian David Salcedo
    (19, 2, 2),  -- Julian David Salcedo
    (20, 10, 3);  -- Andrea Carolina Padilla

-- VERIFICACION DE IDENTIDAD
INSERT INTO verificacion_identidad (id_usuario, url_documento_frente, url_documento_reverso, url_selfie, estado_verificacion, id_admin_revisor, observacion, fecha_revision) VALUES
    (4, 'https://storage.inwork.com.co/verificaciones/usuario_04_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_04_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_04_selfie.jpg', 'aprobada', 2, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '26 days'),  -- Valentina Mendoza
    (5, 'https://storage.inwork.com.co/verificaciones/usuario_05_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_05_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_05_selfie.jpg', 'aprobada', 1, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '25 days'),  -- Ricardo Barrios
    (6, 'https://storage.inwork.com.co/verificaciones/usuario_06_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_06_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_06_selfie.jpg', 'aprobada', 2, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '24 days'),  -- Paola Andrea Charris
    (7, 'https://storage.inwork.com.co/verificaciones/usuario_07_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_07_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_07_selfie.jpg', 'aprobada', 1, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '23 days'),  -- Luis Fernando De
    (8, 'https://storage.inwork.com.co/verificaciones/usuario_08_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_08_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_08_selfie.jpg', 'aprobada', 2, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '22 days'),  -- Natalia Ospino
    (9, 'https://storage.inwork.com.co/verificaciones/usuario_09_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_09_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_09_selfie.jpg', 'aprobada', 1, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '21 days'),  -- Hernan Polo
    (10, 'https://storage.inwork.com.co/verificaciones/usuario_10_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_10_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_10_selfie.jpg', 'pendiente', NULL, NULL, NULL),  -- Camila Ariza
    (11, 'https://storage.inwork.com.co/verificaciones/usuario_11_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_11_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_11_selfie.jpg', 'rechazada', 2, 'La selfie esta borrosa, no se ve el rostro completo.', CURRENT_TIMESTAMP - INTERVAL '20 days'),  -- Daniela Orozco
    (12, 'https://storage.inwork.com.co/verificaciones/usuario_12_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_12_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_12_selfie.jpg', 'aprobada', 2, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '18 days'),  -- Kevin Escorcia
    (13, 'https://storage.inwork.com.co/verificaciones/usuario_13_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_13_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_13_selfie.jpg', 'aprobada', 1, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '17 days'),  -- Yesid Cantillo
    (14, 'https://storage.inwork.com.co/verificaciones/usuario_14_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_14_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_14_selfie.jpg', 'aprobada', 2, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '16 days'),  -- Wilmer Navarro
    (15, 'https://storage.inwork.com.co/verificaciones/usuario_15_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_15_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_15_selfie.jpg', 'aprobada', 1, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '15 days'),  -- Luz Marina Arrieta
    (16, 'https://storage.inwork.com.co/verificaciones/usuario_16_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_16_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_16_selfie.jpg', 'aprobada', 2, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '14 days'),  -- Edinson Ballestas
    (17, 'https://storage.inwork.com.co/verificaciones/usuario_17_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_17_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_17_selfie.jpg', 'aprobada', 1, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '13 days'),  -- Jesus Alberto Marquez
    (18, 'https://storage.inwork.com.co/verificaciones/usuario_18_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_18_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_18_selfie.jpg', 'aprobada', 2, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '12 days'),  -- Sandra Milena Cervantes
    (19, 'https://storage.inwork.com.co/verificaciones/usuario_19_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_19_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_19_selfie.jpg', 'aprobada', 1, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '11 days'),  -- Julian David Salcedo
    (20, 'https://storage.inwork.com.co/verificaciones/usuario_20_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_20_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_20_selfie.jpg', 'aprobada', 2, 'Documento y selfie coinciden.', CURRENT_TIMESTAMP - INTERVAL '10 days'),  -- Andrea Carolina Padilla
    (11, 'https://storage.inwork.com.co/verificaciones/usuario_11_frente.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_11_reverso.jpg', 'https://storage.inwork.com.co/verificaciones/usuario_11_selfie.jpg', 'pendiente', NULL, NULL, NULL);  -- Daniela Orozco

-- TRABAJOS (26)
-- Los trabajos ya terminados tienen fecha pasada, por eso se apaga un momento
-- el trigger que no deja crear trabajos con fecha anterior a hoy.
-- categorias: 1 Hogar, 2 Limpieza, 3 Transporte, 4 Jardineria, 5 Tecnologia, 6 Eventos,
--             7 Cuidado de personas, 8 Otros, 9 Clases y tutorias, 10 Belleza
ALTER TABLE trabajos DISABLE TRIGGER trg_trabajos_fecha;

INSERT INTO trabajos (id_cliente, id_categoria, id_ciudad, titulo, descripcion, direccion, latitud, longitud, fecha_trabajo, hora_inicio, hora_fin, presupuesto, estado_trabajo) VALUES
    (4, 1, 1, 'Reparar fuga en el lavaplatos', 'La tuberia debajo del lavaplatos gotea y ya mojo el mueble. Hay que revisar y cambiar el sifon.', 'Calle 98 #52-115, Apto 502, Riomar', 11.0189, -74.8291, CURRENT_DATE - 28, '08:00', '10:00', 120000, 'finalizado'),  -- id 1 - finalizado
    (7, 1, 1, 'Instalar ventiladores de techo', 'Instalar dos ventiladores de techo en las habitaciones. Ya estan comprados.', 'Carrera 21B #63-14, Boston', 10.9978, -74.7975, CURRENT_DATE - 25, '09:00', '12:00', 180000, 'finalizado'),  -- id 2 - finalizado
    (6, 2, 1, 'Limpieza profunda de apartamento', 'Apartamento de 3 habitaciones: cocina, dos banos, ventanas y balcon.', 'Calle 85 #47-60, Villa Country', 11.0063, -74.8115, CURRENT_DATE - 22, '07:00', '15:00', 150000, 'finalizado'),  -- id 3 - finalizado
    (9, 1, 1, 'Pintar fachada del edificio', 'Pintar la fachada frontal de un edificio de 3 pisos. La administracion pone la pintura.', 'Calle 79 #42F-35, Ciudad Jardin', 10.9995, -74.8072, CURRENT_DATE - 20, '07:00', '17:00', 1200000, 'finalizado'),  -- id 4 - finalizado
    (4, 1, 1, 'Mantenimiento de 2 aires acondicionados', 'Lavado y revision de gas de dos aires mini split de 12000 BTU en el consultorio.', 'Carrera 51B #82-254, Consultorio 305, Alto Prado', 11.0048, -74.815, CURRENT_DATE - 18, '08:00', '11:00', 220000, 'finalizado'),  -- id 5 - finalizado
    (5, 3, 1, 'Transporte de materiales a una obra en Soledad', 'Llevar 40 bultos de cemento y 20 tubos PVC desde la ferreteria hasta una obra en Soledad.', 'Carrera 44 #34-12, Centro', 10.9792, -74.7826, CURRENT_DATE - 15, '06:00', '10:00', 250000, 'finalizado'),  -- id 6 - finalizado
    (8, 5, 8, 'Configurar red wifi y revisar computador', 'El internet no llega a la oficina de la casa. Instalar un repetidor y revisar el computador que esta lento.', 'Calle 63 #13-28, Villa Katanga', 10.915, -74.7706, CURRENT_DATE - 12, '14:00', '17:00', 130000, 'finalizado'),  -- id 7 - finalizado
    (10, 1, 1, 'Arreglar puerta del bano y closet', 'La puerta del bano no cierra y una puerta del closet se descolgo. Ajustar bisagras y cepillar.', 'Calle 61 #27-35, Las Delicias', 10.9905, -74.8006, CURRENT_DATE - 9, '08:00', '12:00', 160000, 'finalizado'),  -- id 8 - finalizado
    (6, 7, 1, 'Cuidado de adulto mayor un fin de semana', 'Acompanar a mi mama de 82 anos sabado y domingo, darle sus medicamentos y comidas.', 'Calle 85 #47-60, Villa Country', 11.0063, -74.8115, CURRENT_DATE - 7, '08:00', '18:00', 300000, 'finalizado'),  -- id 9 - finalizado
    (11, 9, 1, 'Clases de refuerzo de matematicas', 'Refuerzo para mi hermano de noveno grado antes de los examenes finales. 4 sesiones.', 'Calle 47 #22-18, Los Andes', 10.98, -74.804, CURRENT_DATE - 5, '15:00', '17:00', 160000, 'finalizado'),  -- id 10 - finalizado
    (9, 1, 1, 'Cambiar tablero electrico de zonas comunes', 'El tablero de las zonas comunes esta viejo y se dispara. Cambiar breakers y organizar el cableado.', 'Calle 79 #42F-35, Ciudad Jardin', 10.9995, -74.8072, CURRENT_DATE + 3, '08:00', '14:00', 650000, 'asignado'),  -- id 11 - asignado
    (7, 1, 1, 'Instalar calentador de agua a gas', 'Instalar un calentador de paso a gas en la cocina con todas sus conexiones.', 'Carrera 21B #63-14, Boston', 10.9978, -74.7975, CURRENT_DATE + 4, '09:00', '12:00', 200000, 'asignado'),  -- id 12 - asignado
    (11, 6, 1, 'Apoyo logistico en fiesta de 15 anos', 'Transporte, montaje y desmontaje de mesas, sillas y decoracion para 80 invitados.', 'Calle 72 #46-50, El Prado', 10.9974, -74.803, CURRENT_DATE + 6, '14:00', '23:00', 280000, 'asignado'),  -- id 13 - asignado
    (4, 2, 1, 'Limpieza semanal del consultorio', 'Limpieza del consultorio odontologico: pisos, banos y sala de espera.', 'Carrera 51B #82-254, Consultorio 305, Alto Prado', 11.0048, -74.815, CURRENT_DATE + 2, '18:00', '21:00', 90000, 'asignado'),  -- id 14 - asignado
    (5, 1, 1, 'Instalar aire acondicionado en la oficina', 'Instalar un aire mini split de 18000 BTU en la oficina de la ferreteria, incluye tuberia de cobre.', 'Carrera 44 #34-12, Centro', 10.9792, -74.7826, CURRENT_DATE + 5, '08:00', '13:00', 380000, 'asignado'),  -- id 15 - asignado
    (8, 9, 8, 'Clases de ingles para nina de 10 anos', 'Clases de ingles dos veces por semana durante un mes.', 'Calle 63 #13-28, Villa Katanga', 10.915, -74.7706, CURRENT_DATE + 7, '16:00', '18:00', 240000, 'asignado'),  -- id 16 - asignado
    (10, 5, 1, 'Instalar camaras de seguridad en la panaderia', 'Instalar 4 camaras con grabador y dejar la vista en el celular.', 'Calle 61 #27-35, Las Delicias', 10.9905, -74.8006, CURRENT_DATE + 8, '08:00', '15:00', 520000, 'asignado'),  -- id 17 - asignado
    (6, 4, 1, 'Poda de arboles del patio', 'Podar un palo de mango y un almendro que golpean el techo. Recoger las ramas.', 'Calle 85 #47-60, Villa Country', 11.0063, -74.8115, CURRENT_DATE + 9, '07:00', '12:00', 200000, 'publicado'),  -- id 18 - publicado
    (5, 1, 1, 'Pintar local comercial', 'Pintar las paredes internas del local (60 m2 aprox.) y la reja de la entrada.', 'Carrera 44 #34-12, Centro', 10.9792, -74.7826, CURRENT_DATE + 10, '07:00', '17:00', 500000, 'publicado'),  -- id 19 - publicado
    (7, 3, 1, 'Mudanza de apartamento a casa', 'Mudanza de un apartamento de 2 habitaciones desde Boston hasta el barrio La Concepcion.', 'Carrera 21B #63-14, Boston', 10.9978, -74.7975, CURRENT_DATE + 12, '07:00', '13:00', 450000, 'publicado'),  -- id 20 - publicado
    (9, 2, 1, 'Lavado de tanques de agua del edificio', 'Lavar y desinfectar dos tanques elevados de 2000 litros.', 'Calle 79 #42F-35, Ciudad Jardin', 10.9995, -74.8072, CURRENT_DATE + 11, '07:00', '13:00', 350000, 'publicado'),  -- id 21 - publicado
    (11, 10, 1, 'Maquillaje y peinado para una boda', 'Maquillaje y peinado para 3 personas antes de una boda.', 'Calle 47 #22-18, Los Andes', 10.98, -74.804, CURRENT_DATE + 14, '13:00', '17:00', 270000, 'publicado'),  -- id 22 - publicado
    (4, 1, 1, 'Cambiar griferia del bano', 'Cambiar la llave del lavamanos y la ducha por griferia nueva.', 'Calle 98 #52-115, Apto 502, Riomar', 11.0189, -74.8291, CURRENT_DATE + 6, '09:00', '12:00', 140000, 'publicado'),  -- id 23 - publicado
    (5, 3, 5, 'Flete de estanteria a Cartagena', 'Llevar estanteria metalica desarmada desde Barranquilla hasta un local en Bazurto, Cartagena.', 'Avenida Pedro de Heredia #30-15, Bazurto', 10.4185, -75.5375, CURRENT_DATE + 9, '05:00', '14:00', 900000, 'publicado'),  -- id 24 - publicado
    (8, 1, 8, 'Reparar techo con goteras', 'Revisar y sellar las goteras del techo de eternit antes de la temporada de lluvias.', 'Calle 63 #13-28, Villa Katanga', 10.915, -74.7706, CURRENT_DATE + 5, '08:00', '12:00', 260000, 'cancelado'),  -- id 25 - cancelado
    (10, 8, 1, 'Armar muebles de la sala', 'Armar un sofa modular y un mueble de TV comprados en tienda.', 'Calle 61 #27-35, Las Delicias', 10.9905, -74.8006, CURRENT_DATE + 4, '14:00', '18:00', 110000, 'publicado');  -- id 26 - publicado

ALTER TABLE trabajos ENABLE TRIGGER trg_trabajos_fecha;

-- HABILIDADES QUE PIDE CADA TRABAJO
INSERT INTO trabajos_habilidades (id_trabajo, id_habilidad) VALUES
    (1, 1),
    (2, 2),
    (3, 5),
    (4, 3),
    (5, 9),
    (6, 7),
    (7, 8),
    (8, 4),
    (10, 10),
    (11, 2),
    (12, 1),
    (13, 7),
    (14, 5),
    (15, 9),
    (15, 2),
    (16, 10),
    (17, 8),
    (17, 2),
    (18, 6),
    (19, 3),
    (20, 7),
    (21, 5),
    (21, 1),
    (23, 1),
    (24, 7),
    (25, 4),
    (26, 4);

-- OFERTAS
-- Las 20 primeras son las aceptadas: la oferta N corresponde al trabajo N y a la contratacion N.
INSERT INTO ofertas (id_trabajo, id_trabajador, valor_oferta, mensaje, estado_oferta) VALUES
    (1, 13, 110000, 'Puedo ir temprano, llevo el sifon y la cinta de teflon.', 'aceptada'),  -- id 1
    (2, 12, 170000, 'Instalo los dos ventiladores con su interruptor.', 'aceptada'),  -- id 2
    (3, 15, 150000, 'Llevo todos los implementos de aseo.', 'aceptada'),  -- id 3
    (4, 14, 1150000, 'Tengo andamio propio, lo hago en dos dias.', 'aceptada'),  -- id 4
    (5, 16, 200000, 'Incluye lavado, revision de gas y limpieza de filtros.', 'aceptada'),  -- id 5
    (6, 17, 250000, 'Tengo camion de 3 toneladas, cabe todo en un viaje.', 'aceptada'),  -- id 6
    (7, 19, 120000, 'Llevo el repetidor y hago mantenimiento al computador.', 'aceptada'),  -- id 7
    (8, 14, 150000, 'Ajusto las bisagras y cepillo las puertas.', 'aceptada'),  -- id 8
    (9, 18, 300000, 'Soy auxiliar de enfermeria, tengo experiencia con adultos mayores.', 'aceptada'),  -- id 9
    (10, 20, 150000, 'Llevo guias de ejercicios para cada tema.', 'aceptada'),  -- id 10
    (11, 12, 620000, 'Cambio el tablero y dejo los circuitos marcados.', 'aceptada'),  -- id 11
    (12, 13, 190000, 'Incluye la conexion de gas y la prueba de fugas.', 'aceptada'),  -- id 12
    (13, 17, 280000, 'Llevo las mesas y sillas en el camion y ayudo a montar.', 'aceptada'),  -- id 13
    (14, 15, 90000, 'Puedo ir todos los viernes en la noche.', 'aceptada'),  -- id 14
    (15, 16, 360000, 'Incluye tuberia de cobre hasta 3 metros.', 'aceptada'),  -- id 15
    (16, 20, 220000, 'Clases martes y jueves de 4 a 6.', 'aceptada'),  -- id 16
    (17, 19, 500000, 'Instalo y configuro la app en su celular.', 'aceptada'),  -- id 17
    (18, 15, 180000, 'Hago la poda y dejo el patio limpio.', 'aceptada'),  -- id 18
    (19, 13, 480000, 'Tambien hago trabajos de pintura.', 'aceptada'),  -- id 19
    (20, 17, 420000, 'Hago la mudanza con dos ayudantes.', 'aceptada'),  -- id 20
    (2, 16, 190000, 'Tambien instalo ventiladores.', 'rechazada'),  -- id 21
    (2, 19, 200000, 'Puedo ir esta semana.', 'rechazada'),  -- id 22
    (3, 18, 160000, 'Tengo experiencia en limpieza de apartamentos.', 'rechazada'),  -- id 23
    (4, 13, 1300000, 'Lo hago en tres dias con un ayudante.', 'rechazada'),  -- id 24
    (7, 12, 140000, 'Reviso la red y el computador.', 'rechazada'),  -- id 25
    (11, 16, 700000, 'Tengo experiencia en tableros de edificios.', 'rechazada'),  -- id 26
    (14, 18, 95000, 'Puedo ir lunes y viernes.', 'rechazada'),  -- id 27
    (17, 12, 550000, 'Instalo camaras Hikvision con garantia.', 'rechazada'),  -- id 28
    (18, 14, 210000, 'Tengo motosierra y escalera, lo hago en una manana.', 'pendiente'),  -- id 29
    (19, 14, 470000, 'Pinto el local en un dia y la reja al siguiente.', 'pendiente'),  -- id 30
    (21, 13, 340000, 'Lavo los tanques y reviso las tuberias.', 'pendiente'),  -- id 31
    (21, 15, 320000, 'Uso productos para desinfectar tanques.', 'pendiente'),  -- id 32
    (23, 13, 130000, 'Cambio la griferia el mismo dia.', 'pendiente'),  -- id 33
    (24, 17, 850000, 'Salgo de madrugada y llego antes del mediodia.', 'pendiente'),  -- id 34
    (26, 14, 100000, 'Armo los muebles en una tarde.', 'pendiente'),  -- id 35
    (23, 12, 150000, 'Puedo ir el sabado.', 'retirada'),  -- id 36
    (25, 14, 250000, 'Sello las goteras con manto asfaltico.', 'retirada');  -- id 37

-- CONTRATACIONES (20): 10 finalizadas, 7 activas y 3 canceladas
INSERT INTO contrataciones (id_trabajo, id_cliente, id_trabajador, id_oferta, estado_contratacion) VALUES
    (1, 4, 13, 1, 'finalizada'),  -- id 1
    (2, 7, 12, 2, 'finalizada'),  -- id 2
    (3, 6, 15, 3, 'finalizada'),  -- id 3
    (4, 9, 14, 4, 'finalizada'),  -- id 4
    (5, 4, 16, 5, 'finalizada'),  -- id 5
    (6, 5, 17, 6, 'finalizada'),  -- id 6
    (7, 8, 19, 7, 'finalizada'),  -- id 7
    (8, 10, 14, 8, 'finalizada'),  -- id 8
    (9, 6, 18, 9, 'finalizada'),  -- id 9
    (10, 11, 20, 10, 'finalizada'),  -- id 10
    (11, 9, 12, 11, 'activa'),  -- id 11
    (12, 7, 13, 12, 'activa'),  -- id 12
    (13, 11, 17, 13, 'activa'),  -- id 13
    (14, 4, 15, 14, 'activa'),  -- id 14
    (15, 5, 16, 15, 'activa'),  -- id 15
    (16, 8, 20, 16, 'activa'),  -- id 16
    (17, 10, 19, 17, 'activa'),  -- id 17
    (18, 6, 15, 18, 'cancelada'),  -- id 18
    (19, 5, 13, 19, 'cancelada'),  -- id 19
    (20, 7, 17, 20, 'cancelada');  -- id 20

-- CALIFICACIONES (20): en cada contratacion finalizada el cliente califica al trabajador y al reves.
-- El trigger trg_calificacion_reputacion actualiza solo el promedio de cada usuario.
INSERT INTO calificacion (id_calificador, id_calificado, id_trabajo, puntuacion, comentario) VALUES
    (4, 13, 1, 5, 'Llego puntual y dejo todo limpio. Muy recomendado.'),
    (13, 4, 1, 5, 'Clienta muy amable y clara con lo que necesitaba.'),
    (7, 12, 2, 5, 'Excelente trabajo, los ventiladores quedaron perfectos.'),
    (12, 7, 2, 4, 'Buen cliente, pago puntual.'),
    (6, 15, 3, 5, 'Dejo el apartamento impecable.'),
    (15, 6, 3, 5, 'Muy buena atencion.'),
    (9, 14, 4, 4, 'Buen acabado, pero se demoro un dia mas de lo acordado.'),
    (14, 9, 4, 5, 'Tenian listos los materiales y el permiso del edificio.'),
    (4, 16, 5, 5, 'Los aires quedaron enfriando como nuevos.'),
    (16, 4, 5, 5, 'Todo muy organizado en el consultorio.'),
    (5, 17, 6, 4, 'Cumplio con la entrega sin problemas.'),
    (17, 5, 6, 3, 'Me hicieron esperar casi dos horas para cargar.'),
    (8, 19, 7, 5, 'Ahora el wifi llega a toda la casa y el computador va rapido.'),
    (19, 8, 7, 5, 'Clienta muy puntual.'),
    (10, 14, 8, 3, 'Arreglo la puerta, pero el closet sigue rozando un poco.'),
    (14, 10, 8, 4, 'Buena clienta.'),
    (6, 18, 9, 5, 'Mi mama quedo feliz, muy carinosa y responsable.'),
    (18, 6, 9, 5, 'Familia muy respetuosa.'),
    (11, 20, 10, 5, 'Mi hermano gano el examen final, excelente profe.'),
    (20, 11, 10, 5, 'El estudiante fue muy juicioso.');

-- CHATS (20): uno por cada contratacion
INSERT INTO chat (id_trabajo, id_cliente, id_trabajador) VALUES
    (1, 4, 13),  -- id 1
    (2, 7, 12),  -- id 2
    (3, 6, 15),  -- id 3
    (4, 9, 14),  -- id 4
    (5, 4, 16),  -- id 5
    (6, 5, 17),  -- id 6
    (7, 8, 19),  -- id 7
    (8, 10, 14),  -- id 8
    (9, 6, 18),  -- id 9
    (10, 11, 20),  -- id 10
    (11, 9, 12),  -- id 11
    (12, 7, 13),  -- id 12
    (13, 11, 17),  -- id 13
    (14, 4, 15),  -- id 14
    (15, 5, 16),  -- id 15
    (16, 8, 20),  -- id 16
    (17, 10, 19),  -- id 17
    (18, 6, 15),  -- id 18
    (19, 5, 13),  -- id 19
    (20, 7, 17);  -- id 20

-- MENSAJES
INSERT INTO mensajes (id_chat, id_remitente, mensaje, leido) VALUES
    (1, 4, 'Hola Yesid, la fuga es debajo del lavaplatos. Puedes venir el sabado?', TRUE),  -- id 1
    (1, 13, 'Hola, si claro. Llego a las 8 con los materiales.', TRUE),  -- id 2
    (1, 4, 'Perfecto, te espero.', TRUE),  -- id 3
    (2, 12, 'Buenas don Luis, los ventiladores son de 3 o de 5 aspas?', TRUE),  -- id 4
    (2, 7, 'Son de 5 aspas y tienen luz.', TRUE),  -- id 5
    (3, 6, 'Luz Marina, el apartamento tiene dos banos y balcon.', TRUE),  -- id 6
    (3, 15, 'Listo senora Paola, llevo mis implementos.', TRUE),  -- id 7
    (4, 9, 'Wilmer, la pintura ya esta en la porteria.', TRUE),  -- id 8
    (4, 14, 'Gracias don Hernan, empiezo el lunes a las 7.', TRUE),  -- id 9
    (5, 16, 'Doctora, los aires son inverter?', TRUE),  -- id 10
    (5, 4, 'Si, son inverter de 12000 BTU.', TRUE),  -- id 11
    (6, 5, 'Jesus, la obra queda en la Calle 30 con Carrera 19 de Soledad.', TRUE),  -- id 12
    (6, 17, 'Entendido, salgo a las 6 de la ferreteria.', TRUE),  -- id 13
    (7, 8, 'Julian, el repetidor lo compro yo o lo traes?', TRUE),  -- id 14
    (7, 19, 'Yo lo llevo, le mando la foto de la factura.', TRUE),  -- id 15
    (8, 10, 'Wilmer, puedes venir antes del mediodia?', TRUE),  -- id 16
    (8, 14, 'Si senora, llego a las 8.', TRUE),  -- id 17
    (9, 6, 'Sandra, te dejo la lista de medicamentos pegada en la nevera.', TRUE),  -- id 18
    (9, 18, 'Muy bien, cualquier cosa le escribo.', TRUE),  -- id 19
    (10, 11, 'Andrea, los temas son ecuaciones y funciones.', TRUE),  -- id 20
    (10, 20, 'Perfecto, preparo guias de ejercicios.', TRUE),  -- id 21
    (11, 12, 'Don Hernan, ese dia hay que cortar la luz de las zonas comunes.', TRUE),  -- id 22
    (11, 9, 'Listo, ya avise a los residentes.', FALSE),  -- id 23
    (12, 13, 'Don Luis, ya tiene el calentador comprado?', TRUE),  -- id 24
    (12, 7, 'Si, es uno de 10 litros a gas natural.', FALSE),  -- id 25
    (13, 11, 'Jesus, el salon abre a la 1 de la tarde.', TRUE),  -- id 26
    (13, 17, 'Ok, llego a las 2 con las mesas.', FALSE),  -- id 27
    (14, 15, 'Doctora, el consultorio lo dejan abierto o recojo la llave?', FALSE),  -- id 28
    (15, 16, 'Don Ricardo, el aire ya esta en la oficina?', TRUE),  -- id 29
    (15, 5, 'Llega el jueves del proveedor.', FALSE),  -- id 30
    (16, 8, 'Andrea, las clases pueden ser martes y jueves?', TRUE),  -- id 31
    (16, 20, 'Si senora, de 4 a 6 de la tarde.', FALSE),  -- id 32
    (17, 19, 'Senora Camila, le mando la cotizacion de las camaras.', TRUE),  -- id 33
    (17, 10, 'Gracias, la reviso esta noche.', FALSE),  -- id 34
    (18, 15, 'Senora Paola, disculpe, tuve una calamidad familiar y no puedo ir.', TRUE),  -- id 35
    (18, 6, 'Tranquila, espero que todo este bien.', TRUE),  -- id 36
    (19, 5, 'Yesid, necesito el local pintado antes, voy a buscar a otra persona.', TRUE),  -- id 37
    (19, 13, 'Entiendo don Ricardo, quedo atento.', TRUE),  -- id 38
    (20, 7, 'Jesus, ya estoy esperando, vas a venir?', TRUE),  -- id 39
    (20, 7, 'Como no llegaste voy a cancelar la mudanza.', FALSE);  -- id 40

-- NOTIFICACIONES
INSERT INTO notificaciones (id_usuario, tipo, titulo, contenido, id_referencia, leida) VALUES
    (13, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Reparar fuga en el lavaplatos', 1, TRUE),
    (12, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Instalar ventiladores de techo', 2, TRUE),
    (15, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Limpieza profunda de apartamento', 3, TRUE),
    (14, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Pintar fachada del edificio', 4, TRUE),
    (16, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Mantenimiento de 2 aires acondicionados', 5, TRUE),
    (17, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Transporte de materiales a una obra en Soledad', 6, TRUE),
    (19, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Configurar red wifi y revisar computador', 7, TRUE),
    (14, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Arreglar puerta del bano y closet', 8, TRUE),
    (18, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Cuidado de adulto mayor un fin de semana', 9, TRUE),
    (20, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Clases de refuerzo de matematicas', 10, TRUE),
    (12, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Cambiar tablero electrico de zonas comunes', 11, FALSE),
    (13, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Instalar calentador de agua a gas', 12, FALSE),
    (17, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Apoyo logistico en fiesta de 15 anos', 13, FALSE),
    (15, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Limpieza semanal del consultorio', 14, FALSE),
    (16, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Instalar aire acondicionado en la oficina', 15, FALSE),
    (20, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Clases de ingles para nina de 10 anos', 16, FALSE),
    (19, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Instalar camaras de seguridad en la panaderia', 17, FALSE),
    (15, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Poda de arboles del patio', 18, TRUE),
    (13, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Pintar local comercial', 19, TRUE),
    (17, 'oferta_aceptada', 'Tu oferta fue aceptada', 'Fuiste contratado para: Mudanza de apartamento a casa', 20, TRUE),
    (13, 'contratacion_finalizada', 'Trabajo finalizado', 'El trabajo fue finalizado. Ya puedes calificar al cliente.', 1, TRUE),
    (12, 'contratacion_finalizada', 'Trabajo finalizado', 'El trabajo fue finalizado. Ya puedes calificar al cliente.', 2, TRUE),
    (15, 'contratacion_finalizada', 'Trabajo finalizado', 'El trabajo fue finalizado. Ya puedes calificar al cliente.', 3, TRUE),
    (14, 'contratacion_finalizada', 'Trabajo finalizado', 'El trabajo fue finalizado. Ya puedes calificar al cliente.', 4, TRUE),
    (16, 'contratacion_finalizada', 'Trabajo finalizado', 'El trabajo fue finalizado. Ya puedes calificar al cliente.', 5, TRUE),
    (17, 'contratacion_finalizada', 'Trabajo finalizado', 'El trabajo fue finalizado. Ya puedes calificar al cliente.', 6, TRUE),
    (19, 'contratacion_finalizada', 'Trabajo finalizado', 'El trabajo fue finalizado. Ya puedes calificar al cliente.', 7, TRUE),
    (14, 'contratacion_finalizada', 'Trabajo finalizado', 'El trabajo fue finalizado. Ya puedes calificar al cliente.', 8, TRUE),
    (18, 'contratacion_finalizada', 'Trabajo finalizado', 'El trabajo fue finalizado. Ya puedes calificar al cliente.', 9, TRUE),
    (20, 'contratacion_finalizada', 'Trabajo finalizado', 'El trabajo fue finalizado. Ya puedes calificar al cliente.', 10, TRUE),
    (6, 'contratacion_cancelada', 'Contratacion cancelada', 'La contratacion fue cancelada.', 18, TRUE),
    (13, 'contratacion_cancelada', 'Contratacion cancelada', 'La contratacion fue cancelada.', 19, TRUE),
    (17, 'contratacion_cancelada', 'Contratacion cancelada', 'La contratacion fue cancelada.', 20, FALSE),
    (11, 'verificacion', 'Verificacion rechazada', 'La selfie esta borrosa. Sube una foto nueva con buena luz.', NULL, TRUE),
    (17, 'reporte', 'Advertencia por incumplimiento', 'Recibimos un reporte por no asistir a una mudanza. Si se repite, la cuenta sera suspendida.', NULL, FALSE),
    (4, 'sistema', 'Bienvenida a InWork', 'Tu identidad fue verificada. Ya puedes publicar trabajos.', NULL, TRUE);

-- REPORTES
INSERT INTO reportes (id_reportante, id_reportado, id_trabajo, motivo, descripcion, estado_reporte, id_admin_revisor, resolucion, fecha_resolucion) VALUES
    (7, 17, 20, 'incumplimiento', 'Acepto la mudanza y no llego el dia acordado. Tampoco contesto el telefono.', 'resuelto', 2, 'Se advirtio al trabajador. Si se repite se suspende la cuenta.', CURRENT_TIMESTAMP - INTERVAL '1 days'),  -- id 1
    (10, 14, 8, 'incumplimiento', 'El closet quedo rozando y no volvio a revisarlo.', 'rechazado', 2, 'El trabajo se finalizo y fue calificado. Se recomienda acordar una revision directamente.', CURRENT_TIMESTAMP - INTERVAL '6 days'),  -- id 2
    (13, 5, 19, 'otro', 'El cliente cancelo cuando yo ya habia comprado la pintura.', 'en_revision', 2, NULL, NULL),  -- id 3
    (17, 5, 6, 'otro', 'Me hicieron esperar casi dos horas para cargar el camion.', 'pendiente', NULL, NULL, NULL),  -- id 4
    (7, 19, 2, 'lenguaje_inapropiado', 'Cuando rechace su oferta me escribio de forma grosera por WhatsApp.', 'resuelto', 1, 'Se hablo con el usuario y se dejo una advertencia en su cuenta.', CURRENT_TIMESTAMP - INTERVAL '20 days'),  -- id 5
    (5, 17, 24, 'fraude', 'Me pide el 50% por adelantado por fuera de la plataforma.', 'pendiente', NULL, NULL, NULL),  -- id 6
    (13, 9, 4, 'otro', 'Publico el trabajo con un precio y despues pidio rebaja por chat.', 'rechazado', 2, 'Negociar el precio esta permitido antes de aceptar la oferta.', CURRENT_TIMESTAMP - INTERVAL '18 days'),  -- id 7
    (18, 4, 14, 'otro', 'Me pidio ir a ver el consultorio y despues rechazo mi oferta.', 'pendiente', NULL, NULL, NULL),  -- id 8
    (12, 19, 17, 'suplantacion', 'Usa en su perfil fotos de instalaciones que hice yo.', 'en_revision', 2, NULL, NULL),  -- id 9
    (4, 12, 23, 'otro', 'Retiro la oferta el mismo dia que le confirme la visita.', 'rechazado', 2, 'Retirar una oferta pendiente esta permitido.', CURRENT_TIMESTAMP - INTERVAL '2 days');  -- id 10

-- ADJUNTOS
INSERT INTO adjuntos (tipo_entidad, id_entidad, id_subido_por, url, tipo_mime) VALUES
    ('trabajo', 1, 4, 'https://storage.inwork.com.co/trabajos/1/fuga_lavaplatos.jpg', 'image/jpeg'),
    ('trabajo', 4, 9, 'https://storage.inwork.com.co/trabajos/4/fachada_edificio.jpg', 'image/jpeg'),
    ('trabajo', 11, 9, 'https://storage.inwork.com.co/trabajos/11/tablero_electrico.jpg', 'image/jpeg'),
    ('trabajo', 15, 5, 'https://storage.inwork.com.co/trabajos/15/ficha_tecnica_aire.pdf', 'application/pdf'),
    ('trabajo', 18, 6, 'https://storage.inwork.com.co/trabajos/18/arboles_patio.jpg', 'image/jpeg'),
    ('trabajo', 25, 8, 'https://storage.inwork.com.co/trabajos/25/goteras_techo.jpg', 'image/jpeg'),
    ('mensaje', 15, 19, 'https://storage.inwork.com.co/mensajes/15/factura_repetidor.jpg', 'image/jpeg'),
    ('mensaje', 33, 19, 'https://storage.inwork.com.co/mensajes/33/cotizacion_camaras.pdf', 'application/pdf'),
    ('reporte', 1, 7, 'https://storage.inwork.com.co/reportes/1/llamadas_sin_respuesta.png', 'image/png'),
    ('reporte', 6, 5, 'https://storage.inwork.com.co/reportes/6/chat_pago_por_fuera.png', 'image/png');

-- DISPOSITIVOS (para notificaciones push)
INSERT INTO dispositivos (id_usuario, token_push, plataforma) VALUES
    (1, 'Nhf78hJacxjPWi4kF_NHbj:APA91btqO7cunmn89Uqj_bJF_xIpvIRkiHTcM4U5eCET9J', 'web'),
    (4, 'xsmAKqYmwuL23QNt2xVNyy:APA91bwZd9UoV6EybesYlnyDJNG232PfQE7X7ESgOeGK_Y', 'android'),
    (6, 'goaoIqRRQqrELZBR_LyxyZ:APA91bVCLqgoxfin1Mu3loWmtTgGH0ganEGY6D8oFaX8Rc', 'ios'),
    (7, 'Jqywfktk6SkdLwDcP0qo1Y:APA91b1u-boeKaZpVpXlde0gXImO_eWwhXToABH43VZcAr', 'android'),
    (9, 'E2s0Yd0B34TbvOguwNN9uK:APA91bqGCCuluHW0YsqSomyshbUDFhZiNUB5A2okrTmrad', 'android'),
    (12, 'KqLwXV0Ywt2PlS6Rzxkq3p:APA91bmex5PTaTTUwjbFIp75eNKqhFYRNTMucJOE5nxu7D', 'android'),
    (13, 'ZjzEj3fw4bBmkGwxhg7_Qy:APA91b5IBkYohElHfNa0QdVHQzcQ_d2iUBskwx3_VpgjMz', 'android'),
    (15, 'Ri7ah3akxNcSsRUDlrHLtM:APA91bmaHD6cM3Gk0p70DhhrUQUfKvNiwgJH6dS66P2urn', 'android'),
    (16, 'A8R7yjnHy0AHE0GdgvEedY:APA91blwnWRfenO0r7dRz2kbVVFeJqc1dtpiZvMIJJRA1w', 'ios'),
    (19, 'm6e3hDNA4fAmIVWJaf_vbq:APA91bgiOqlJzRPOwIsG1_ajMjzOAR9lfUfyqco7jUyF-A', 'web');

-- TOKENS DE USUARIO (se guarda el hash, nunca el token real)
INSERT INTO tokens_usuario (id_usuario, tipo, token_hash, expira, usado) VALUES
    (11, 'verificacion_correo', '97e97bddf8fe091ddb905d3d955fe053974defdac5cdd004097b5a68eea7cb7f', CURRENT_TIMESTAMP + INTERVAL '1 day', FALSE),
    (7, 'recuperar_password', '1a7018ce912ce5ea1ab77de7480858babda1c2739665f171b790f5a36ea7863a', CURRENT_TIMESTAMP - INTERVAL '10 days', TRUE),
    (18, 'recuperar_password', '44292c67a2be798b0ebc250344427089297f61bdec2133377d8f7db4e8cd2a2d', CURRENT_TIMESTAMP + INTERVAL '30 minutes', FALSE),
    (1, 'refresh', '328c132401bb16c5501236f785dcf8d67c9b7b1c81d65c05ba57f3789effa814', CURRENT_TIMESTAMP + INTERVAL '30 days', FALSE),
    (2, 'refresh', '4980040877be9b1de193271839bd9ba7d80692fc665a981c8dc7fff3e5756d2a', CURRENT_TIMESTAMP + INTERVAL '30 days', FALSE),
    (4, 'refresh', '5fd23d4b4ed5e1f6fc9564a82b3400afaa7417dbfbcb8b15df596519cf26904a', CURRENT_TIMESTAMP + INTERVAL '30 days', FALSE),
    (9, 'refresh', '1a0d31d79f6bc979fcf4c49717970bb88b101fd58d1df03e1aacc2a24fc63766', CURRENT_TIMESTAMP + INTERVAL '30 days', FALSE),
    (12, 'refresh', '37d7e33f9f5618af8a562fa3da8eb2238dc827618925355ad1818ffa060e08bc', CURRENT_TIMESTAMP + INTERVAL '30 days', FALSE),
    (19, 'refresh', '9d3764248bc39095a97ef521eac401d8e9ba6f5fdfb1af775467758e771443d8', CURRENT_TIMESTAMP + INTERVAL '30 days', FALSE),
    (5, 'refresh', 'd4893cfdc950fd8ad40e5317b6ffad074ac474161794f7536b945d0aba05bfc1', CURRENT_TIMESTAMP - INTERVAL '2 days', TRUE);

-- AUDITORIA
INSERT INTO auditoria (id_usuario, tabla, id_registro, accion) VALUES
    (4, 'contrataciones', 1, 'INSERT'),
    (4, 'contrataciones', 1, 'UPDATE'),
    (7, 'contrataciones', 2, 'INSERT'),
    (9, 'contrataciones', 4, 'INSERT'),
    (15, 'contrataciones', 18, 'UPDATE'),
    (5, 'contrataciones', 19, 'UPDATE'),
    (7, 'contrataciones', 20, 'UPDATE'),
    (1, 'usuarios', 3, 'UPDATE'),
    (2, 'reportes', 1, 'UPDATE'),
    (1, 'categorias', 10, 'INSERT');

