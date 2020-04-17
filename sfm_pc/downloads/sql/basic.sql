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
      array_agg(DISTINCT name_sources.accesspoint_id) AS name_sources,
      MAX(division_id.value) AS division_id,
      MAX(division_id.confidence) AS division_id_confidence,
      array_agg(DISTINCT division_id_sources.accesspoint_id) AS division_id_sources,
      array_agg(DISTINCT classifications.value) AS classifications,
      MAX(classifications.confidence) AS classifications_confidence,
      array_agg(DISTINCT classifications_sources.accesspoint_id) AS classifications_sources,
      array_agg(DISTINCT aliases.value) AS aliases,
      MAX(aliases.confidence) AS aliases_confidence,
      array_agg(DISTINCT aliases_sources.accesspoint_id) AS aliases_sources,
      MAX(firstciteddate.value) AS first_cited_date,
      MAX(firstciteddate.confidence) AS first_cited_date_confidence,
      array_agg(DISTINCT firstciteddate_sources.accesspoint_id) AS first_cited_date_sources,
      MAX(lastciteddate.value) AS last_cited_date,
      MAX(lastciteddate.confidence) AS last_cited_date_confidence,
      array_agg(DISTINCT lastciteddate_sources.accesspoint_id) AS last_cited_date_sources,
      CASE
        WHEN bool_and(realstart.value) = true THEN 'Y'
        WHEN bool_and(realstart.value) = false THEN 'N'
        ELSE '' END
      AS real_start,
      MAX(realstart.confidence) AS real_start_confidence,
      array_agg(DISTINCT realstart_sources.accesspoint_id) AS real_start_sources,
      MAX(open_ended.value) AS open_ended,
      MAX(open_ended.confidence) AS open_ended_confidence,
      array_agg(DISTINCT open_ended_sources.accesspoint_id) AS open_ended_sources
    FROM organization_organization AS object_ref
    JOIN organization_organizationname AS name
      ON object_ref.id = name.object_ref_id
    LEFT JOIN organization_organizationname_accesspoints AS name_sources
      ON name.id = name_sources.organizationname_id
    JOIN organization_organizationdivisionid AS division_id
      ON object_ref.id = division_id.object_ref_id
    LEFT JOIN organization_organizationdivisionid_accesspoints AS division_id_sources
      ON division_id.id = division_id_sources.organizationdivisionid_id
    LEFT JOIN organization_organizationclassification AS classifications
      ON object_ref.id = classifications.object_ref_id
    LEFT JOIN organization_organizationclassification_accesspoints AS classifications_sources
      ON classifications.id = classifications_sources.organizationclassification_id
    LEFT JOIN organization_organizationalias AS aliases
      ON object_ref.id = aliases.object_ref_id
    LEFT JOIN organization_organizationalias_accesspoints AS aliases_sources
      ON aliases.id = aliases_sources.organizationalias_id
    LEFT JOIN organization_organizationfirstciteddate AS firstciteddate
      ON object_ref.id = firstciteddate.object_ref_id
    LEFT JOIN organization_organizationfirstciteddate_accesspoints AS firstciteddate_sources
      ON firstciteddate.id = firstciteddate_sources.organizationfirstciteddate_id
    LEFT JOIN organization_organizationlastciteddate AS lastciteddate
      ON object_ref.id = lastciteddate.object_ref_id
    LEFT JOIN organization_organizationlastciteddate_accesspoints AS lastciteddate_sources
      ON lastciteddate.id = lastciteddate_sources.organizationlastciteddate_id
    LEFT JOIN organization_organizationrealstart AS realstart
      ON object_ref.id = realstart.object_ref_id
    LEFT JOIN organization_organizationrealstart_accesspoints AS realstart_sources
      ON realstart.id = realstart_sources.organizationrealstart_id
    LEFT JOIN organization_organizationopenended AS open_ended
      ON object_ref.id = open_ended.object_ref_id
    LEFT JOIN organization_organizationopenended_accesspoints AS open_ended_sources
      ON open_ended.id = open_ended_sources.organizationopenended_id
    GROUP BY object_ref.id
  )
SELECT
 {select}
FROM filtered_organization
JOIN organization
  ON filtered_organization.id = organization.id
