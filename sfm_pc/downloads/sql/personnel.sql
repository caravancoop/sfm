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
  ), filtered_person AS (
    SELECT
      person.id AS id
      FROM person_person AS person
      WHERE person.published = true
  ), person AS (
    SELECT
      person.id AS id,
      MAX(person.uuid::text) AS uuid,
      MAX(person_name.value) AS name,
      MAX(person_name.confidence) AS name_confidence,
      array_agg(DISTINCT person_name_sources.accesspoint_id) AS name_sources,
      array_agg(DISTINCT person_alias.value) AS aliases,
      MAX(person_alias.confidence) AS aliases_confidence,
      array_agg(DISTINCT person_alias_sources.accesspoint_id) AS aliases_sources,
      MAX(person_division_id.value) AS division_id,
      MAX(person_division_id.confidence) AS division_id_confidence,
      array_agg(DISTINCT person_division_id_sources.accesspoint_id) AS division_id_sources,
      MAX(person_date_of_birth.value) AS date_of_birth,
      MAX(person_date_of_birth.confidence) AS date_of_birth_confidence,
      array_agg(DISTINCT person_date_of_birth_sources.accesspoint_id) AS date_of_birth_sources,
      MAX(person_date_of_death.value) AS date_of_death,
      MAX(person_date_of_death.confidence) AS date_of_death_confidence,
      array_agg(DISTINCT person_date_of_death_sources.accesspoint_id) AS date_of_death_sources,
      bool_and(person_deceased.value) AS deceased,
      MAX(person_deceased.confidence) AS deceased_confidence,
      array_agg(DISTINCT person_deceased_sources.accesspoint_id) AS deceased_sources,
      MAX(person_gender.value) AS gender,
      MAX(person_gender.confidence) AS gender_confidence,
      array_agg(DISTINCT person_gender_sources.accesspoint_id) AS gender_sources,
      array_agg(DISTINCT person_account_type.value) AS account_types,
      MAX(person_account_type.confidence) AS account_types_confidence,
      array_agg(DISTINCT person_account_type_sources.accesspoint_id) AS account_types_sources,
      array_agg(DISTINCT person_account.value) AS accounts,
      MAX(person_account_type.confidence) AS accounts_confidence,
      array_agg(DISTINCT person_account_sources.accesspoint_id) AS accounts_sources,
      array_agg(DISTINCT person_external_link_description.value) AS external_link_descriptions,
      MAX(person_external_link_description.confidence) AS external_link_descriptions_confidence,
      array_agg(DISTINCT person_external_link_description_sources.accesspoint_id) AS external_link_descriptions_sources,
      array_agg(DISTINCT person_media_description.value) AS media_descriptions,
      MAX(person_media_description.confidence) AS media_descriptions_confidence,
      array_agg(DISTINCT person_media_description_sources.accesspoint_id) AS media_descriptions_sources,
      array_agg(DISTINCT person_notes.value) AS notes,
      MAX(person_notes.confidence) AS notes_confidence,
      array_agg(DISTINCT person_notes_sources.accesspoint_id) AS notes_sources
    FROM person_person AS person
    JOIN person_personname AS person_name
      ON person.id = person_name.object_ref_id
    LEFT JOIN person_personname_accesspoints AS person_name_sources
      ON person_name.id = person_name_sources.personname_id
    LEFT JOIN person_persondivisionid as person_division_id
      ON person.id = person_division_id.id
    LEFT JOIN person_persondivisionid_accesspoints AS person_division_id_sources
      ON person_division_id.id = person_division_id_sources.persondivisionid_id
    LEFT JOIN person_personalias AS person_alias
      ON person.id = person_alias.object_ref_id
    LEFT JOIN person_personalias_accesspoints AS person_alias_sources
      ON person_alias.id = person_alias_sources.personalias_id
    LEFT JOIN personbiography_personbiographyperson AS person_biography_person
      ON person.id = person_biography_person.value_id
    LEFT JOIN personbiography_personbiography AS person_biography
      ON person_biography_person.object_ref_id = person_biography.id
    LEFT JOIN personbiography_personbiographydateofbirth AS person_date_of_birth
      ON person_biography.id = person_date_of_birth.object_ref_id
    LEFT JOIN personbiography_personbiographydateofbirth_accesspoints AS person_date_of_birth_sources
      ON person_date_of_birth.id = person_date_of_birth_sources.personbiographydateofbirth_id
    LEFT JOIN personbiography_personbiographydateofdeath AS person_date_of_death
      ON person_biography.id = person_date_of_death.object_ref_id
    LEFT JOIN personbiography_personbiographydateofdeath_accesspoints AS person_date_of_death_sources
      ON person_date_of_death.id = person_date_of_death_sources.personbiographydateofdeath_id
    LEFT JOIN personbiography_personbiographygender AS person_gender
      ON person_biography.id = person_gender.object_ref_id
    LEFT JOIN personbiography_personbiographygender_accesspoints AS person_gender_sources
      ON person_gender.id = person_gender_sources.personbiographygender_id
    LEFT JOIN personbiography_personbiographydeceased AS person_deceased
      ON person_biography.id = person_deceased.object_ref_id
    LEFT JOIN personbiography_personbiographydeceased_accesspoints AS person_deceased_sources
      ON person_deceased.id = person_deceased_sources.personbiographydeceased_id
    LEFT JOIN personextra_personextraperson AS person_extra_person
      ON person.id = person_extra_person.value_id
    LEFT JOIN personextra_personextra AS person_extra
      ON person_extra_person.object_ref_id = person_extra.id
    LEFT JOIN personextra_personextraaccounttype AS person_account_type
      ON person_extra.id = person_account_type.object_ref_id
    LEFT JOIN personextra_personextraaccounttype_accesspoints AS person_account_type_sources
      ON person_account_type.id = person_account_type_sources.personextraaccounttype_id
    LEFT JOIN personextra_personextraaccount AS person_account
      ON person_extra.id = person_account.object_ref_id
    LEFT JOIN personextra_personextraaccount_accesspoints AS person_account_sources
      ON person_account.id = person_account_sources.personextraaccount_id
    LEFT JOIN personextra_personextraexternallinkdescription AS person_external_link_description
      ON person_extra.id = person_external_link_description.object_ref_id
    LEFT JOIN personextra_personextraexternallinkdescription_accesspoints AS person_external_link_description_sources
      ON person_external_link_description.id = person_external_link_description_sources.personextraexternallinkdescription_id
    LEFT JOIN personextra_personextramediadescription AS person_media_description
      ON person_extra.id = person_media_description.object_ref_id
    LEFT JOIN personextra_personextramediadescription_accesspoints AS person_media_description_sources
      ON person_media_description.id = person_media_description_sources.personextramediadescription_id
    LEFT JOIN personextra_personextranotes AS person_notes
      ON person_extra.id = person_notes.object_ref_id
    LEFT JOIN personextra_personextranotes_accesspoints AS person_notes_sources
      ON person_notes.id = person_notes_sources.personextranotes_id
    GROUP BY person.id
  ), membership AS (
    SELECT
      membership_organization.value_id AS organization_id,
      member.value_id AS person_id,
      MAX(member.confidence) AS person_id_confidence,
      array_agg(DISTINCT member_sources.accesspoint_id) AS person_id_sources,
      MAX(person_role.value) AS role,
      MAX(role.confidence) AS role_confidence,
      array_agg(DISTINCT role_sources.accesspoint_id) AS role_sources,
      MAX(person_rank.value) AS rank,
      MAX(rank.confidence) AS rank_confidence,
      array_agg(DISTINCT rank_sources.accesspoint_id) AS rank_sources,
      MAX(person_title.value) AS title,
      MAX(person_title.confidence) AS title_confidence,
      array_agg(DISTINCT title_sources.accesspoint_id) AS title_sources,
      MAX(person_first_cited_date.value) AS first_cited_date,
      split_part(MAX(person_first_cited_date.value), '-', 1) As first_cited_date_year,
      split_part(MAX(person_first_cited_date.value), '-', 2) As first_cited_date_month,
      split_part(MAX(person_first_cited_date.value), '-', 3) As first_cited_date_day,
      MAX(person_first_cited_date.confidence) AS first_cited_date_confidence,
      array_agg(DISTINCT person_first_cited_date_sources.accesspoint_id) AS first_cited_date_sources,
      CASE
        WHEN bool_and(person_real_start.value) = true THEN 'Y'
        WHEN bool_and(person_real_start.value) = false THEN 'N'
        ELSE '' END
      AS real_start,
      MAX(person_real_start.confidence) AS real_start_confidence,
      array_agg(DISTINCT person_real_start_sources.accesspoint_id) AS real_start_sources,
      MAX(person_start_context.value) AS start_context,
      MAX(person_start_context.confidence) AS start_context_confidence,
      array_agg(DISTINCT person_start_context_sources.accesspoint_id) AS start_context_sources,
      MAX(person_last_cited_date.value) AS last_cited_date,
      split_part(MAX(person_last_cited_date.value), '-', 1) As last_cited_date_year,
      split_part(MAX(person_last_cited_date.value), '-', 2) As last_cited_date_month,
      split_part(MAX(person_last_cited_date.value), '-', 3) As last_cited_date_day,
      MAX(person_last_cited_date.confidence) AS last_cited_date_confidence,
      array_agg(DISTINCT person_last_cited_date_sources.accesspoint_id) AS last_cited_date_sources,
      CASE
        WHEN bool_and(person_real_end.value) = true THEN 'Y'
        WHEN bool_and(person_real_end.value) = false THEN 'N'
        ELSE '' END
      AS real_end,
      MAX(person_real_end.confidence) AS real_end_confidence,
      array_agg(DISTINCT person_real_end_sources.accesspoint_id) AS real_end_sources,
      MAX(person_end_context.value) AS end_context,
      MAX(person_end_context.confidence) AS end_context_confidence,
      array_agg(DISTINCT person_end_context_sources.accesspoint_id) AS end_context_sources
    FROM membershipperson_membershippersonorganization AS membership_organization
    JOIN membershipperson_membershipperson AS membership
      ON membership_organization.object_ref_id = membership.id
    JOIN membershipperson_membershippersonmember AS member
      ON membership.id = member.object_ref_id
    LEFT JOIN membershipperson_membershippersonmember_accesspoints AS member_sources
      ON member.id = member_sources.membershippersonmember_id
    LEFT JOIN membershipperson_membershippersonrole AS role
      ON membership.id = role.object_ref_id
    JOIN membershipperson_role AS person_role
      ON role.value_id = person_role.id
    LEFT JOIN membershipperson_membershippersonrole_accesspoints AS role_sources
      ON role.id = role_sources.membershippersonrole_id
    LEFT JOIN membershipperson_membershippersonrank AS rank
      ON membership.id = rank.object_ref_id
    JOIN membershipperson_rank AS person_rank
      ON rank.value_id = person_rank.id
    LEFT JOIN membershipperson_membershippersonrank_accesspoints AS rank_sources
      ON rank.id = rank_sources.membershippersonrank_id
    LEFT JOIN membershipperson_membershippersontitle AS person_title
      ON membership.id = person_title.object_ref_id
    LEFT JOIN membershipperson_membershippersontitle_accesspoints AS title_sources
      ON person_title.id = title_sources.membershippersontitle_id
    LEFT JOIN membershipperson_membershippersonlastciteddate AS person_last_cited_date
      ON membership.id = person_last_cited_date.object_ref_id
    LEFT JOIN membershipperson_membershippersonlastciteddate_accesspoints AS person_last_cited_date_sources
      ON person_last_cited_date.id = person_last_cited_date_sources.membershippersonlastciteddate_id
    LEFT JOIN membershipperson_membershippersonfirstciteddate AS person_first_cited_date
      ON membership.id = person_first_cited_date.object_ref_id
    LEFT JOIN membershipperson_membershippersonfirstciteddate_accesspoints AS person_first_cited_date_sources
      ON person_first_cited_date.id = person_first_cited_date_sources.membershippersonfirstciteddate_id
    LEFT JOIN membershipperson_membershippersonstartcontext AS person_start_context
      ON membership.id = person_start_context.object_ref_id
    LEFT JOIN membershipperson_membershippersonstartcontext_accesspoints AS person_start_context_sources
      ON person_start_context.id = person_start_context_sources.membershippersonstartcontext_id
    LEFT JOIN membershipperson_membershippersonendcontext AS person_end_context
      ON membership.id = person_end_context.object_ref_id
    LEFT JOIN membershipperson_membershippersonendcontext_accesspoints AS person_end_context_sources
      ON person_end_context.id = person_end_context_sources.membershippersonendcontext_id
    LEFT JOIN membershipperson_membershippersonrealstart AS person_real_start
      ON membership.id = person_real_start.object_ref_id
    LEFT JOIN membershipperson_membershippersonrealstart_accesspoints AS person_real_start_sources
      ON person_real_start.id = person_real_start_sources.membershippersonrealstart_id
    LEFT JOIN membershipperson_membershippersonrealend AS person_real_end
      ON membership.id = person_real_end.object_ref_id
    LEFT JOIN membershipperson_membershippersonrealend_accesspoints AS person_real_end_sources
      ON person_real_end.id = person_real_end_sources.membershippersonrealend_id
    GROUP BY membership_organization.value_id, member.value_id
  )
SELECT
  {select}
FROM filtered_organization
JOIN organization
  ON filtered_organization.id = organization.id
LEFT JOIN membership
  ON organization.id = membership.organization_id
LEFT JOIN filtered_person
  ON membership.person_id = filtered_person.id
LEFT JOIN person
  ON filtered_person.id = person.id
