SELECT
  {select}
FROM source_source AS source
JOIN source_accesspoint AS access_point
  ON source.uuid = access_point.source_id
