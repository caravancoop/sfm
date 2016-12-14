CREATE OR REPLACE VIEW membershiporganization_sources AS 
  SELECT 
    m.id,
    mm.uuid AS member_id_value,
    mom.confidence AS member_id_confidence,
    row_to_json(momss.*) AS member_id_sources,
    
    mo.uuid AS organization_id_value,
    mmo.confidence AS organization_id_confidence,
    row_to_json(mmoss.*) AS organization_id_sources,

    mmfc.value AS first_cited_date_value,
    mmfc.confidence AS first_cited_date_confidence,
    row_to_json(mmfcss.*) AS first_cited_date_sources,

    mmlc.value AS last_cited_date_value,
    mmlc.confidence AS last_cited_date_confidence,
    row_to_json(mmlcss.*) AS last_cited_date_sources
  FROM membershiporganization_membershiporganization AS m
  LEFT JOIN membershiporganization_m AS mom
    ON m.id = mom.object_ref_id
  LEFT JOIN organization_organization AS mm
    ON mom.value_id = mm.id
  LEFT JOIN membershiporganization_m_sources AS moms
    ON mom.id = moms.membershiporganizationmember_id
  LEFT JOIN source_source AS momss
    ON moms.source_id = momss.id
  LEFT JOIN membershiporganization_moo AS mmo
    ON m.id = mmo.object_ref_id
  LEFT JOIN membershiporganization_moo_sources AS mmos
    ON mmo.id = mmos.membershiporganizationorganization_id
  LEFT JOIN source_source AS mmoss
    ON mmos.source_id = mmoss.id
  LEFT JOIN organization_organization AS mo
    ON mmo.value_id = mo.id
  LEFT JOIN membershiporganization_fcd AS mmfc
    ON m.id = mmfc.object_ref_id
  LEFT JOIN membershiporganization_fcd_sources AS mmfcs
    ON mmfc.id = mmfcs.membershiporganizationfirstciteddate_id
  LEFT JOIN source_source AS mmfcss
    ON mmfcs.source_id = mmfcss.id
  LEFT JOIN membershiporganization_lcd AS mmlc
    ON m.id = mmlc.object_ref_id
  LEFT JOIN membershiporganization_lcd_sources AS mmlcs
    ON mmlc.id = mmlcs.membershiporganizationlastciteddate_id
  LEFT JOIN source_source AS mmlcss
    ON mmlcs.source_id = mmlcss.id
