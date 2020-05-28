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
  ), composition AS (
    SELECT
      comp_object_ref.id AS id,
      array_agg(DISTINCT comp_classification.value) AS classifications,
      MAX(comp_classification.confidence) AS classifications_confidence,
      MAX(comp_firstciteddate.value) AS first_cited_date,
      MAX(comp_firstciteddate.confidence) AS first_cited_date_confidence,
      CASE
        WHEN bool_and(comp_realstart.value) = true THEN 'Y'
        WHEN bool_and(comp_realstart.value) = false THEN 'N'
        ELSE '' END
      AS real_start,
      MAX(comp_realstart.confidence) AS real_start_confidence,
      MAX(comp_lastciteddate.value) AS last_cited_date,
      MAX(comp_lastciteddate.confidence) AS last_cited_date_confidence,
      MAX(comp_openended.value) AS open_ended,
      MAX(comp_openended.confidence) AS open_ended_confidence
    FROM composition_composition AS comp_object_ref
    LEFT JOIN composition_compositionclassification AS comp_classification
      ON comp_object_ref.id = comp_classification.object_ref_id
    LEFT JOIN composition_compositionstartdate AS comp_firstciteddate
      ON comp_object_ref.id = comp_firstciteddate.object_ref_id
    LEFT JOIN composition_compositionenddate AS comp_lastciteddate
      ON comp_object_ref.id = comp_lastciteddate.object_ref_id
    LEFT JOIN composition_compositionrealstart AS comp_realstart
      ON comp_object_ref.id = comp_realstart.object_ref_id
    LEFT JOIN composition_compositionopenended AS comp_openended
      ON comp_object_ref.id = comp_openended.object_ref_id
    GROUP BY comp_object_ref.id
  ), composition_parent_metadata AS (
    SELECT
      composition_parent.id AS id,
      MAX(composition_parent.confidence) AS confidence
    FROM composition_compositionparent AS composition_parent
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
