CREATE MATERIALIZED VIEW organization_firstciteddate_export AS
  SELECT
    oo.uuid AS organization_id,
    oofcd.value AS first_cited_date,
    oors.value AS real_start_date,
    oofcd.confidence AS first_cited_date_confidence,
    oofcdss.id AS source_id
  FROM organization_organization AS oo
  LEFT JOIN organization_organizationfirstciteddate AS oofcd
    ON oo.id = oofcd.object_ref_id
  LEFT JOIN organization_organizationrealstart AS oors
    ON oo.id = oors.object_ref_id
  LEFT JOIN organization_organizationfirstciteddate_sources AS oofcds
    ON oofcd.id = oofcds.organizationfirstciteddate_id
  LEFT JOIN source_source AS oofcdss
    ON oofcds.source_id = oofcdss.uuid
  GROUP BY oo.uuid, oofcd.value, oors.value, oofcd.confidence, oofcdss.id
