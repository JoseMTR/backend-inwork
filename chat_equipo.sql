-- =====================================================================
-- CHAT DEL EQUIPO (panel de administracion, tiempo real con WebSocket)
-- Conversacion grupal entre Administrador, Moderador y Analista.
-- Es aparte de las tablas chat / mensajes, que son las conversaciones
-- entre un cliente y un trabajador sobre un trabajo.
--
-- Corre este archivo UNA vez en la base de datos que ya tienes
-- (local y Neon). En una base nueva ya viene incluido al final de DB.sql.
-- =====================================================================

CREATE TABLE IF NOT EXISTS mensajes_equipo (
    id_mensaje_equipo SERIAL PRIMARY KEY,

    id_remitente INTEGER NOT NULL,
    mensaje TEXT NOT NULL,

    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_mensaje_equipo_usuario
        FOREIGN KEY (id_remitente) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,

    CONSTRAINT chk_mensaje_equipo_texto
        CHECK (length(trim(mensaje)) BETWEEN 1 AND 1000)
);

CREATE INDEX IF NOT EXISTS idx_mensajes_equipo_created ON mensajes_equipo(created);

-- Fecha de modificacion automatica (igual que las demas tablas)
DROP TRIGGER IF EXISTS trg_mensajes_equipo_updated ON mensajes_equipo;
CREATE TRIGGER trg_mensajes_equipo_updated
BEFORE UPDATE ON mensajes_equipo
FOR EACH ROW EXECUTE FUNCTION fn_set_updated();

-- Solo el equipo del panel (roles 1, 2 y 3) puede escribir en este chat
CREATE OR REPLACE FUNCTION fn_validar_mensaje_equipo()
RETURNS TRIGGER AS $$
DECLARE
    v_rol INTEGER;
BEGIN
    SELECT id_rol INTO v_rol FROM usuarios WHERE id_usuario = NEW.id_remitente;
    IF v_rol IS NULL OR v_rol NOT IN (1, 2, 3) THEN
        RAISE EXCEPTION 'Solo administradores, moderadores y analistas pueden escribir en el chat del equipo';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_mensajes_equipo_validar ON mensajes_equipo;
CREATE TRIGGER trg_mensajes_equipo_validar
BEFORE INSERT ON mensajes_equipo
FOR EACH ROW EXECUTE FUNCTION fn_validar_mensaje_equipo();

-- Mensajes de prueba (1 Sebastian - Administrador, 2 Mariana - Moderadora, 3 Jorge Luis - Analista)
INSERT INTO mensajes_equipo (id_remitente, mensaje, created) VALUES
    (1, 'Buenos dias equipo. Hoy hay que revisar los reportes pendientes.', CURRENT_TIMESTAMP - INTERVAL '2 hours'),
    (2, 'Listo, ya estoy con los reportes y las verificaciones de identidad.', CURRENT_TIMESTAMP - INTERVAL '1 hour 50 minutes'),
    (3, 'Les paso el informe de la semana en la tarde.', CURRENT_TIMESTAMP - INTERVAL '1 hour 30 minutes');
