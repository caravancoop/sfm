# Area

**Added**

* `geonameid` ID of the Geoname the area is associated with
* `division_id` OCD Division identifier for the country the Area is in

**Modified**

* `geoname` Changed from `Integer` to `Text`

# Geosite

**Added**

* `division_id` OCD Division identifier for the country the Geosite is in

**Modified**

* `geoname` Changed from `Integer` to `Text`

# Organization

**Added**

* `division_id` OCD Division identifier for the country the Organization is associated with

**Modified**

* `alias` Became `aliases` and is now a list of `Alias` (which is just a string)
* `classification` Changed from `Text` to a list of `Classification` (which is just a string)

**Deleted**

* `foundingdate`
* `realfounding`
* `dissolutiondate`
* `realdissolution`

# Person

**Added**

* `division_id` OCD Division identifier for the country the Person is associated with

**Modified**

* `alias` Became `aliases` and is now a list of `Alias` (which is just a string)

**Deleted**

* `deathdate`

# Source

**Added**

* `title` Title of the source 
* `publication.title` Title of the publication
* `publication.country` Country where the publication is based
* `published_on` Date the source was published
* `source_url` Original URL where the source is published
* `archive_url` Archive.org URL for the source
* `date_updated` Date the source was last updated
* `date_added` Date the source was first added
* `page_numer` In the case where the source is printed (book periodical, etc), the page number on which the relevant material can be found
* `accessed_on` Date upon which the researcher accessed the source

# Violation (aka Event)

**Added**

* `division_id` OCD Division identifier for the country where the Violation occurred
* `perpetratorclassification` 
* `types` List of `ViolationType` (based on HURIDOCs standard)

**Modified**

* `perpetrator` Changed from `Person` to list of `Person`
* `perpetratororganization` Changed from `Organization` to list of `Organization`


