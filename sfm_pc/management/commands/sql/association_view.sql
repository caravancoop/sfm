CREATE MATERIALIZED VIEW association AS 
  SELECT 
    aa.id,
    aasd.value AS start_date,
    aars.value AS real_start,
    aaed.value AS end_date,
    aaoe.value AS open_ended,
    oo.uuid AS organization_id,
    aaa.value_id AS area_id
  FROM association_association AS aa
  LEFT JOIN association_associationstartdate AS aasd
    ON aa.id = aasd.object_ref_id
  LEFT JOIN association_associationrealstart AS aars
    ON aa.id = aars.object_ref_id
  LEFT JOIN association_associationenddate AS aaed
    ON aa.id = aaed.object_ref_id
  LEFT JOIN association_associationopenended AS aaoe
    ON aa.id = aaoe.object_ref_id
  LEFT JOIN association_associationorganization AS aao
    ON aa.id = aao.object_ref_id
  LEFT JOIN organization_organization AS oo
    ON aao.value_id = oo.id
  LEFT JOIN association_associationarea AS aaa
    ON aa.id = aaa.object_ref_id;

CREATE UNIQUE INDEX association_index ON association (id, start_date, real_start, end_date, open_ended, area_id);
CREATE INDEX association_org_index ON association (organization_id, area_id)
