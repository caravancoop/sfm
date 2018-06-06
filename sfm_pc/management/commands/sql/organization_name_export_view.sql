CREATE MATERIALIZED VIEW organization_name_export AS
  SELECT
    oo.uuid AS organization_id,
    oon.value AS name,
    oon.confidence AS name_confidence,
    oonss.id AS source_id
  FROM organization_organization AS oo
  LEFT JOIN organization_organizationname AS oon
    ON oo.id = oon.object_ref_id
  LEFT JOIN organization_organizationname_sources AS oons
    ON oon.id = oons.organizationname_id
  LEFT JOIN source_source AS oonss
    ON oons.source_id = oonss.uuid
  GROUP BY oo.uuid, oon.value, oon.confidence, oonss.id
