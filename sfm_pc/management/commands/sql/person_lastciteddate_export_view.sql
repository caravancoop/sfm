CREATE MATERIALIZED VIEW person_lastciteddate_export AS
  SELECT
    pp.uuid AS person_id,
    mm.id AS membership_id,
    mmlc.value AS last_cited_date,
    mmre.value AS real_end_date,
    mmlc.confidence AS last_cited_date_confidence,
    mmlcss.uuid AS source_id
  FROM membershipperson_membershipperson AS mm
  LEFT JOIN membershipperson_membershippersonmember AS mmm
    ON mm.id = mmm.object_ref_id
  LEFT JOIN person_person AS pp
    ON mmm.value_id = pp.id
  LEFT JOIN membershipperson_membershippersonlastciteddate AS mmlc
    ON mm.id = mmlc.object_ref_id
  LEFT JOIN membershipperson_membershippersonrealend AS mmre
    ON mm.id = mmre.object_ref_id
  LEFT JOIN membershipperson_membershippersonlastciteddate_sources AS mmlcs
    ON mmlc.id = mmlcs.membershippersonlastciteddate_id
  LEFT JOIN source_source AS mmlcss
    ON mmlcs.source_id = mmlcss.uuid
  GROUP BY pp.uuid, mm.id, mmlc.value, mmre.value, mmlc.confidence, mmlcss.uuid
