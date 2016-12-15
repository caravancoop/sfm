CREATE MATERIALIZED VIEW geosite AS 
  SELECT 
    gg.id,
    ggn.value AS name,
    ggal1.value AS admin_level_1,
    ggal2.value AS admin_level_2,
    ggo.value AS osmname,
    ggni.value AS osm_id,
    ggc.value AS coordinates,
    ggd.value AS division_id,
    ggfc.value AS first_cited,
    gglc.value AS last_cited,
    ggoe.value AS open_ended
  FROM geosite_geosite AS gg
  LEFT JOIN geosite_geositename AS ggn
    ON gg.id = ggn.object_ref_id
  LEFT JOIN geosite_geositeosmname AS ggo
    ON gg.id = ggo.object_ref_id
  LEFT JOIN geosite_geositeosmid AS ggni
    ON gg.id = ggni.object_ref_id
  LEFT JOIN geosite_geositeadminlevel1 AS ggal1
    ON gg.id = ggal1.object_ref_id
  LEFT JOIN geosite_geositeadminlevel2 AS ggal2
    ON gg.id = ggal2.object_ref_id
  LEFT JOIN geosite_geositecoordinates AS ggc
    ON gg.id = ggc.object_ref_id
  LEFT JOIN geosite_geositedivisionid AS ggd
    ON gg.id = ggd.object_ref_id
  LEFT JOIN geosite_geositefirstcited AS ggfc
    ON gg.id = ggfc.object_ref_id
  LEFT JOIN geosite_geositelastcited AS gglc
    ON gg.id = gglc.object_ref_id
  LEFT JOIN geosite_geositeopenended AS ggoe
    ON gg.id = ggoe.object_ref_id
