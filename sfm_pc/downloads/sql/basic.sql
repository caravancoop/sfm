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
  )
SELECT
 {select}
FROM filtered_organization
JOIN organization
  ON filtered_organization.id = organization.id
