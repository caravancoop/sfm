CREATE OR REPLACE VIEW geosite AS 
  SELECT 
    gg.id,
    ggn.value AS name,
    ggal1.value AS admin_level_1,
    ggal2.value AS admin_level_2,
    ggc.value AS coordinates,
    ggd.value AS division_id
  FROM geosite_geosite AS gg
  LEFT JOIN geosite_geositename AS ggn
    ON gg.id = ggn.object_ref_id
  LEFT JOIN geosite_geositeadminlevel1 AS ggal1
    ON gg.id = ggal1.object_ref_id
  LEFT JOIN geosite_geositeadminlevel2 AS ggal2
    ON gg.id = ggal2.object_ref_id
  LEFT JOIN geosite_geositecoordinates AS ggc
    ON gg.id = ggc.object_ref_id
  LEFT JOIN geosite_geositedivisionid AS ggd
    ON gg.id = ggd.object_ref_id
