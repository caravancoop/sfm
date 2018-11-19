SELECT
  object_ref.uuid AS uuid,
  MAX(name.value) AS name,
  MAX(division_id.value) AS division_id,
  array_to_string(array_agg(DISTINCT classifications.value), ';') AS classifications,
  array_to_string(array_agg(DISTINCT aliases.value), ';') AS other_names,
  MAX(firstciteddate.value) AS first_cited_date,
  MAX(lastciteddate.value) AS last_cited_date,
  bool_and(realstart.value) AS start_date_of_organization,
  MAX(open_ended.value) AS open_ended,
  parent.uuid AS parent_id,
  MAX(parent_name.value) AS parent_name,
  array_to_string(array_agg(DISTINCT comp_classification.value), ';') AS relationship_classifications,
  MAX(comp_firstciteddate.value) AS relationship_first_cited_date,
  bool_and(comp_realstart.value) AS relationship_realstart,
  MAX(comp_lastciteddate.value) AS relationship_last_cited_date,
  MAX(comp_openended.value) AS relationship_open_ended
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
LEFT JOIN composition_compositionchild AS child
  ON object_ref.id = child.value_id
LEFT JOIN composition_composition AS comp_object_ref
  ON child.object_ref_id = comp_object_ref.id
LEFT JOIN composition_compositionparent AS comp_parent
  ON comp_object_ref.id = comp_parent.object_ref_id
LEFT JOIN organization_organization AS parent
  ON comp_parent.value_id = parent.id
LEFT JOIN organization_organizationname AS parent_name
  ON parent.id = parent_name.object_ref_id
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
WHERE division_id.value = '%s'
GROUP BY object_ref.id, parent.uuid
