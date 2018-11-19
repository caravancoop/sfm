SELECT
  source.uuid AS source_id,
  source.title,
  source.published_on AS publication_date,
  source.source_url,
  source.publication,
  source.publication_country,
  access_point.uuid AS access_point_id,
  access_point.archive_url
FROM source_source AS source
JOIN source_accesspoint AS access_point
  ON source.uuid = access_point.source_id
