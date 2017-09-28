CREATE MATERIALIZED VIEW area AS 
  SELECT 
    aa.id,
    aan.value AS name,
    ac.value AS code,
    aag.value AS osmname,
    aagi.value AS osmid,
    aagm.value AS geometry,
    aad.value AS division_id
  FROM area_area AS aa
  LEFT JOIN area_areaname AS aan
    ON aa.id = aan.object_ref_id
  LEFT JOIN area_areacode AS aac
    ON aa.id = aac.object_ref_id
  LEFT JOIN area_code AS ac
    ON aac.value_id = ac.id
  LEFT JOIN area_areaosmname AS aag
    ON aa.id = aag.object_ref_id
  LEFT JOIN area_areaosmid AS aagi
    ON aa.id = aagi.object_ref_id
  LEFT JOIN area_areageometry AS aagm
    ON aa.id = aagm.object_ref_id
  LEFT JOIN area_areadivisionid AS aad
    ON aa.id = aad.object_ref_id;
CREATE UNIQUE INDEX area_id_index ON area (id)
