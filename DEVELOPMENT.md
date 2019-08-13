# Security Force Monitor CMS: Getting started with development

This document lays out a basic guide for how to get going with development on
this project and provides a few tips as to where you might want to start
looking for how to extend it's current functionality or debug issues you might
be having.

### I'm setup. Now what?

So you've gone through the README and have a working version of the site. Let's
start with a basic overview of the data structure which will also give you
a pretty good sense of how the code is organized.

**Top-level entities**

In the world of SFM, there are three entities which reign supreme: People,
Organizations, and Violations (referred to as "Incidents" in the UI parts).
There are also two other entities which should be thought of as first-class but
which operate more in a supporting role so we'll talk about them in a little
bit: Sources and Locations.

People and Organizations are relatively self-explanatory and Violations are
basically the bad things that People and Organizations are reported to have
done. Those three entities also map to the `person`, `organization`, and
`violation` apps within the Django project.

Most of the other Django apps in the project are there to keep track of the
models that create the relationships between these top-level entities. So, for
instance, the `membershipperson` app is where you'll find the models that
relate people to their memberships within organizations. Here's a brief rundown
of the various other kinds of entities:

* **Association** - Relates an Organization to it's area of operation (which is
  a Location that is a polygon)
* **Composition** - Relates an Organization to other Organizations in a command
  chain. This is distinct from **MembershipOrganization** which is described
  below.
* **Emplacement** - Relates an Organization to a location where it was known to
  have been on a date. Similar to **Association** but instead of a Location
  that is a polygon, this will always be a point.
* **MembershipOrganization** - Relates an Organization to some kind of
  temporary grouping such as a UN mission or some other operation. Unlike
  **Composition**s, these kinds of relationships do not imply a command chain.
* **MembershipPerson** - Relates People to Organizations to which they might
  have been posted.

**Sources & AccessPoints**

