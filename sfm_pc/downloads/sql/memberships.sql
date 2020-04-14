WITH filtered_organization AS (
    SELECT
      organization.id AS id
    FROM organization_organization AS organization
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
  ), membership AS (
    SELECT
      membership.value_id AS organization_id,
      member_organization.value_id AS member_id,
      array_agg(DISTINCT member_organization_sources.accesspoint_id) AS sources,
      MAX(member_organization.confidence) AS confidence,
      MAX(first_cited_date.value) AS first_cited_date,
      MAX(first_cited_date.confidence) AS first_cited_date_confidence,
      array_agg(DISTINCT first_cited_date_sources.accesspoint_id) AS first_cited_date_sources,
      CASE
        WHEN bool_and(real_start.value) = true THEN 'Y'
        WHEN bool_and(real_start.value) = false THEN 'N'
        ELSE '' END
      AS real_start,
      MAX(real_start.confidence) AS real_start_confidence,
      array_agg(DISTINCT real_start_sources.accesspoint_id) AS real_start_sources,
      MAX(last_cited_date.value) AS last_cited_date,
      MAX(last_cited_date.confidence) AS last_cited_date_confidence,
      array_agg(DISTINCT last_cited_date_sources.accesspoint_id) AS last_cited_date_sources,
      CASE
        WHEN bool_and(real_end.value) = true THEN 'Y'
        WHEN bool_and(real_end.value) = false THEN 'N'
        ELSE '' END
      AS real_end,
      MAX(real_end.confidence) AS real_end_confidence,
      array_agg(DISTINCT real_end_sources.accesspoint_id) AS real_end_sources
    FROM membershiporganization_m AS membership
    JOIN membershiporganization_membershiporganization AS member_object_ref
      ON membership.object_ref_id = member_object_ref.id
    LEFT JOIN membershiporganization_moo AS member_organization
      ON member_object_ref.id = member_organization.object_ref_id
    LEFT JOIN membershiporganization_moo_accesspoints AS member_organization_sources
      ON member_organization.id = member_organization_sources.membershiporganizationorganization_id
    LEFT JOIN membershiporganization_fcd AS first_cited_date
      ON member_object_ref.id = first_cited_date.object_ref_id
    LEFT JOIN membershiporganization_fcd_accesspoints AS first_cited_date_sources
      ON first_cited_date.id = first_cited_date_sources.membershiporganizationfirstciteddate_id
    LEFT JOIN membershiporganization_lcd AS last_cited_date
      ON member_object_ref.id = last_cited_date.object_ref_id
    LEFT JOIN membershiporganization_lcd_accesspoints AS last_cited_date_sources
      ON last_cited_date.id = last_cited_date_sources.membershiporganizationlastciteddate_id
    LEFT JOIN membershiporganization_membershiporganizationrealstart AS real_start
      ON member_object_ref.id = real_start.object_ref_id
    LEFT JOIN membershiporganization_membershiporganizationrealstart_acceac5c AS real_start_sources
      ON real_start.id = real_start_sources.membershiporganizationrealstart_id
    LEFT JOIN membershiporganization_membershiporganizationrealend AS real_end
      ON member_object_ref.id = real_end.object_ref_id
    LEFT JOIN membershiporganization_membershiporganizationrealend_access5a60 AS real_end_sources
      ON real_end.id = real_end_sources.membershiporganizationrealend_id
    GROUP BY membership.value_id, member_organization.value_id
  )
SELECT
  {select}
FROM filtered_organization
JOIN organization
  ON filtered_organization.id = organization.id
LEFT JOIN membership
  ON organization.id = membership.organization_id
LEFT JOIN filtered_organization AS filtered_member_organization
  ON membership.member_id = filtered_member_organization.id
LEFT JOIN organization AS member
  ON filtered_member_organization.id = member.id
