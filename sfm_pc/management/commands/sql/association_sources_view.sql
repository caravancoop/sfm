CREATE MATERIALIZED VIEW association_sources AS 
  SELECT 
    aa.id,
    aasd.value AS start_date_value,
    MAX(aasd.confidence) AS start_date_confidence,
    json_agg(DISTINCT aasdss.*) AS start_date_source,
    
    aaed.value AS end_date_value,
    MAX(aaed.confidence) AS end_state_confidence,
    json_agg(DISTINCT aaedss.*) AS end_date_source,
    
    aaoe.value AS open_ended_value,
    MAX(aaoe.confidence) AS open_ended_confidence,
    json_agg(DISTINCT aaoess.*) AS open_ended_source,
    
    oo.uuid AS organization_id_value,
    MAX(aao.confidence) AS organization_id_confidence,
    json_agg(DISTINCT aaoss.*) AS organization_id_source,

    aaa.value_id AS area_id_value,
    MAX(aaa.confidence) AS area_id_confidence,
    json_agg(DISTINCT aaass.*) AS area_id_source
  FROM association_association AS aa
  LEFT JOIN association_associationstartdate AS aasd
    ON aa.id = aasd.object_ref_id
  LEFT JOIN association_associationstartdate_sources AS aasds
    ON aasd.id = aasds.associationstartdate_id
  LEFT JOIN source_source AS aasdss
    ON aasds.source_id = aasdss.id
  LEFT JOIN association_associationenddate AS aaed
    ON aa.id = aaed.object_ref_id
  LEFT JOIN association_associationenddate_sources AS aaeds
    ON aaed.id = aaeds.associationenddate_id
  LEFT JOIN source_source AS aaedss
    ON aaeds.source_id = aaedss.id
  LEFT JOIN association_associationopenended AS aaoe
    ON aa.id = aaoe.object_ref_id
  LEFT JOIN association_associationopenended_sources AS aaoes
    ON aaoe.id = aaoes.associationopenended_id
  LEFT JOIN source_source AS aaoess
    ON aaoes.source_id = aaoess.id
  LEFT JOIN association_associationorganization AS aao
    ON aa.id = aao.object_ref_id
  LEFT JOIN organization_organization AS oo
    ON aao.value_id = oo.id
  LEFT JOIN association_associationorganization_sources AS aaos
    ON aao.id = aaos.associationorganization_id
  LEFT JOIN source_source AS aaoss
    ON aaos.source_id = aaoss.id
  LEFT JOIN association_associationarea AS aaa
    ON aa.id = aaa.object_ref_id
  LEFT JOIN association_associationarea_sources AS aaas
    ON aaa.id = aaas.associationarea_id
  LEFT JOIN source_source AS aaass
    ON aaas.source_id = aaass.id
  GROUP BY aa.id,
           aasd.value,
           aaed.value,
           aaoe.value,
           oo.uuid,
           aaa.value_id;

CREATE UNIQUE INDEX association_sources_index 
  ON association_sources (id, 
                          start_date_value, 
                          end_date_value, 
                          area_id_value);
CREATE INDEX association_org_sources_index ON association_sources (organization_id_value, area_id_value)
