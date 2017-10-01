CREATE MATERIALIZED VIEW person_rank_export AS
  SELECT
    pp.uuid AS person_id,
    mm.id AS membership_id,
    mmrk.value AS rank,
    mmk.confidence AS rank_confidence,
    mmrkss.id AS source_id
  FROM membershipperson_membershipperson AS mm
  LEFT JOIN membershipperson_membershippersonmember AS mmm
    ON mm.id = mmm.object_ref_id
  LEFT JOIN person_person AS pp
    ON mmm.value_id = pp.id
  LEFT JOIN membershipperson_membershippersonrank AS mmk
    ON mm.id = mmk.object_ref_id
  LEFT JOIN membershipperson_membershippersonrank_sources AS mmrks
    ON mmk.id = mmrks.membershippersonrank_id
  LEFT JOIN membershipperson_rank AS mmrk
    ON mmk.value_id = mmrk.id
  LEFT JOIN source_source AS mmrkss
    ON mmrks.source_id = mmrkss.id
  GROUP BY pp.uuid, mm.id, mmrk.value, mmk.confidence, mmrkss.id
