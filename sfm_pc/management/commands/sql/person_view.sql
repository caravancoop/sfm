CREATE MATERIALIZED VIEW person AS 
  SELECT 
    pp.uuid AS id,
    ppn.value AS name,
    pa.value AS alias,
    ppd.value AS division_id
  FROM person_person AS pp
  LEFT JOIN person_personname AS ppn
    ON pp.id = ppn.object_ref_id
  LEFT JOIN person_personalias AS ppa
    ON pp.id = ppa.object_ref_id
  LEFT JOIN person_alias AS pa
    ON ppa.value_id = pa.id
  LEFT JOIN person_persondivisionid AS ppd
    ON pp.id = ppd.object_ref_id;
CREATE UNIQUE INDEX person_id_index ON person (id, alias)
