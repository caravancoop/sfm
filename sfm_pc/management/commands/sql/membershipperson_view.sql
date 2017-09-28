CREATE MATERIALIZED VIEW membershipperson AS 
  SELECT 
    mm.id,
    pp.uuid AS member_id,
    oo.uuid AS organization_id,
    mr.value AS role,
    mmt.value AS title,
    mmrk.value AS rank,
    mmrs.value AS real_start,
    mmre.value AS real_end,
    sc.value AS start_context,
    ec.value AS end_context,
    mmfc.value AS first_cited,
    mmlc.value AS last_cited
  FROM membershipperson_membershipperson AS mm
  LEFT JOIN membershipperson_membershippersonmember AS mmm
    ON mm.id = mmm.object_ref_id
  LEFT JOIN person_person AS pp
    ON mmm.value_id = pp.id
  LEFT JOIN membershipperson_membershippersonorganization AS mmo
    ON mm.id = mmo.object_ref_id
  LEFT JOIN organization_organization AS oo
    ON mmo.value_id = oo.id
  LEFT JOIN membershipperson_membershippersonrole AS mmr
    ON mm.id = mmr.object_ref_id
  LEFT JOIN membershipperson_role AS mr
    ON mmr.value_id = mr.id
  LEFT JOIN membershipperson_membershippersontitle AS mmt
    ON mm.id = mmt.object_ref_id
  LEFT JOIN membershipperson_membershippersonrank AS mmk
    ON mm.id = mmk.object_ref_id
  LEFT JOIN membershipperson_rank AS mmrk
    ON mmk.value_id = mmrk.id
  LEFT JOIN membershipperson_membershippersonrealstart AS mmrs
    ON mm.id = mmrs.object_ref_id
  LEFT JOIN membershipperson_membershippersonrealend AS mmre
    ON mm.id = mmre.object_ref_id
  LEFT JOIN membershipperson_membershippersonstartcontext AS mmsc
    ON mm.id = mmsc.object_ref_id
  LEFT JOIN membershipperson_context AS sc
    ON mmsc.value_id = sc.id
  LEFT JOIN membershipperson_membershippersonendcontext AS mmec
    ON mm.id = mmec.object_ref_id
  LEFT JOIN membershipperson_context AS ec
    ON mmec.value_id = sc.id
  LEFT JOIN membershipperson_membershippersonfirstciteddate AS mmfc
    ON mm.id = mmfc.object_ref_id
  LEFT JOIN membershipperson_membershippersonlastciteddate AS mmlc
    ON mm.id = mmlc.object_ref_id;
CREATE UNIQUE INDEX membershipperson_id_index ON membershipperson (
  id,
  title,
  rank,
  start_context,
  end_context,
  first_cited,
  last_cited
)
