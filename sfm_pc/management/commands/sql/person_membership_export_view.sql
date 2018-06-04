CREATE MATERIALIZED VIEW person_membership_export AS
  SELECT
    mm.id AS membership_id,
    pp.uuid AS person_id,
    oo.uuid AS organization_id,
    mmo.confidence AS organization_id_confidence,
    mmpss.id AS source_id
  FROM membershipperson_membershipperson AS mm
  LEFT JOIN membershipperson_membershippersonmember AS mmm
    ON mm.id = mmm.object_ref_id
  LEFT JOIN person_person AS pp
    ON mmm.value_id = pp.id
  LEFT JOIN membershipperson_membershippersonorganization AS mmo
    ON mm.id = mmo.object_ref_id
  LEFT JOIN membershipperson_membershippersonorganization_sources AS mmp
    ON mmo.id = mmp.membershippersonorganization_id
  LEFT JOIN source_source AS mmpss
    ON mmp.source_id = mmpss.uuid
  LEFT JOIN organization_organization AS oo
    ON mmo.value_id = oo.id
  GROUP BY mm.id, pp.uuid, oo.uuid, mmo.confidence, mmpss.id
