CREATE MATERIALIZED VIEW organization_site_name_export AS
  SELECT
    oo.uuid AS organization_id,
    ee.id AS emplacement_id,
    ggn.value AS site_name,
    ggn.confidence AS site_name_confidence,
    ggnss.uuid AS source_id
  FROM emplacement_emplacement AS ee
  LEFT JOIN emplacement_emplacementorganization AS eeo
    ON ee.id = eeo.object_ref_id
  LEFT JOIN organization_organization AS oo
    ON eeo.value_id = oo.id
  LEFT JOIN emplacement_emplacementsite AS ees
    ON ee.id = ees.object_ref_id
  LEFT JOIN geosite_geosite AS gg
    ON ees.value_id = gg.id
  LEFT JOIN geosite_geositename AS ggn
    ON gg.id = ggn.object_ref_id
  LEFT JOIN geosite_geositename_sources AS ggns
    ON ggn.id = ggns.geositename_id
  LEFT JOIN source_source AS ggnss
    ON ggns.source_id = ggnss.uuid
  GROUP BY oo.uuid, ee.id, gg.id, ggn.value, ggn.confidence, ggnss.uuid
