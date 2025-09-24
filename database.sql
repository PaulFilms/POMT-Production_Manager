CREATE TABLE IF NOT EXISTS "usuarios" (
	"id"	TEXT NOT NULL UNIQUE,
	"nombre"	TEXT,
	"apellidos"	TEXT,
	"mail"	TEXT,
	"info"	TEXT,
	"password"	TEXT,
	"DB"	BLOB DEFAULT '{}',
	"firm"	TEXT,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "departamentos" (
	"id"	TEXT NOT NULL UNIQUE,
	"info"	TEXT NOT NULL,
	"DB"	BLOB DEFAULT '{"usuario_id": []}',
	"firm"	TEXT,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "business_unit" (
	"id"	TEXT NOT NULL UNIQUE,
	"info"	TEXT NOT NULL,
	"DB"	BLOB DEFAULT '{}',
	"firm"	TEXT,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "pedidos" (
	"id"	TEXT NOT NULL UNIQUE,
	"info"	TEXT NOT NULL,
	"bu_id"	TEXT,
	"contraseña"	TEXT,
	"planificador"	TEXT,
	"fecha_ini"	TEXT DEFAULT '2025-01-01',
	"fecha_fin"	TEXT DEFAULT '2025-01-01',
	"alarma"	INTEGER,
	"DB"	BLOB DEFAULT '{}',
	"firm"	TEXT,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "hitos" (
	"id"	INTEGER NOT NULL UNIQUE,
	"pedido_id"	TEXT NOT NULL,
	"grupo"	TEXT,
	"info"	TEXT,
	"fecha_ini"	TEXT DEFAULT '2025-01-01',
	"fecha_fin"	TEXT DEFAULT '2025-01-01',
	"responsable"	TEXT,
	"alarma"	INTEGER DEFAULT 0,
	"estado"	INTEGER DEFAULT 0,
	"DB"	BLOB DEFAULT '{}',
	"firm"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("pedido_id") REFERENCES "pedidos"("id")
);

CREATE TABLE IF NOT EXISTS "acciones" (
	"id"	INTEGER NOT NULL UNIQUE,
	"pedido_id"	TEXT NOT NULL,
	"causa"	TEXT,
	"alarma"	INTEGER,
	"info"	TEXT,
	"accion"	TEXT,
	"planificador"	TEXT,
	"responsable"	TEXT,
	"fecha_accion"	TEXT DEFAULT '2025-01-01',
	"fecha_req"	INTEGER DEFAULT '2025-01-01',
	"estado"	INTEGER DEFAULT 0,
	"DB"	BLOB DEFAULT '{}',
	"firm"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("pedido_id") REFERENCES "pedidos"("id")
);

CREATE TABLE IF NOT EXISTS "empresas" (
	"id"	TEXT NOT NULL UNIQUE,
	"nombre"	TEXT NOT NULL,
	"direccion1"	TEXT,
	"direccion2"	TEXT,
	"url"	TEXT,
	"info"	TEXT,
	"DB"	BLOB DEFAULT '{}',
	"firm"	TEXT,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "productos" (
	"id"	TEXT NOT NULL UNIQUE,
	"modelo"	TEXT NOT NULL,
	"empresa_id"	TEXT,
	"tipo"	TEXT,
	"info"	TEXT,
	"url"	TEXT,
	"part_number"	TEXT,
	"sap_id"	INTEGER,
	"DB"	BLOB DEFAULT '{}',
	"firm"	TEXT,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "templates" (
	"id"	INTEGER NOT NULL UNIQUE,
	"template"	TEXT NOT NULL,
	"nombre"	TEXT NOT NULL,
	"orden"	INTEGER NOT NULL,
	"porcentage"	INTEGER NOT NULL,
	"info"	TEXT,
	PRIMARY KEY("id")
)

DROP INDEX IF EXISTS "main"."indx_templates";
CREATE INDEX "indx_templates" ON "templates" (
	"template"	ASC,
	"orden"	ASC
);

/* VIEWS
________________________________________________________________________________________________________________________________ */

DROP VIEW IF EXISTS "main"."view_pedidos";
DROP VIEW IF EXISTS "main"."view_bunit_count";
DROP VIEW IF EXISTS "main"."view_bi_hitos_top3";

-- DROP VIEW IF EXISTS "main"."view_pedidos";
CREATE VIEW view_pedidos AS
SELECT
	pedidos.*,
	COUNT(CASE WHEN hitos.pedido_id<>4 THEN 1 ELSE 0 END) AS 'hitos' -- Sin finalizados
FROM pedidos
	LEFT JOIN hitos ON pedidos.id = hitos.pedido_id
GROUP BY hitos.pedido_id;

-- DROP VIEW IF EXISTS "main"."view_bunit_count";
CREATE VIEW view_bunit_count AS
SELECT 
--  a.id AS id,
-- 	a.info,
	bu.*,
    COUNT(p.id) AS gpi,
	SUM(CASE WHEN p.alarma = 1 THEN 1 ELSE 0 END) AS 🟥,
	SUM(CASE WHEN p.alarma = 2 THEN 1 ELSE 0 END) AS 🟨,
	SUM(CASE WHEN p.alarma = 3 THEN 1 ELSE 0 END) AS 🟩
FROM 
    business_unit bu
LEFT JOIN 
    pedidos p ON p.bu_id = bu.id
GROUP BY 
    bu.id
ORDER BY 
    gpi DESC;

-- DROP VIEW IF EXISTS "main"."view_bi_hitos_top3";
CREATE VIEW view_bi_hitos_top3 AS
SELECT 
	*,
	b.id as bu_id,
	CAST(julianday(h.fecha_fin) - julianday('now') AS INTEGER) AS Δ
FROM hitos as h
	INNER JOIN pedidos p ON h.pedido_id = p.id
	INNER JOIN business_unit b ON p.bu_id = b.id
WHERE h.estado <> 4
ORDER BY h.fecha_fin ASC
LIMIT 3;

-- DROP VIEW IF EXISTS "main"."view_pedidos_count";
-- CREATE VIEW view_pedidos_count AS
-- SELECT 
--     p.*,
--     COALESCE(a.total_acciones, 0) AS total_acciones,
--     COALESCE(a.LM, NULL) AS LM,
--     COALESCE(a.DT, NULL) AS DT,
--     COALESCE(a.PL, NULL) AS PL,
--     COALESCE(a.PR, NULL) AS PR,
--     COALESCE(a.EM, NULL) AS EM,
-- 	COALESCE(a.CA, NULL) AS CA
-- FROM 
--     pedidos p
-- LEFT JOIN (
--     SELECT 
--         pedido_id,
--         COUNT(*) AS total_acciones,
--         MIN(CASE WHEN causa = 'LM' THEN alarma END) AS LM,
--         MIN(CASE WHEN causa = 'DT' THEN alarma END) AS DT,
--         MIN(CASE WHEN causa = 'PL' THEN alarma END) AS PL,
--         MIN(CASE WHEN causa = 'PR' THEN alarma END) AS PR,
--         MIN(CASE WHEN causa = 'EM' THEN alarma END) AS EM,
-- 		MIN(CASE WHEN causa = 'CA' THEN alarma END) AS CA
--     FROM acciones
-- 	WHERE estado <> 4 OR estado IS NULL
--     GROUP BY pedido_id
-- ) a ON p.id = a.pedido_id
-- ORDER BY total_acciones DESC;