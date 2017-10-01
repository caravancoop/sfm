CREATE MATERIALIZED VIEW organization_lastciteddate_export AS
  SELECT
    oo.uuid AS organization_id,
    oolcd.value AS last_cited_date,
    oooe.value AS assume_end_date,
    oolcd.confidence AS last_cited_date_confidence,
    oolcdss.id AS source_id
  FROM organization_organization AS oo
  LEFT JOIN organization_organizationlastciteddate AS oolcd
    ON oo.id = oolcd.object_ref_id
  LEFT JOIN organization_organizationopenended AS oooe
    ON oo.id = oooe.object_ref_id
  LEFT JOIN organization_organizationlastciteddate_sources AS oolcds
    ON oolcd.id = oolcds.organizationlastciteddate_id
  LEFT JOIN source_source AS oolcdss
    ON oolcds.source_id = oolcdss.id
  GROUP BY oo.uuid, oolcd.value, oooe.value, oolcd.confidence, oolcdss.id
