CREATE MATERIALIZED VIEW composition AS 
  SELECT 
    cc.id,
    oop.uuid AS parent_id,
    ooc.uuid AS child_id,
    ccsd.value AS start_date,
    ccrs.value AS real_start,
    cced.value AS end_date,
    cls.value AS classification,
    ccoe.value AS open_ended
  FROM composition_composition AS cc
  LEFT JOIN composition_compositionparent AS ccp
    ON cc.id = ccp.object_ref_id
  LEFT JOIN organization_organization AS oop
    ON ccp.value_id = oop.id
  LEFT JOIN composition_compositionchild AS ccc
    ON cc.id = ccc.object_ref_id
  LEFT JOIN organization_organization AS ooc
    ON ccc.value_id = ooc.id
  LEFT JOIN composition_compositionstartdate AS ccsd
    ON cc.id = ccsd.object_ref_id
  LEFT JOIN composition_compositionrealstart AS ccrs
    ON cc.id = ccrs.object_ref_id
  LEFT JOIN composition_compositionenddate AS cced
    ON cc.id = cced.object_ref_id
  LEFT JOIN composition_compositionclassification AS ccf
    ON cc.id = ccf.object_ref_id
  LEFT JOIN composition_classification AS cls
    ON ccf.value_id = cls.id
  LEFT JOIN composition_compositionopenended AS ccoe
    ON cc.id = ccoe.object_ref_id;
CREATE UNIQUE INDEX composition_id_index ON composition (
  id, 
  parent_id, 
  child_id, 
  classification, 
  start_date, 
  real_start,
  end_date,
  open_ended
);
CREATE INDEX composition_relation_index ON composition (parent_id, child_id)
