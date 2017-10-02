CREATE MATERIALIZED VIEW organization_classification_export AS
  SELECT
    oo.uuid AS organization_id,
    oc.value AS classification,
    ooc.confidence AS classification_confidence,
    oocss.id AS source_id
  FROM organization_organization AS oo
  LEFT JOIN organization_organizationclassification AS ooc
    ON oo.id = ooc.object_ref_id
  LEFT JOIN organization_classification AS oc
    ON ooc.value_id = oc.id
  LEFT JOIN organization_organizationclassification_sources AS oocs
    ON ooc.id = oocs.organizationclassification_id
  LEFT JOIN source_source AS oocss
    ON oocs.source_id = oocss.id
  GROUP BY oo.uuid, oc.value, ooc.confidence, oocss.id
