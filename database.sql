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
	"fecha_fin"	TEXT DEFAULT '2026-01-01',
	"alarma"	INTEGER,
	"DB"	BLOB DEFAULT '{"modificaciones": []}',
	"firm"	TEXT,
	PRIMARY KEY("id")
);

CREATE TABLE IF NOT EXISTS "hitos" (
	"id"	INTEGER NOT NULL UNIQUE,
	"pedido_id"	TEXT NOT NULL,
	"grupo"	TEXT,
	"nombre"	TEXT NOT NULL,
	"fecha_req"	TEXT DEFAULT '2025-01-01',
	"fecha_plan"	TEXT DEFAULT '2025-01-01',
	"departamento"	TEXT,
	"responsable"	TEXT,
	"alarma"	INTEGER DEFAULT 0,
	"estado"	INTEGER DEFAULT 0,
	"info"	TEXT,
	"DB"	BLOB DEFAULT '{"modificaciones": []}',
	"firm"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("pedido_id") REFERENCES "pedidos"("id")
);

CREATE TABLE IF NOT EXISTS "acciones" (
	"id"	INTEGER NOT NULL UNIQUE,
	"pedido_id"	TEXT NOT NULL,
	"hito_id"	INTEGER NOT NULL,
	"causa"	TEXT NOT NULL,
	"alarma"	INTEGER,
	"info"	TEXT,
	"accion"	TEXT,
	"planificador"	TEXT,
	"responsable"	TEXT,
	"fecha_accion"	TEXT DEFAULT '2025-01-01',
	"fecha_req"	INTEGER DEFAULT '2025-01-01',
	"estado"	INTEGER DEFAULT 1,
	"DB"	BLOB DEFAULT '{"modificaciones": []}',
	"firm"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
	-- FOREIGN KEY("hito_id") REFERENCES "hitos"("id")
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



/* ETL
________________________________________________________________________________________________________________________________ */

DROP TABLE IF EXISTS "main"."csv_grafos";
DROP TABLE IF EXISTS "main"."csv_pde_files";

-- DROP TABLE IF EXISTS "main"."csv_grafos";
CREATE TABLE IF NOT EXISTS csv_grafos (
    "PROYECTO"           TEXT, 
    "DESC PROYECTO"      TEXT, 
    "OPERACIÓN"          TEXT, 
    "DESCRIPCIÓN ORDEN"  TEXT, 
    "CENTRO"             TEXT, 
    "ELEMENTO PEP"       TEXT, 
    "FECHA APERTURA"     TEXT, 
    "RTGP/ PI"           TEXT, 
    "COMENTARIOS"        TEXT, 
    "DESCRIPCIÓN"        TEXT, 
    "IP"                 TEXT, 
    "Grafos_Operación"   TEXT, 
    "PI"                 TEXT, 
    "Grafo"              TEXT, 
    "Sistema"            TEXT, 
    PRIMARY KEY("ELEMENTO PEP")
);

-- DROP TABLE IF EXISTS "main"."csv_pde_files";
CREATE TABLE IF NOT EXISTS "csv_pde_files" (
	"Archivo" TEXT,
	"Ruta" TEXT,
	"Actualizar Automaticamente?" TEXT,
	"Actualizado" TEXT,
	"Actualizado por" TEXT,
	"Proyecto" TEXT,
	"Arbol" TEXT,
	"PEP" TEXT,
	"Fecha Necesidad" TEXT,
	"Fecha Entrega" TEXT,
	"Retraso (días naturales)" TEXT,
	"Material Crítico" TEXT,
	"Descripcion" TEXT,
	"Estado MD4C" TEXT,
	"Orden" TEXT,
	"Unnamed: 15" TEXT,
	"TIMELINE" TEXT
)

-- DROP TABLE IF EXISTS "main"."csv_pde_items";
CREATE TABLE IF NOT EXISTS "csv_pde_items" (
        "filename" TEXT,
        "Parentesco" TEXT,
        "Fila con el elemento Padre" TEXT,
        "NIVEL" TEXT,
        "CODIGO" TEXT,
        "NOMBRE" TEXT,
        "EC" TEXT,
        "Cl. Aprov." TEXT,
        "MAKE / BUY" TEXT,
        "Planificador" TEXT,
        "Grupo Planificador" TEXT,
        "Cant." TEXT,
        "Uds." TEXT,
        "T.Trat EM" TEXT,
        "Plazo Entrega Prev" TEXT,
        "Tiempo Fab. Propia" TEXT,
        "LT SAP" TEXT,
        "LT OP. (Manual)" TEXT,
        "Ini. Oper. ASAP" TEXT,
        "Fin. Oper. ASAP" TEXT,
        "Ini. Oper. ALAP" TEXT,
        "Fin. Oper. ALAP" TEXT,
        "Centro" TEXT,
        "GPI" TEXT,
        "Hito" TEXT,
        "Grafo" TEXT,
        "Orden 1ºNivel" TEXT,
        "Tipo" TEXT,
        "Elem. PEP" TEXT,
        "Stc. Proy." TEXT,
        "Stc. Centro" TEXT,
        "Uds..1" TEXT,
        "Estado MD4C" TEXT,
        "Orden" TEXT,
        "Ctd. Nec." TEXT,
        "SolPed" TEXT,
        "Pedido" TEXT,
        "Fecha Entrega" TEXT,
        "Fecha Confirmada / Estadística" TEXT,
        "Ctd. Ped." TEXT,
        "Ctd. Entr." TEXT,
        "Ctd. Rest." TEXT,
        "Ctd. Según Arbol" TEXT,
        "Ctd. Nec. Para 1 sistema/s" TEXT,
        "Ctd. Nec. Acumulada Para 1 sistema/s" TEXT,
        "Ctd. Nec. Total" TEXT,
        "Pedido.1" TEXT,
        "SolPed.1" TEXT,
        "OP asociada" TEXT,
        "Ctd. Solicitada" TEXT,
        "Cant. Pedida" TEXT,
        "Ctd. Recepcionada" TEXT,
        "Ctd. por recepcionar" TEXT,
        "Ctd. por inspeccionar" TEXT,
        "Ctd. Rechazada" TEXT,
        "Ctd. Aceptada" TEXT,
        "Fecha Sol." TEXT,
        "Fecha Ped." TEXT,
        "Fe. Entrega" TEXT,
        "Fecha Confirmada / Estadística.1" TEXT,
        "Recibido" TEXT,
        "Elemento PEP" TEXT,
        "Comprador" TEXT,
        "Proveedor" TEXT,
        "Fecha Inicio" TEXT,
        "Fecha Fin" TEXT,
        "Mensaje" TEXT,
        "Fecha Nec. Inicio" TEXT,
        "Fecha Necesidad" TEXT,
        "Forzar Fecha Ini" TEXT,
        "Forzar Fecha Fin" TEXT,
        "Considerar" TEXT,
        "Comentarios" TEXT,
        "Holgura (días)" TEXT,
        "Retraso (días)" TEXT,
        "Camino Critico 1" TEXT,
        "Camino Critico 1.1" TEXT,
        "Camino Critico 3" TEXT,
        "Camino Critico 4" TEXT,
        "Camino Critico 5" TEXT,
        "Camino Critico 6" TEXT,
        "Camino Critico 7" TEXT,
        "Camino Critico 8" TEXT,
        "Camino Critico 9" TEXT,
        "Camino Critico 10" TEXT,
        "Camino Critico 11" TEXT,
        "Camino Critico 12" TEXT,
        "Camino Critico 13" TEXT,
        "Camino Critico 14" TEXT,
        "Camino Critico 15" TEXT,
        "Camino Critico 16" TEXT,
        "Camino Critico 17" TEXT,
        "Camino Critico 18" TEXT,
        "Camino Critico 19" TEXT,
        "Camino Critico 20" TEXT,
        "¿Es el hijo que mas tarde se entrega?" TEXT,
        "Camino Critico - Nivel 1 & 2" TEXT,
        "Camino Critico - Resto de niveles" TEXT,
        "Unnamed: 97" TEXT,
        "Filtro cantidad nula" TEXT,
        "Filtro previsionales de comerciales" TEXT,
        "Filtro Stock" TEXT,
        "Filtro consumibles" TEXT,
        "Filtro Caminos Criticos" TEXT,
        "Filtro Botón Arbolito" TEXT,
        "Nº Caminos Críticos" TEXT,
        "Fecha Necesidad Sistema/s" TEXT,
        "Nº Sistemas a entregar" TEXT,
        """Descartar """"Sin necesidad""""""" TEXT,
        "Descatar O.Previsionales de comerciales" TEXT,
        "Descartar Consumibles" TEXT,
        "Centros/Almacenes Descartados" TEXT,
        "Planificadores Descartados" TEXT,
        "Descartes por nombre" TEXT,
        "GPIs consideradas" TEXT,
        "Hitos Considerados" TEXT,
        "Grafos Considerados" TEXT,
        "Orden 1er Nivel Consideradas" TEXT
);



/* VIEWS
________________________________________________________________________________________________________________________________ */

DROP VIEW IF EXISTS "main"."view_pedidos";
DROP VIEW IF EXISTS "main"."view_hitos";
DROP VIEW IF EXISTS "main"."view_business_unit";
DROP VIEW IF EXISTS "main"."view_bi_hitos_top3";



-- DROP VIEW IF EXISTS "main"."view_pedidos";
CREATE VIEW IF NOT EXISTS view_pedidos AS
SELECT 
    gpi.*,

    -- Conteo de hitos (estado ≠ 4)
    COALESCE(h.total_hitos, 0) AS "∑_hitos",

    -- Conteo de acciones (estado ≠ 4)
    COALESCE(a.total_acciones, 0) AS "∑_acciones",

    -- Mínimos por causa, En caso de no tener incidencia indicamos verde
    COALESCE(a.LM, 3) AS LM,
    COALESCE(a.DT, 3) AS DT,
    COALESCE(a.PL, 3) AS PL,
    COALESCE(a.PR, 3) AS PR,
    COALESCE(a.EM, NULL) AS EM,
    COALESCE(a.CA, NULL) AS CA,
	
	-- PDE
	"Retraso (días naturales)" as pde_retraso_dias,
	"Material Crítico" as pde_material_critico,
	"Descripcion" as pde_description,
	"Actualizado" as pde_actualizado,
	"Actualizado por" as pde_usuario

FROM pedidos gpi

-- Subconsulta de hitos
LEFT JOIN (
    SELECT 
		id,
        pedido_id,
        COUNT(*) AS total_hitos
    FROM hitos
    WHERE estado <> 4 OR estado IS NULL
    GROUP BY pedido_id
) h ON gpi.id = h.pedido_id

-- Subconsulta de acciones
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
--     WHERE estado <> 4 OR estado IS NULL
    GROUP BY pedido_id
) a ON gpi.id = a.pedido_id

