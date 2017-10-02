CREATE MATERIALIZED VIEW person_role_export AS
  SELECT
    pp.uuid AS person_id,
    mm.id AS membership_id,
    mr.value AS role,
    mmr.confidence AS role_confidence,
    mmrss.id AS source_id
  FROM membershipperson_membershipperson AS mm
  LEFT JOIN membershipperson_membershippersonmember AS mmm
    ON mm.id = mmm.object_ref_id
  LEFT JOIN person_person AS pp
    ON mmm.value_id = pp.id
  LEFT JOIN membershipperson_membershippersonrole AS mmr
    ON mm.id = mmr.object_ref_id
  LEFT JOIN membershipperson_role AS mr
    ON mmr.value_id = mr.id
  LEFT JOIN membershipperson_membershippersonrole_sources AS mmrs
    ON mmr.id = mmrs.membershippersonrole_id
  LEFT JOIN source_source AS mmrss
    ON mmrs.source_id = mmrss.id
  GROUP BY pp.uuid, mm.id, mr.value, mmr.confidence, mmrss.id
