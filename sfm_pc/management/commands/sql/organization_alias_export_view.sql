CREATE MATERIALIZED VIEW organization_alias_export AS
  SELECT
    oo.uuid AS organization_id,
    oa.value AS alias,
    ooa.confidence AS alias_confidence,
    ooass.id AS source_id
  FROM organization_organization AS oo
  LEFT JOIN organization_organizationalias AS ooa
    ON oo.id = ooa.object_ref_id
  LEFT JOIN organization_alias AS oa
    ON ooa.value_id = oa.id
  LEFT JOIN organization_organizationalias_sources AS ooas
    ON ooa.id = ooas.organizationalias_id
  LEFT JOIN source_source AS ooass
    ON ooas.source_id = ooass.uuid
  GROUP BY oo.uuid, oa.value, ooa.confidence, ooass.id
