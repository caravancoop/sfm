CREATE MATERIALIZED VIEW organization_membership_export AS
  SELECT
    m.id AS membership_id,
    mm.uuid AS member_organization_id,
    mo.uuid AS organization_id,
    mmo.confidence AS membership_confidence,
    mmoss.id AS source_id
  FROM membershiporganization_membershiporganization AS m
  LEFT JOIN membershiporganization_m AS mom
    ON m.id = mom.object_ref_id
  LEFT JOIN organization_organization AS mm
    ON mom.value_id = mm.id
  LEFT JOIN membershiporganization_moo AS mmo
    ON m.id = mmo.object_ref_id
  LEFT JOIN organization_organization AS mo
    ON mmo.value_id = mo.id
  LEFT JOIN membershiporganization_moo_sources AS mmos
    ON mmo.id = mmos.membershiporganizationorganization_id
  LEFT JOIN source_source AS mmoss
    ON mmos.source_id = mmoss.id
  GROUP BY m.id, mm.uuid, mo.uuid, mmo.confidence, mmoss.id
