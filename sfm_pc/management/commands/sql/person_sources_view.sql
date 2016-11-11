CREATE OR REPLACE VIEW person_sources AS 
  SELECT 
    pp.uuid AS id,
    ppn.value AS name_value,
    ppn.confidence AS name_confidence,
    row_to_json(ppnss.*) AS name_source,
    pa.value AS alias_value,
    ppa.confidence AS alias_confidence,
    row_to_json(ppass.*) AS alias_source,
    ppd.value AS division_id
  FROM person_person AS pp
  LEFT JOIN person_personname AS ppn
    ON pp.id = ppn.object_ref_id
  LEFT JOIN person_personname_sources AS ppns
    ON ppn.id = ppns.personname_id
  LEFT JOIN source_source AS ppnss
    ON ppns.source_id = ppnss.id
  LEFT JOIN person_personalias AS ppa
    ON pp.id = ppa.object_ref_id
  LEFT JOIN person_alias AS pa
    ON ppa.value_id = pa.id
  LEFT JOIN person_personalias_sources AS ppas
    ON ppa.id = ppas.personalias_id
  LEFT JOIN source_source AS ppass
    ON ppas.source_id = ppass.id
  LEFT JOIN person_persondivisionid AS ppd
    ON pp.id = ppd.object_ref_id
