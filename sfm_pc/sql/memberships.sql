SELECT
  object_ref.uuid AS uuid,
  MAX(name.value) AS name,
  substring(MAX(division_id.value), position(':' IN MAX(division_id.value)) + 1, 2) AS org_country_iso,
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
  member.uuid AS member_id,
  MAX(member_name.value) AS member_name,
  substring(MAX(member_country.value), position(':' IN MAX(member_country.value)) + 1, 2) AS member_country_iso,
  MAX(member_firstciteddate.value) AS membership_start_date,
  MAX(member_lastciteddate.value) AS membership_end_date,
  CASE
    WHEN bool_and(member_realstart.value) = true THEN 'Y'
    WHEN bool_and(member_realstart.value) = false THEN 'N'
    ELSE '' END
  AS membership_real_start,
  CASE
    WHEN bool_and(member_realend.value) = true THEN 'Y'
    WHEN bool_and(member_realend.value) = false THEN 'N'
    ELSE '' END
  AS membership_real_end
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
LEFT JOIN membershiporganization_m AS membership
  ON object_ref.id = membership.value_id
JOIN membershiporganization_membershiporganization AS member_object_ref
  ON membership.object_ref_id = member_object_ref.id
LEFT JOIN membershiporganization_moo AS member_organization
  ON member_object_ref.id = member_organization.object_ref_id
LEFT JOIN organization_organization AS member
  ON member_organization.value_id = member.id
LEFT JOIN organization_organizationname AS member_name
  ON member.id = member_name.object_ref_id
JOIN organization_organizationdivisionid as member_country
  on member.id = member_country.object_ref_id
LEFT JOIN membershiporganization_fcd AS member_firstciteddate
  ON member_object_ref.id = member_firstciteddate.object_ref_id
LEFT JOIN membershiporganization_lcd AS member_lastciteddate
  ON member_object_ref.id = member_lastciteddate.object_ref_id
LEFT JOIN membershiporganization_membershiporganizationrealstart AS member_realstart
  ON member_object_ref.id = member_realstart.object_ref_id
LEFT JOIN membershiporganization_membershiporganizationrealend AS member_realend
  ON member_object_ref.id = member_realend.object_ref_id
WHERE division_id.value = '%s'
GROUP BY object_ref.id, member.uuid