-- Subconsulta pde
LEFT JOIN csv_grafos gr ON gpi.id=gr."RTGP/ PI"
LEFT JOIN csv_pde_files pde ON gr."ELEMENTO PEP"=pde.PEP

ORDER BY gpi.id;



-- DROP VIEW IF EXISTS "main"."view_hitos";
CREATE VIEW view_hitos AS
SELECT 
	hitos.*,
	gpi.bu_id,
	
    -- Conteo de acciones (estado ≠ 4)
    COALESCE(a.∑_acciones, 0) AS "∑_acciones",
	json_extract(CAST(DB AS TEXT), '$.cantidad') AS cantidad,

    -- Mínimos por causa
    COALESCE(a.LM, 3) AS LM,
    COALESCE(a.DT, 3) AS DT,
    COALESCE(a.PL, 3) AS PL,
    COALESCE(a.PR, 3) AS PR,
    COALESCE(a.EM, NULL) AS EM,
    COALESCE(a.CA, NULL) AS CA
FROM hitos

LEFT JOIN (
	SELECT
		id,
		bu_id
	FROM pedidos
) gpi ON hitos.pedido_id=gpi.id

LEFT JOIN (
	SELECT
		hito_id,
		COUNT(*) AS "∑_acciones",
        MIN(CASE WHEN causa = 'LM' THEN alarma END) AS LM,
        MIN(CASE WHEN causa = 'DT' THEN alarma END) AS DT,
        MIN(CASE WHEN causa = 'PL' THEN alarma END) AS PL,
        MIN(CASE WHEN causa = 'PR' THEN alarma END) AS PR,
        MIN(CASE WHEN causa = 'EM' THEN alarma END) AS EM,
        MIN(CASE WHEN causa = 'CA' THEN alarma END) AS CA
	FROM acciones
	WHERE estado <> 4 OR estado IS NULL
	GROUP BY hito_id
) a ON hitos.id=a.hito_id

