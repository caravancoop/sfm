CREATE MATERIALIZED VIEW person_alias_export AS
  SELECT
    pp.uuid as person_id,
    pa.value AS alias,
    ppa.confidence AS alias_confidence,
    ppass.uuid AS source_id
  FROM person_person AS pp
  LEFT JOIN person_personalias AS ppa
    ON pp.id = ppa.object_ref_id
  LEFT JOIN person_alias AS pa
    ON ppa.value_id = pa.id
  LEFT JOIN person_personalias_sources AS ppas
    ON ppa.id = ppas.personalias_id
  LEFT JOIN source_source AS ppass
    ON ppas.source_id = ppass.uuid
  GROUP BY pp.uuid, pa.value, ppa.confidence, ppass.uuid
