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