ORDER BY hitos.id



-- DROP VIEW IF EXISTS "main"."view_business_unit";
CREATE VIEW IF NOT EXISTS view_business_unit AS
SELECT 
	bu.*,
    COUNT(p.id) AS "∑_GPIs",
	SUM(CASE WHEN p.alarma = 1 THEN 1 ELSE 0 END) AS "🟥",
	SUM(CASE WHEN p.alarma = 2 THEN 1 ELSE 0 END) AS "🟨",
	SUM(CASE WHEN p.alarma = 3 THEN 1 ELSE 0 END) AS "🟩"
FROM 
    business_unit bu
LEFT JOIN 
    pedidos p ON p.bu_id = bu.id
GROUP BY 
    bu.id
ORDER BY 
    "∑_GPIs" DESC;



-- DROP VIEW IF EXISTS "main"."view_bi_hitos_top3";
CREATE VIEW IF NOT EXISTS view_bi_hitos_top3 AS
SELECT 
	hitos.*,
	b.id as bu_id,
	CAST(julianday(hitos.fecha_plan) - julianday('now') AS INTEGER) AS "Δ_dias"
FROM hitos
	INNER JOIN pedidos p ON hitos.pedido_id = p.id
	INNER JOIN business_unit b ON p.bu_id = b.id
WHERE hitos.estado <> 4
ORDER BY hitos.fecha_plan ASC
LIMIT 3;


