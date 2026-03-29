-- ============================================
--  HABITA - Base de Datos
--  Plataforma de renta de inmuebles en Querétaro
-- ============================================

CREATE DATABASE IF NOT EXISTS habita_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE habita_db;

-- --------------------------------------------
-- Tabla: usuarios
-- --------------------------------------------
CREATE TABLE usuarios (
  id          INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(100)    NOT NULL,
  apellido    VARCHAR(100)    NOT NULL,
  email       VARCHAR(150)    NOT NULL UNIQUE,
  telefono    VARCHAR(15),
  password    VARCHAR(255)    NOT NULL,
  rol         ENUM('arrendador','inquilino','admin') NOT NULL DEFAULT 'inquilino',
  creado_en   TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------
-- Tabla: propiedades
-- --------------------------------------------
CREATE TABLE propiedades (
  id               INT UNSIGNED     AUTO_INCREMENT PRIMARY KEY,
  usuario_id       INT UNSIGNED     NOT NULL,
  titulo           VARCHAR(150)     NOT NULL,
  descripcion      TEXT,
  tipo             ENUM('casa','habitacion','departamento') NOT NULL,
  precio_mensual   DECIMAL(10,2)    NOT NULL,
  direccion        VARCHAR(255)     NOT NULL,
  colonia          VARCHAR(100),
  municipio        VARCHAR(100)     DEFAULT 'Querétaro',
  codigo_postal    VARCHAR(10),
  habitaciones     TINYINT UNSIGNED DEFAULT 1,
  banos            TINYINT UNSIGNED DEFAULT 1,
  metros_cuadrados DECIMAL(7,2),
  amueblado        TINYINT(1)       DEFAULT 0,
  estatus          ENUM('disponible','rentada','pausada') DEFAULT 'disponible',
  creado_en        TIMESTAMP        DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_propiedad_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios(id) ON DELETE CASCADE
);

-- --------------------------------------------
-- Tabla: imagenes_propiedades
-- --------------------------------------------
CREATE TABLE imagenes_propiedades (
  id           INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
  propiedad_id INT UNSIGNED  NOT NULL,
  url_imagen   VARCHAR(255)  NOT NULL,
  es_portada   TINYINT(1)    DEFAULT 0,
  CONSTRAINT fk_imagen_propiedad FOREIGN KEY (propiedad_id)
    REFERENCES propiedades(id) ON DELETE CASCADE
);

-- --------------------------------------------
-- Tabla: solicitudes
-- --------------------------------------------
CREATE TABLE solicitudes (
  id           INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
  propiedad_id INT UNSIGNED  NOT NULL,
  inquilino_id INT UNSIGNED  NOT NULL,
  mensaje      TEXT,
  estatus      ENUM('pendiente','aceptada','rechazada') DEFAULT 'pendiente',
  creado_en    TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_solicitud_propiedad FOREIGN KEY (propiedad_id)
    REFERENCES propiedades(id) ON DELETE CASCADE,
  CONSTRAINT fk_solicitud_inquilino FOREIGN KEY (inquilino_id)
    REFERENCES usuarios(id) ON DELETE CASCADE
);

-- --------------------------------------------
-- Tabla: favoritos
-- --------------------------------------------
CREATE TABLE favoritos (
  usuario_id   INT UNSIGNED NOT NULL,
  propiedad_id INT UNSIGNED NOT NULL,
  agregado_en  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (usuario_id, propiedad_id),
  CONSTRAINT fk_favorito_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios(id) ON DELETE CASCADE,
  CONSTRAINT fk_favorito_propiedad FOREIGN KEY (propiedad_id)
    REFERENCES propiedades(id) ON DELETE CASCADE
);