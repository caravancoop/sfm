CREATE MATERIALIZED VIEW membershipperson_sources AS
  SELECT
    mm.id,
    pp.uuid AS member_id,
    oo.uuid AS organization_id_value,
    MAX(mmo.confidence) AS organization_id_confidence,
    json_agg(DISTINCT mmpss.*) AS organization_id_sources,

    mr.value AS role_value,
    MAX(mmr.confidence) AS role_confidence,
    json_agg(DISTINCT mmrss.*) AS role_sources,

    mmt.value AS title_value,
    MAX(mmt.confidence) AS title_confidence,
    json_agg(DISTINCT mmtss.*) AS title_sources,

    mmrk.value AS rank_value,
    MAX(mmk.confidence) AS rank_confidence,
    json_agg(DISTINCT mmrkss.*) AS rank_sources,

    mmreals.value AS real_start_value,
    MAX(mmreals.confidence) AS real_start_confidence,
    json_agg(DISTINCT mmrealsss.*) AS real_start_sources,

    mmre.value AS real_end_value,
    MAX(mmre.confidence) AS real_end_confidence,
    json_agg(DISTINCT mmress.*) AS real_end_sources,

    mmsc.value AS start_context_value,
    MAX(mmsc.confidence) AS start_context_confidence,
    json_agg(DISTINCT scss.*) AS start_context_sources,

    mmec.value AS end_context_value,
    MAX(mmec.confidence) AS end_context_confidence,
    json_agg(DISTINCT ecss.*) AS end_context_sources,

    mmfc.value AS first_cited_value,
    MAX(mmfc.confidence) AS first_cited_confidence,
    json_agg(DISTINCT mmfcss.*) AS first_cited_sources,

    mmlc.value AS last_cited_value,
    MAX(mmlc.confidence) AS last_cited_confidence,
    json_agg(DISTINCT mmlcss.*) AS last_cited_sources
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

  LEFT JOIN membershipperson_membershippersonrole AS mmr
    ON mm.id = mmr.object_ref_id
  LEFT JOIN membershipperson_membershippersonrole_sources AS mmrs
    ON mmr.id = mmrs.membershippersonrole_id
  LEFT JOIN source_source AS mmrss
    ON mmrs.source_id = mmrss.uuid
  LEFT JOIN membershipperson_role AS mr
    ON mmr.value_id = mr.id

  LEFT JOIN membershipperson_membershippersontitle AS mmt
    ON mm.id = mmt.object_ref_id
  LEFT JOIN membershipperson_membershippersontitle_sources AS mmts
    ON mmt.id = mmts.membershippersontitle_id
  LEFT JOIN source_source AS mmtss
    ON mmts.source_id = mmtss.uuid

  LEFT JOIN membershipperson_membershippersonrank AS mmk
    ON mm.id = mmk.object_ref_id
  LEFT JOIN membershipperson_membershippersonrank_sources AS mmrks
    ON mmk.id = mmrks.membershippersonrank_id
  LEFT JOIN membershipperson_rank AS mmrk
    ON mmk.value_id = mmrk.id
  LEFT JOIN source_source AS mmrkss
    ON mmrks.source_id = mmrkss.uuid

  LEFT JOIN membershipperson_membershippersonrealstart AS mmreals
    ON mm.id = mmreals.object_ref_id
  LEFT JOIN membershipperson_membershippersonrealstart_sources AS mmrealss
    ON mmreals.id = mmrealss.membershippersonrealstart_id
  LEFT JOIN source_source AS mmrealsss
    ON mmrealss.source_id = mmrealsss.uuid

  LEFT JOIN membershipperson_membershippersonrealend AS mmre
    ON mm.id = mmre.object_ref_id
  LEFT JOIN membershipperson_membershippersonrealend_sources AS mmres
    ON mmre.id = mmres.membershippersonrealend_id
  LEFT JOIN source_source AS mmress
    ON mmres.source_id = mmress.uuid

  LEFT JOIN membershipperson_membershippersonstartcontext AS mmsc
    ON mm.id = mmsc.object_ref_id
  LEFT JOIN membershipperson_membershippersonstartcontext_sources AS mmscs
    ON mmsc.id = mmscs.membershippersonstartcontext_id
  LEFT JOIN source_source AS scss
    ON mmscs.source_id = scss.uuid

  LEFT JOIN membershipperson_membershippersonendcontext AS mmec
    ON mm.id = mmec.object_ref_id
  LEFT JOIN membershipperson_membershippersonendcontext_sources AS mmecs
    ON mmec.id = mmecs.membershippersonendcontext_id
  LEFT JOIN source_source AS ecss
    ON mmecs.source_id = ecss.uuid

  LEFT JOIN membershipperson_membershippersonfirstciteddate AS mmfc
    ON mm.id = mmfc.object_ref_id
  LEFT JOIN membershipperson_membershippersonfirstciteddate_sources AS mmfcs
    ON mmfc.id = mmfcs.membershippersonfirstciteddate_id
  LEFT JOIN source_source AS mmfcss
    ON mmfcs.source_id = mmfcss.uuid

  LEFT JOIN membershipperson_membershippersonlastciteddate AS mmlc
    ON mm.id = mmlc.object_ref_id
  LEFT JOIN membershipperson_membershippersonlastciteddate_sources AS mmlcs
    ON mmlc.id = mmlcs.membershippersonlastciteddate_id
  LEFT JOIN source_source AS mmlcss
    ON mmlcs.source_id = mmlcss.uuid
  GROUP BY mm.id,
           pp.uuid,
           oo.uuid,
           mr.value,
           mmt.value,
           mmrk.value,
           mmreals.value,
           mmre.value,
           mmsc.value,
           mmec.value,
           mmfc.value,
           mmlc.value;
CREATE UNIQUE INDEX membershipperson_src_id_idx ON membershipperson_sources (
  id,
  title_value,
  rank_value,
  start_context_value,
  end_context_value,
  first_cited_value,
  last_cited_value
)
