WITH filtered_organization AS (
    SELECT
      organization.id AS id
    FROM organization_organization as organization
    WHERE organization.published = true
  ), organization AS (
    SELECT
      object_ref.id AS id,
      MAX(object_ref.uuid::text) AS uuid,
      MAX(name.value) AS name,
      MAX(name.confidence) AS name_confidence,
      MAX(division_id.value) AS division_id,
      MAX(division_id.confidence) AS division_id_confidence,
      array_agg(DISTINCT classifications.value) AS classifications,
      MAX(classifications.confidence) AS classifications_confidence,
      array_agg(DISTINCT aliases.value) AS aliases,
      MAX(aliases.confidence) AS aliases_confidence,
      MAX(firstciteddate.value) AS first_cited_date,
      MAX(firstciteddate.confidence) AS first_cited_date_confidence,
      MAX(lastciteddate.value) AS last_cited_date,
      MAX(lastciteddate.confidence) AS last_cited_date_confidence,
      CASE
        WHEN bool_and(realstart.value) = true THEN 'Y'
        WHEN bool_and(realstart.value) = false THEN 'N'
        ELSE '' END
      AS real_start,
      MAX(realstart.confidence) AS real_start_confidence,
      MAX(open_ended.value) AS open_ended,
      MAX(open_ended.confidence) AS open_ended_confidence
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
    GROUP BY object_ref.id
  ), emplacement AS (
    SELECT
      emplacement_organization.value_id AS organization_id,
      emplacement.id AS id,
      MAX(location.id) AS site_id,
      MAX(site.confidence) AS site_confidence
    FROM emplacement_emplacementorganization AS emplacement_organization
    JOIN emplacement_emplacement AS emplacement
      ON emplacement_organization.object_ref_id = emplacement.id
    JOIN emplacement_emplacementsite AS site
      ON emplacement.id = site.object_ref_id
    JOIN location_location AS location
      ON site.value_id = location.id
    GROUP BY emplacement_organization.value_id, emplacement.id
  ), filtered_location AS (
    SELECT
      location.id AS id
    FROM location_location AS location
    WHERE (location.feature_type = 'node' OR location.feature_type = 'point')
  ), location AS (
    SELECT
      location.id AS id,
      MAX(location.name) AS name,
      MAX(location.division_id) AS division_id,
      MAX(location.feature_type) AS feature_type,
      MAX(location.adminlevel) AS admin_level,
      MAX(adminlevel1.id) AS admin_level_1_id,
      MAX(adminlevel1.name) AS admin_level_1_name,
      MAX(adminlevel2.id) AS admin_level_2_id,
      MAX(adminlevel2.name) AS admin_level_2_name
    FROM location_location AS location
    LEFT JOIN location_location AS adminlevel1
      ON location.adminlevel1_id = adminlevel1.id
    LEFT JOIN location_location AS adminlevel2
      ON location.adminlevel2_id = adminlevel2.id
    GROUP BY location.id
  )
SELECT
  {select}
FROM filtered_organization
JOIN organization
  ON filtered_organization.id = organization.id
JOIN emplacement
  ON organization.id = emplacement.organization_id
JOIN filtered_location
  ON emplacement.site_id = filtered_location.id
JOIN location
  ON filtered_location.id = location.id
