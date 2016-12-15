CREATE MATERIALIZED VIEW membershiporganization AS 
  SELECT 
    m.id,
    mm.uuid AS member_id,
    mo.uuid AS organization_id,
    mmfc.value AS first_cited,
    mmlc.value AS last_cited
  FROM membershiporganization_membershiporganization AS m
  LEFT JOIN membershiporganization_m AS mom
    ON m.id = mom.object_ref_id
  LEFT JOIN organization_organization AS mm
    ON mom.value_id = mm.id
  LEFT JOIN membershiporganization_moo AS mmo
    ON m.id = mmo.object_ref_id
  LEFT JOIN organization_organization AS mo
    ON mmo.value_id = mo.id
  LEFT JOIN membershiporganization_fcd AS mmfc
    ON m.id = mmfc.object_ref_id
  LEFT JOIN membershiporganization_lcd AS mmlc
    ON m.id = mmlc.object_ref_id
