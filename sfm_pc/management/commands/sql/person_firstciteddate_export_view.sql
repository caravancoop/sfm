CREATE MATERIALIZED VIEW person_firstciteddate_export AS
  SELECT
    pp.uuid AS person_id,
    mm.id AS membership_id,
    mmfc.value AS first_cited_date,
    mmrs.value AS real_start_date,
    mmfc.confidence AS first_cited_date_confidence,
    mmfcss.id AS source_id
  FROM membershipperson_membershipperson AS mm
  LEFT JOIN membershipperson_membershippersonmember AS mmm
    ON mm.id = mmm.object_ref_id
  LEFT JOIN person_person AS pp
    ON mmm.value_id = pp.id
  LEFT JOIN membershipperson_membershippersonfirstciteddate AS mmfc
    ON mm.id = mmfc.object_ref_id
  LEFT JOIN membershipperson_membershippersonrealstart AS mmrs
    ON mm.id = mmrs.object_ref_id
  LEFT JOIN membershipperson_membershippersonfirstciteddate_sources AS mmfcs
    ON mmfc.id = mmfcs.membershippersonfirstciteddate_id
  LEFT JOIN source_source AS mmfcss
    ON mmfcs.source_id = mmfcss.uuid
  GROUP BY mm.id, pp.uuid, mmfc.value, mmrs.value, mmfc.confidence, mmfcss.id
