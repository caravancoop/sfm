CREATE OR REPLACE VIEW emplacement AS 
  SELECT 
    ee.id,
    eesd.value AS start_date,
    eeed.value AS end_date,
    oo.uuid AS organization_id,
    gg.id AS site_id
  FROM emplacement_emplacement AS ee
  LEFT JOIN emplacement_emplacementstartdate AS eesd
    ON ee.id = eesd.object_ref_id
  LEFT JOIN emplacement_emplacementenddate AS eeed
    ON ee.id = eeed.object_ref_id
  LEFT JOIN emplacement_emplacementorganization AS eeo
    ON ee.id = eeo.object_ref_id
  LEFT JOIN organization_organization AS oo
    ON eeo.value_id = oo.id
  LEFT JOIN emplacement_emplacementsite AS ees
    ON ee.id = ees.object_ref_id
  LEFT JOIN geosite_geosite AS gg
    ON ees.value_id = gg.id
