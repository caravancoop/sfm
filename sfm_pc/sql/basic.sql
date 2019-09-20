SELECT
  object_ref.uuid AS uuid,
  MAX(name.value) AS name,
  substring(MAX(division_id.value), position(':' IN MAX(division_id.value)) + 1, 2) AS basic_country_iso,
  array_to_string(array_agg(DISTINCT classifications.value), ';') AS classifications,
  array_to_string(array_agg(DISTINCT aliases.value), ';') AS other_names,
  MAX(firstciteddate.value) AS first_cited_date,
  MAX(lastciteddate.value) AS last_cited_date,
  CASE
    WHEN bool_and(realstart.value) = true THEN 'Y'
    WHEN bool_and(realstart.value) = false THEN 'N'
    ELSE '' END
  AS start_date_of_organization,
  MAX(open_ended.value) AS open_ended
FROM organization_organization AS object_ref
JOIN organization_organizationname AS name
  ON object_ref.id = name.object_ref_id
JOIN organization_organizationdivisionid AS division_id
  ON object_ref.id = division_id.object_ref_id
LEFT JOIN organization_organizationclassification AS classifications
  ON object_ref.id = classifications.object_ref_id
LEFT JOIN organization_organizationalias AS aliases
  ON object_ref.id = aliases.object_ref_id
LEFT JOIN organization_organizationfirstciteddate AS firstciteddate
  ON object_ref.id = firstciteddate.object_ref_id
LEFT JOIN organization_organizationlastciteddate AS lastciteddate
  ON object_ref.id = lastciteddate.object_ref_id
LEFT JOIN organization_organizationrealstart AS realstart
  ON object_ref.id = realstart.object_ref_id
LEFT JOIN organization_organizationopenended AS open_ended
  ON object_ref.id = open_ended.object_ref_id
WHERE division_id.value = '%s'
GROUP BY object_ref.id
