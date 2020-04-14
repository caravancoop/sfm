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
  ), composition AS (
    SELECT
      comp_object_ref.id AS id,
      array_agg(DISTINCT comp_classification.value) AS classifications,
      MAX(comp_classification.confidence) AS classifications_confidence,
      array_agg(DISTINCT comp_classification_sources.accesspoint_id) AS classifications_sources,
      MAX(comp_firstciteddate.value) AS first_cited_date,
      MAX(comp_firstciteddate.confidence) AS first_cited_date_confidence,
      array_agg(DISTINCT comp_firstciteddate_sources.accesspoint_id) AS first_cited_date_sources,
      CASE
        WHEN bool_and(comp_realstart.value) = true THEN 'Y'
        WHEN bool_and(comp_realstart.value) = false THEN 'N'
        ELSE '' END
      AS real_start,
      MAX(comp_realstart.confidence) AS real_start_confidence,
      array_agg(DISTINCT comp_realstart_sources.accesspoint_id) AS real_start_sources,
      MAX(comp_lastciteddate.value) AS last_cited_date,
      MAX(comp_lastciteddate.confidence) AS last_cited_date_confidence,
      array_agg(DISTINCT comp_lastciteddate_sources.accesspoint_id) AS last_cited_date_sources,
      MAX(comp_openended.value) AS open_ended,
      MAX(comp_openended.confidence) AS open_ended_confidence,
      array_agg(DISTINCT comp_openended_sources.accesspoint_id) AS open_ended_sources
    FROM composition_composition AS comp_object_ref
    LEFT JOIN composition_compositionclassification AS comp_classification
      ON comp_object_ref.id = comp_classification.object_ref_id
    LEFT JOIN composition_compositionclassification_accesspoints AS comp_classification_sources
      ON comp_classification.id = comp_classification_sources.compositionclassification_id
    LEFT JOIN composition_compositionstartdate AS comp_firstciteddate
      ON comp_object_ref.id = comp_firstciteddate.object_ref_id
    LEFT JOIN composition_compositionstartdate_accesspoints AS comp_firstciteddate_sources
      ON comp_firstciteddate.id = comp_firstciteddate_sources.compositionstartdate_id
    LEFT JOIN composition_compositionenddate AS comp_lastciteddate
      ON comp_object_ref.id = comp_lastciteddate.object_ref_id
    LEFT JOIN composition_compositionenddate_accesspoints AS comp_lastciteddate_sources
      ON comp_lastciteddate.id = comp_lastciteddate_sources.compositionenddate_id
    LEFT JOIN composition_compositionrealstart AS comp_realstart
      ON comp_object_ref.id = comp_realstart.object_ref_id
    LEFT JOIN composition_compositionrealstart_accesspoints AS comp_realstart_sources
      ON comp_realstart.id = comp_realstart_sources.compositionrealstart_id
    LEFT JOIN composition_compositionopenended AS comp_openended
      ON comp_object_ref.id = comp_openended.object_ref_id
    LEFT JOIN composition_compositionopenended_accesspoints AS comp_openended_sources
      ON comp_openended.id = comp_openended_sources.compositionopenended_id
    GROUP BY comp_object_ref.id
  ), composition_parent_metadata AS (
    SELECT
      composition_parent.id AS id,
      MAX(composition_parent.confidence) AS confidence,
      array_agg(DISTINCT composition_parent_sources.accesspoint_id) AS sources
    FROM composition_compositionparent AS composition_parent
    LEFT JOIN composition_compositionparent_accesspoints AS composition_parent_sources
      ON composition_parent.id = composition_parent_sources.compositionparent_id
    GROUP BY composition_parent.id
  )
SELECT
  {select}
FROM composition
LEFT JOIN composition_compositionchild AS composition_child
  ON composition.id = composition_child.object_ref_id
LEFT JOIN filtered_organization AS filtered_child_organization
  ON composition_child.value_id = filtered_child_organization.id
LEFT JOIN organization AS child
  ON filtered_child_organization.id = child.id
LEFT JOIN composition_compositionparent AS composition_parent
  ON composition.id = composition_parent.object_ref_id
LEFT JOIN composition_parent_metadata
  ON composition_parent.id = composition_parent_metadata.id
LEFT JOIN filtered_organization AS filtered_parent_organization
  ON composition_parent.value_id = filtered_parent_organization.id
LEFT JOIN organization AS parent
  ON filtered_parent_organization.id = parent.id
