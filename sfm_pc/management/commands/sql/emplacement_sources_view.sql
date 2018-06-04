CREATE MATERIALIZED VIEW emplacement_sources AS
  SELECT
    ee.id,
    eesd.value AS start_date_value,
    MAX(eesd.confidence) AS start_date_confidence,
    json_agg(DISTINCT eesdss.*) AS start_date_source,

    eeed.value AS end_date_value,
    MAX(eeed.confidence) AS end_date_confidence,
    json_agg(DISTINCT eeedss.*) AS end_date_source,

    eeoe.value AS open_ended_value,
    MAX(eeoe.confidence) AS open_ended_confidence,
    json_agg(DISTINCT eeoess.*) AS open_ended_source,

    oo.uuid AS organization_id_value,
    MAX(eeo.confidence) AS organization_id_confidence,
    json_agg(DISTINCT eeoss.*) AS organization_id_source,

    gg.id AS site_id_value,
    MAX(ees.confidence) AS site_id_confidence,
    json_agg(DISTINCT eesss.*) AS site_id_source
  FROM emplacement_emplacement AS ee
  LEFT JOIN emplacement_emplacementstartdate AS eesd
    ON ee.id = eesd.object_ref_id
  LEFT JOIN emplacement_emplacementstartdate_sources AS eesds
    ON eesd.id = eesds.emplacementstartdate_id
  LEFT JOIN source_source AS eesdss
    ON eesds.source_id = eesdss.uuid
  LEFT JOIN emplacement_emplacementenddate AS eeed
    ON ee.id = eeed.object_ref_id
  LEFT JOIN emplacement_emplacementenddate_sources AS eeeds
    ON eeed.id = eeeds.emplacementenddate_id
  LEFT JOIN source_source AS eeedss
    ON eeeds.source_id = eeedss.uuid
  LEFT JOIN emplacement_emplacementopenended AS eeoe
    ON ee.id = eeoe.object_ref_id
  LEFT JOIN emplacement_emplacementopenended_sources AS eeoes
    ON eeoe.id = eeoes.emplacementopenended_id
  LEFT JOIN source_source AS eeoess
    ON eeoes.source_id = eeoess.uuid
  LEFT JOIN emplacement_emplacementorganization AS eeo
    ON ee.id = eeo.object_ref_id
  LEFT JOIN emplacement_emplacementorganization_sources AS eeos
    ON eeo.id = eeos.emplacementorganization_id
  LEFT JOIN source_source AS eeoss
    ON eeos.source_id = eeoss.uuid
  LEFT JOIN organization_organization AS oo
    ON eeo.value_id = oo.id
  LEFT JOIN emplacement_emplacementsite AS ees
    ON ee.id = ees.object_ref_id
  LEFT JOIN geosite_geosite AS gg
    ON ees.value_id = gg.id
  LEFT JOIN emplacement_emplacementsite_sources AS eess
    ON ees.id = eess.emplacementsite_id
  LEFT JOIN source_source AS eesss
    ON eess.source_id = eesss.uuid
  GROUP BY ee.id,
           eesd.value,
           eeed.value,
           eeoe.value,
           oo.uuid,
           gg.id;
CREATE UNIQUE INDEX emplacement_source_id_index
  ON emplacement_sources (id,
                          open_ended_value,
                          start_date_value,
                          end_date_value);
CREATE INDEX emplacement_org_sources_index
  ON emplacement_sources (organization_id_value, site_id_value)
