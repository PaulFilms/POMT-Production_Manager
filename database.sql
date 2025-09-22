CREATE TABLE "usuarios" (
	"id"	TEXT NOT NULL UNIQUE,
	"nombre"	TEXT,
	"apellidos"	TEXT,
	"mail"	TEXT,
	"info"	TEXT,
	"password"	TEXT,
	"DB"	BLOB DEFAULT '{}',
	"firm"	TEXT,
	PRIMARY KEY("id")
)

CREATE TABLE "business_unit" (
	"id"	TEXT NOT NULL UNIQUE,
	"info"	TEXT NOT NULL,
	"DB"	BLOB DEFAULT '{}',
	"firm"	TEXT,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "pedidos" (
	"id"	TEXT NOT NULL UNIQUE,
	"info"	TEXT,
	"bu_id"	TEXT,
	"contraseña"	TEXT,
	"planificador"	TEXT,
	"fecha_ini"	TEXT DEFAULT '2025-09-16',
	"fecha_fin"	TEXT DEFAULT '2025-09-16',
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
	"fecha_ini"	TEXT DEFAULT '2025-09-16',
	"fecha_fin"	TEXT DEFAULT '2025-09-16',
	"responsable"	TEXT,
	"alarma"	INTEGER DEFAULT 0,
	"estado"	INTEGER DEFAULT 0,
	"DB"	BLOB DEFAULT '{}',
	"firm"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("pedido_id") REFERENCES "pedidos"("id")
);

CREATE TABLE IF NOT EXISTS "productos" (
	"id"	TEXT NOT NULL UNIQUE,
	"modelo"	TEXT,
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

/* VIEWS
________________________________________________________________________________________________________________________________ */

DROP VIEW IF EXISTS "main"."view_pedidos";
CREATE VIEW view_pedidos AS
SELECT
	pedidos.*,
	COUNT(hitos.pedido_id) AS 'hitos'
FROM pedidos
	LEFT JOIN hitos ON pedidos.id = hitos.pedido_id
GROUP BY hitos.pedido_id;

DROP VIEW IF EXISTS "main"."view_bunit_count";
CREATE VIEW view_bunit_count AS
SELECT 
    a.id AS id,
	a.info,
    COUNT(p.id) AS total_pedidos,
	SUM(CASE WHEN p.alarma = 1 THEN 1 ELSE 0 END) AS alarma_1,
	SUM(CASE WHEN p.alarma = 2 THEN 1 ELSE 0 END) AS alarma_2,
	SUM(CASE WHEN p.alarma = 3 THEN 1 ELSE 0 END) AS alarma_3
FROM 
    business_unit a
LEFT JOIN 
    pedidos p ON p.bu_id = a.id
GROUP BY 
    a.id, a.id
ORDER BY 
    total_pedidos DESC;

DROP VIEW IF EXISTS "main"."view_pedidos_count";
CREATE VIEW view_pedidos_count AS
SELECT 
    p.*,
    COALESCE(a.total_acciones, 0) AS total_acciones,
    COALESCE(a.LM, NULL) AS LM,
    COALESCE(a.DT, NULL) AS DT,
    COALESCE(a.PL, NULL) AS PL,
    COALESCE(a.PR, NULL) AS PR,
    COALESCE(a.EM, NULL) AS EM,
	COALESCE(a.CA, NULL) AS CA
FROM 
    pedidos p
LEFT JOIN (
    SELECT 
        pedido_id,
        COUNT(*) AS total_acciones,
        MIN(CASE WHEN causa = 'LM' THEN alarma END) AS LM,
        MIN(CASE WHEN causa = 'DT' THEN alarma END) AS DT,
        MIN(CASE WHEN causa = 'PL' THEN alarma END) AS PL,
        MIN(CASE WHEN causa = 'PR' THEN alarma END) AS PR,
        MIN(CASE WHEN causa = 'EM' THEN alarma END) AS EM,
		MIN(CASE WHEN causa = 'CA' THEN alarma END) AS CA
    FROM acciones
	WHERE estado <> 4 OR estado IS NULL
    GROUP BY pedido_id
) a ON p.id = a.pedido_id
ORDER BY total_acciones DESC;

DROP VIEW IF EXISTS "main"."view_bi_hitos_top3";
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