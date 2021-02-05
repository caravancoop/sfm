CREATE MATERIALIZED VIEW membershiporganization AS 
  SELECT 
    m.id,
    mm.uuid AS member_id,
    oo.uuid AS organization_id,
    mofc.value AS first_cited,
    mors.value as real_start,
    molc.value as last_cited,
    mooe.value as real_end
  FROM membershiporganization_membershiporganization AS m
  LEFT JOIN membershiporganization_m AS mom
    ON m.id = mom.object_ref_id
  LEFT JOIN organization_organization AS mm
    ON mom.value_id = mm.id
  LEFT JOIN membershiporganization_moo AS mmo
    ON m.id = mmo.object_ref_id
  LEFT JOIN organization_organization AS oo
    ON mmo.value_id = oo.id
  LEFT JOIN membershiporganization_fcd AS mofc
    ON m.id = mofc.object_ref_id
  LEFT JOIN membershiporganization_membershiporganizationrealstart AS mors
    ON m.id = mors.object_ref_id
  LEFT JOIN membershiporganization_lcd AS molc
    ON m.id = molc.object_ref_id
  LEFT JOIN membershiporganization_membershiporganizationopenended AS mooe
    ON m.id = mooe.object_ref_id;
CREATE UNIQUE INDEX membershiporg_id_index
    ON membershiporganization (id, first_cited, real_start, last_cited, real_end)
