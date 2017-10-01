CREATE MATERIALIZED VIEW organization_parent_export AS
  SELECT
    cc.id AS composition_id,
    ooc.uuid AS organization_id,
    oop.uuid AS parent_id,
    ccp.confidence AS composition_confidence,
    ccpss.id AS source_id
  FROM composition_composition AS cc
  LEFT JOIN composition_compositionparent AS ccp
    ON cc.id = ccp.object_ref_id
  LEFT JOIN organization_organization AS oop
    ON ccp.value_id = oop.id
  LEFT JOIN composition_compositionchild AS ccc
    ON cc.id = ccc.object_ref_id
  LEFT JOIN organization_organization AS ooc
    ON ccc.value_id = ooc.id
  LEFT JOIN composition_compositionparent_sources AS ccps
    ON ccp.id = ccps.compositionparent_id
  LEFT JOIN source_source AS ccpss
    ON ccps.source_id = ccpss.id
  GROUP BY cc.id, oop.uuid, ooc.uuid, ccp.confidence, ccpss.id
