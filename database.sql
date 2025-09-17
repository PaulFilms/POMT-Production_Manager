


/* VIEWS
________________________________________________________________________________________________________________________________ */

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