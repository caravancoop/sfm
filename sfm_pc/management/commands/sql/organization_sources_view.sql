CREATE OR REPLACE VIEW organization_sources AS 
  SELECT 
    oo.uuid AS id,
    oon.value AS name_value,
    oon.confidence AS name_confidence,
    row_to_json(oonss.*) AS name_source,
    oa.value AS alias_value,
    ooa.confidence AS alias_confidence,
    row_to_json(ooass.*) AS alias_source,
    oc.value AS classification_value,
    ooc.confidence AS classification_confidence,
    row_to_json(oocss.*) AS classification_source,
    ood.value AS division_id
  FROM organization_organization AS oo
  LEFT JOIN organization_organizationname AS oon
    ON oo.id = oon.object_ref_id
  LEFT JOIN organization_organizationname_sources AS oons
    ON oon.id = oons.organizationname_id
  LEFT JOIN source_source AS oonss
    ON oons.source_id = oonss.id
  LEFT JOIN organization_organizationalias AS ooa
    ON oo.id = ooa.object_ref_id
  LEFT JOIN organization_alias AS oa
    ON ooa.value_id = oa.id
  LEFT JOIN organization_organizationalias_sources AS ooas
    ON ooa.id = ooas.organizationalias_id
  LEFT JOIN source_source AS ooass
    ON ooas.source_id = ooass.id
  LEFT JOIN organization_organizationclassification AS ooc
    ON oo.id = ooc.object_ref_id
  LEFT JOIN organization_classification AS oc
    ON ooc.value_id = oc.id
  LEFT JOIN organization_organizationclassification_sources AS oocs
    ON ooc.id = oocs.organizationclassification_id
  LEFT JOIN source_source AS oocss
    ON oocs.source_id = oocss.id
  LEFT JOIN organization_organizationdivisionid AS ood
    ON oo.id = ood.object_ref_id