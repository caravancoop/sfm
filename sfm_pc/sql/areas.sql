SELECT
  object_ref.uuid AS uuid,
  MAX(name.value) AS name,
  substring(MAX(division_id.value), position(':' IN MAX(division_id.value)) + 1, 2) AS division_id,
  array_to_string(array_agg(DISTINCT classifications.value), ';') AS classifications,
  array_to_string(array_agg(DISTINCT aliases.value), ';') AS other_names,
  MAX(firstciteddate.value) AS first_cited_date,
  MAX(lastciteddate.value) AS last_cited_date,
  CASE
    WHEN bool_and(realstart.value) = true THEN 'Y'
    WHEN bool_and(realstart.value) = false THEN 'N'
    ELSE '' END
  AS start_date_of_organization,
  MAX(open_ended.value) AS open_ended,
  location.id AS area_osm_id,
  MAX(location.name) AS area_name,
  substring(MAX(division_id.value), position(':' IN MAX(division_id.value)) + 1, 2) AS area_country_iso,
  MAX(location.feature_type) AS area_osm_feature_type,
  MAX(location.adminlevel) AS area_admin_level,
  MAX(adminlevel1.id) AS admin_level_1_id,
  MAX(adminlevel1.name) AS admin_level_1_name,
  MAX(adminlevel2.id) AS admin_level_2_id,
  MAX(adminlevel2.name) AS admin_level_2_name
  FROM organization_organization AS object_ref
  JOIN association_associationorganization AS association_organization
    ON object_ref.id = association_organization.value_id
  JOIN association_association AS association
    ON association_organization.object_ref_id = association.id
  JOIN association_associationarea AS area
    ON association.id = area.object_ref_id
  JOIN location_location AS location
    ON area.value_id = location.id
  LEFT JOIN location_location AS adminlevel1
    ON location.adminlevel1_id = adminlevel1.id
  LEFT JOIN location_location AS adminlevel2
    ON location.adminlevel2_id = adminlevel2.id
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
    AND location.feature_type != 'node'
  GROUP BY object_ref.uuid, location.id
