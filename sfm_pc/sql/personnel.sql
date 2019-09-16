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
  person.uuid AS person_id,
  MAX(person_name.value) AS person_name,
  array_to_string(array_agg(DISTINCT person_alias.value), ';') AS person_other_names,
  substring(MAX(division_id.value), position(':' IN MAX(division_id.value)) + 1, 2) AS person_country_iso,
  MAX(person_date_of_birth.value) AS person_date_of_birth,
  MAX(person_date_of_death.value) AS person_date_of_death,
  bool_and(person_deceased.value) AS person_deceased,
  MAX(person_gender.value) AS person_gender,
  MAX(person_biography.value) AS person_biography,
  MAX(person_notes.value) AS person_notes,
  MAX(person_role.value) AS person_role,
  MAX(person_rank.value) AS person_rank,
  MAX(person_title.value) AS person_title,
  MAX(person_first_cited_date.value) AS person_first_cited_date,
  split_part(MAX(person_first_cited_date.value), '-', 1) As person_first_cited_year,
  split_part(MAX(person_first_cited_date.value), '-', 2) As person_first_cited_month,
  split_part(MAX(person_first_cited_date.value), '-', 3) As person_first_cited_day,
  CASE
    WHEN bool_and(person_real_start.value) = true THEN 'Y'
    WHEN bool_and(person_real_start.value) = false THEN 'N'
    ELSE '' END
  AS person_real_start,
  MAX(person_start_context.value) AS person_start_context,
  MAX(person_last_cited_date.value) AS person_last_cited_date,
  split_part(MAX(person_last_cited_date.value), '-', 1) As person_last_cited_year,
  split_part(MAX(person_last_cited_date.value), '-', 2) As person_last_cited_month,
  split_part(MAX(person_last_cited_date.value), '-', 3) As person_last_cited_day,
  CASE
    WHEN bool_and(person_real_end.value) = true THEN 'Y'
    WHEN bool_and(person_real_end.value) = false THEN 'N'
    ELSE '' END
  AS person_real_end,
  MAX(person_end_context.value) AS person_end_context
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
JOIN membershipperson_membershippersonorganization AS membership_organization
  ON object_ref.id = membership_organization.value_id
JOIN membershipperson_membershipperson AS membership
  ON membership_organization.object_ref_id = membership.id
JOIN membershipperson_membershippersonmember AS member
  ON membership.id = member.object_ref_id
JOIN person_person AS person
  ON member.value_id = person.id
JOIN person_personname AS person_name
  ON person.id = person_name.object_ref_id
LEFT JOIN person_personalias AS person_alias
  ON person.id = person_alias.object_ref_id
LEFT JOIN person_persondateofbirth AS person_date_of_birth
  ON person.id = person_date_of_birth.object_ref_id
LEFT JOIN person_persondateofdeath AS person_date_of_death
  ON person.id = person_date_of_death.object_ref_id
LEFT JOIN person_persongender AS person_gender
  ON person.id = person_gender.object_ref_id
LEFT JOIN person_persondeceased AS person_deceased
  ON person.id = person_deceased.object_ref_id
LEFT JOIN person_personbiography AS person_biography
  ON person.id = person_biography.object_ref_id
LEFT JOIN person_personnotes AS person_notes
  ON person.id = person_notes.object_ref_id
LEFT JOIN membershipperson_membershippersonrole AS role
  ON membership.id = role.object_ref_id
JOIN membershipperson_role AS person_role
  ON role.value_id = person_role.id
LEFT JOIN membershipperson_membershippersonrank AS rank
  ON membership.id = rank.object_ref_id
JOIN membershipperson_rank AS person_rank
  ON rank.value_id = person_rank.id
LEFT JOIN membershipperson_membershippersontitle AS person_title
  ON membership.id = person_title.object_ref_id
LEFT JOIN membershipperson_membershippersonlastciteddate AS person_last_cited_date
  ON membership.id = person_last_cited_date.object_ref_id
LEFT JOIN membershipperson_membershippersonfirstciteddate AS person_first_cited_date
  ON membership.id = person_first_cited_date.object_ref_id
LEFT JOIN membershipperson_membershippersonstartcontext AS person_start_context
  ON membership.id = person_start_context.object_ref_id
LEFT JOIN membershipperson_membershippersonendcontext AS person_end_context
  ON membership.id = person_end_context.object_ref_id
LEFT JOIN membershipperson_membershippersonrealstart AS person_real_start
  ON membership.id = person_real_start.object_ref_id
LEFT JOIN membershipperson_membershippersonrealend AS person_real_end
  ON membership.id = person_real_end.object_ref_id
WHERE division_id.value = '%s'
GROUP BY object_ref.id, membership.id, person.id
