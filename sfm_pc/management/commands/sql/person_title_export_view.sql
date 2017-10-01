CREATE MATERIALIZED VIEW person_title_export AS
  SELECT
    pp.uuid AS person_id,
    mm.id AS membership_id,
    mmt.value AS title,
    mmt.confidence AS title_confidence,
    mmtss.id AS source_id
  FROM membershipperson_membershipperson AS mm
  LEFT JOIN membershipperson_membershippersonmember AS mmm
    ON mm.id = mmm.object_ref_id
  LEFT JOIN person_person AS pp
    ON mmm.value_id = pp.id
  LEFT JOIN membershipperson_membershippersontitle AS mmt
    ON mm.id = mmt.object_ref_id
  LEFT JOIN membershipperson_membershippersontitle_sources AS mmts
    ON mmt.id = mmts.membershippersontitle_id
  LEFT JOIN source_source AS mmtss
    ON mmts.source_id = mmtss.id
  GROUP BY pp.uuid, mm.id, mmt.value, mmt.confidence, mmtss.id
