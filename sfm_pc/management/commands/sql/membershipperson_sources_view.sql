CREATE OR REPLACE VIEW membershipperson_sources AS 
  SELECT 
    mm.id,
    pp.uuid AS member_id,
    oo.uuid AS organization_id_value,
    mmo.confidence AS organization_id_confidence,
    row_to_json(mmpss.*) AS organization_id_sources,

    mr.value AS role_value,
    mmr.confidence AS role_confidence,
    row_to_json(mmrss.*) AS role_sources,

    mmt.value AS title_value,
    mmt.confidence AS title_confidence,
    row_to_json(mmtss.*) AS title_sources,

    mmrk.value AS rank_value,
    mmk.confidence AS rank_confidence,
    row_to_json(mmrkss.*) AS rank_sources,

    mmreals.value AS real_start_value,
    mmreals.confidence AS real_start_confidence,
    row_to_json(mmrealsss.*) AS real_start_sources,

    mmre.value AS real_end_value,
    mmre.confidence AS real_end_confidence,
    row_to_json(mmress.*) AS real_end_sources,

    sc.value AS start_context_value,
    mmsc.confidence AS start_context_confidence,
    row_to_json(scss.*) AS start_context_sources,

    ec.value AS end_context_value,
    mmec.confidence AS end_context_confidence,
    row_to_json(ecss.*) AS end_context_sources,

    mmfc.value AS first_cited_value,
    mmfc.confidence AS first_cited_confidence,
    row_to_json(mmfcss.*) AS first_cited_sources,

    mmlc.value AS last_cited_value,
    mmlc.confidence AS last_cited_confidence,
    row_to_json(mmlcss.*) AS last_cited_sources
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
    ON mmp.source_id = mmpss.id
  LEFT JOIN organization_organization AS oo
    ON mmo.value_id = oo.id

  LEFT JOIN membershipperson_membershippersonrole AS mmr
    ON mm.id = mmr.object_ref_id
  LEFT JOIN membershipperson_membershippersonrole_sources AS mmrs
    ON mmr.id = mmrs.membershippersonrole_id
  LEFT JOIN source_source AS mmrss
    ON mmrs.source_id = mmrss.id
  LEFT JOIN membershipperson_role AS mr
    ON mmr.value_id = mr.id
  
  LEFT JOIN membershipperson_membershippersontitle AS mmt
    ON mm.id = mmt.object_ref_id
  LEFT JOIN membershipperson_membershippersontitle_sources AS mmts
    ON mmt.id = mmts.membershippersontitle_id
  LEFT JOIN source_source AS mmtss
    ON mmts.source_id = mmtss.id
  
  LEFT JOIN membershipperson_membershippersonrank AS mmk
    ON mm.id = mmk.object_ref_id
  LEFT JOIN membershipperson_membershippersonrank_sources AS mmrks
    ON mmk.id = mmrks.membershippersonrank_id
  LEFT JOIN membershipperson_rank AS mmrk
    ON mmk.value_id = mmrk.id
  LEFT JOIN source_source AS mmrkss
    ON mmrks.source_id = mmrkss.id
  
  LEFT JOIN membershipperson_membershippersonrealstart AS mmreals
    ON mm.id = mmreals.object_ref_id
  LEFT JOIN membershipperson_membershippersonrealstart_sources AS mmrealss
    ON mmreals.id = mmrealss.membershippersonrealstart_id
  LEFT JOIN source_source AS mmrealsss
    ON mmrealss.source_id = mmrealsss.id

  LEFT JOIN membershipperson_membershippersonrealend AS mmre
    ON mm.id = mmre.object_ref_id
  LEFT JOIN membershipperson_membershippersonrealend_sources AS mmres
    ON mmre.id = mmres.membershippersonrealend_id
  LEFT JOIN source_source AS mmress
    ON mmres.source_id = mmress.id

  LEFT JOIN membershipperson_membershippersonstartcontext AS mmsc
    ON mm.id = mmsc.object_ref_id
  LEFT JOIN membershipperson_membershippersonstartcontext_sources AS mmscs
    ON mmsc.id = mmscs.membershippersonstartcontext_id
  LEFT JOIN source_source AS scss
    ON mmscs.source_id = scss.id
  LEFT JOIN membershipperson_context AS sc
    ON mmsc.value_id = sc.id

  LEFT JOIN membershipperson_membershippersonendcontext AS mmec
    ON mm.id = mmec.object_ref_id
  LEFT JOIN membershipperson_membershippersonendcontext_sources AS mmecs
    ON mmec.id = mmecs.membershippersonendcontext_id
  LEFT JOIN source_source AS ecss
    ON mmecs.source_id = ecss.id
  LEFT JOIN membershipperson_context AS ec
    ON mmec.value_id = ec.id

  LEFT JOIN membershipperson_membershippersonfirstciteddate AS mmfc
    ON mm.id = mmfc.object_ref_id
  LEFT JOIN membershipperson_membershippersonfirstciteddate_sources AS mmfcs
    ON mmfc.id = mmfcs.membershippersonfirstciteddate_id
  LEFT JOIN source_source AS mmfcss
    ON mmfcs.source_id = mmfcss.id

  LEFT JOIN membershipperson_membershippersonlastciteddate AS mmlc
    ON mm.id = mmlc.object_ref_id
  LEFT JOIN membershipperson_membershippersonlastciteddate_sources AS mmlcs
    ON mmlc.id = mmlcs.membershippersonlastciteddate_id
  LEFT JOIN source_source AS mmlcss
    ON mmlcs.source_id = mmlcss.id