For every fact that is recorded within this application, there must be at least
one Source and one AccessPoint associated with it (and there are often more
than one). A Source is something like a book or a particular web page. An
AccessPoint is a particular page in that book (or range of pages) or
a particular snapshot taken on a particular date of a web page. On the backend,
these relationships are created by using the [`complex_fields`
app](https://github.com/security-force-monitor/complex_fields) which, in
effect, creates a table for each fact about a given entity that has
a foreign-key relationship with the source and access point tables that tells
us where that fact might have been collected. So, for example, an Organization
will have attributes such as `name`, `firstciteddate`, `lastciteddate`, etc.
Using the base models and decorators provided by the `complex_fields` app, we
end up with a table for each of those attributes along with a pointer to the
source table.

**Locations**

A Location is a particular OSM node, relation, or way that has been
indoctrinated into this application that can then be used to record the
geographic information about an Organization or Violation.

**A note about deprecated code**

There a few apps within this project which are probably not really needed
anymore but, because of the way that the database migrations in particular need
to work, it is very difficult to remove them. For the record, they are:

* **`area`** - Replaced by the `location` app
* **`geosite`** - Replaced by the `location` app

Another app which can probably be safely removed in the near future is the
**`api`** app which hosted the backend logic for the version 1 of the frontend
presentation for the SFM data. This includes:

* The `make_flattened_views` management command.
* The SQL that was written to support that.
* The `api` app itself.

### Where the magic is and a little bit about how it works

In order to make this project even halfway sane to work on, the layers of
abstraction are very deep and can be easy to get lost in. Luckily, in the most
recent round of development, significant progress was made to provide some sane
APIs to use to do a lot of the heavy lifting farther down the stack.

**Updating and creating entities**

Because each of the attributes of entities are stored in a separate table under
the hood, the out-of-the-box functionality that ships with the Django ORM can
be a little tiresome when it comes to creating and updating entities.  Each of
the models which inherits from `complex_fields.base_models.BaseModel` will have
two methods which help streamline these operations. Predictably, these are
called `create` and `update`. Each "field" that is related to a one of these
entities should inherit from `complex_fields.models.ComplexField`. If we expect
that field to only have one value per entity, it should be associated as an
instance of a `complex_fields.models.ComplexFieldContainer`. For fields where
we expect more than one value, it should be associated as an instance of
`complex_fiels.models.ComplexFieldListContainer`. Here's an example:

```
from django.db import models

from complex_fields.base_models import BaseModel
from complex_fields.models import ComplexField, ComplexFieldContainer, \
    ComplexFieldListContainer


class Organization(models.Model, BaseModel):

    def __init__(self, *args, **kwargs):
        self.name = ComplexFieldContainer(self, OrganizationName)
        self.division_id = ComplexFieldContainer(self, OrganizationDivisionId)
        self.aliases = ComplexFieldListContainer(self, OrganizationAlias)


class OrganizationName(ComplexField):
    object_ref = models.ForeignKey(Organization)
    value = models.TextField()


class OrganizationDivisionId(ComplexField):
    object_ref = models.ForeignKey(Organization)
    value = models.TextField()


class OrganizationAlias(ComplexField):
    object_ref = models.ForeignKey(Organization)
    value = models.TextField()
```

For this example, if you'd like to create or update an `Organization`, you
would create a `dict` that looks like this:


```
{
    'Organization_OrganizationName': {
        'sources': [list of AccessPoint objects],
        'value': 'My cool organization',
        'confidence': '1',
    },
    'Organization_OrganizationDivisionId': {
        'sources': [list of AccessPoint objects],
        'value': 'ocd-division/country:us',
        'confidence': '1',
    }
}
```

The keys take the form of `EntityName_EntityAttribute` and should refer to
another `dict` that has `sources`, `value` and `confidence` as keys. `sources`
should, confusingly, be a list of `AccessPoint` objects (this could be
refactored if some brave soul wanted to undertake such a thing). `value` should
contain the value that will be stored in the database. This will vary depending
on the requirements of the field. For fields where we expect there to be more
than one value associated with that attribute, the key should be called
`values` and contain a list of whatever values are required by the field.

To create or update the entity, simply call the `create` or `update` method as
appropriate:

```
Organization.create(dict_from_above)
Orgniazation.update(dict_from_above)
```

**Base forms**

As if that wasn't enough, we also need to be able to create and update entities
from forms that are submitted via the user interface. This includes validating
if the attributes that have been submitted have all the sources that we expect
and are in the form we expect, etc. All of the heavy lifting is done within the
`sfm_pc.forms.BaseUpdateForm` and the `sfm_pc.forms.BaseCreateForm`. Both of
those classes are pretty heavily commented to let you know what's going on at
each step along the way. If for some reason we ever need to implement a new
entity type that also needs to be edited or if you are trying to debug
a problem with form validation, this is where you'll want to start looking.

**Updating the search index**

Whenever an entity is created, updated, or deleted we will want to update the
appropriate things in the search index. Luckily, the same management command
that you use to create the search index in the first place, was also written to
allow you to update a particular entity. To make that slightly easier, there
are signal handlers which listen for the
`complex_fields.base_models.object_ref_saved` signal which can be triggered by
calling the `object_ref_saved` method on any class which inherits from
`complex_fields.base_models.BaseModel`. All of this is already handled within
the base form classes described above so any time a form that subclasses one of
those should do the right thing. However, if you are needing to implement
something new, here's how that might work:

```
org_dict = {
    'Organization_OrganizationName': {
        'sources': [list of access points],
        'value': 'New organization',
        'confidence': '1'
    }
}
org = Organization.create(org_dict)

# Trigger the appropriate signal.
org.object_ref_saved()
```

_A quick note on deleting things_ As things are implemented currently, the only
entities that can be deleted are the ones that represent relationships between
entities (so, things like `MembershipPerson`, `Association`, `Composition`,
etc. as opposed to `Person` and `Organization`). This has mostly to do with the
cascading effect of deleting a top-level entity and how that might lead to
a nonsensical state for certain parts of the data. This is something that is
still being worked out at a more philosophical level by the SFM team. In the
meantime, deleting those relationship entities should behave as expected.

**Versioning**

Currently, the versioning system is in a bit of a flux. There are a few
different ways that have been attempted to keep track of versions of things and
the thinking about what a "version" is in the first place has been evolving. As
a result, the implementation of how versions are recorded is somewhat
schizophrenic. This is a portion of the application that is ripe for refactor.
The places where versions are recorded include:

* Within the `complex_fields` app (as part of the `versioned` decorator in
  `complex_fields.model_decorators`). This should probably be ditched since it
  records a version for every ComplexField. This means that if a user makes an
  edit to a `Person` and changes 5 attributes of that person, we'll end up with
  5 separate entries in our versioning table. One could try to stitch that back
  together to be displayed in a more sensible way (and who knows maybe this
  will end up being the solution here) but is seems like it'd be better to just
  save all of the 5 changes in one version.
* Within the context of views where we are making edits to entities. Anything
  that inherits from `sfm_pc.base_views.BaseUpdateView` or
  `sfm_pc.base_views.BaseCreateView` has the [`RevisionMixin`](https://django-reversion.readthedocs.io/en/stable/views.html#reversion-views-revisionmixin) from Django Reversion, uh, mixed in. This seems
  like probably the best place to handle this but the implementation needs some
  more testing to work out the bugs.
* Some base models (like `Organization` and `Person`) are decorated with the
  [`register`](https://django-reversion.readthedocs.io/en/stable/api.html#registering-models)
  decorator from Django Reversion. This might work if we could figure out how
  to make it follow all of the relationships in a sane way.

As stated above, this portion of the app needs some refactoring to make it more
sane.

**Search index structure**

This application makes heavy use of Solr's [dynamic
fields](https://lucene.apache.org/solr/guide/6_6/dynamic-fields.html).

**Oppotunities for refactor and/or cleanup**

_Templates_ Over the years as the approach for the front end has evolved, a bit
of template cruft has accumulated. Therefore, don't be surprised if you run
across a template or two that do not seem to be used anyplace. This is
something that definitely needs cleaning up. Additionally, there is quite a lot
of repeated code within the editing templates that could probably be more
cleverly refactored into reusable chunks.

_Unused apps_ As mentioned above, when we added the `location` app, the `area`
and `geosite` app became unneeded and can be factored out. Because of the way
that Django manages things, it would seem that it takes more than just deleting
the code, though.
