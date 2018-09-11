-- Truncate all tables related to the Violation object and remove indeces --
BEGIN;
TRUNCATE "violation_violationstatus",
"violation_violationadminlevel2_sources",
"violation_violationperpetrator_sources",
"violation_violationperpetrator",
"violation_violationadminlevel1_sources",
"violation_violationosmname_sources",
"violation_violationlocationname_sources",
"violation_violationenddate_sources",
"violation_violationlocation_sources",
"violation_violationperpetratororganization_sources",
"violation_violationlocationdescription",
"violation_violationstatus_sources",
"violation_violationtype",
"violation_violationfirstallegation_sources",
"violation_violation",
"violation_violationlastupdate",
"violation_violationlastupdate_sources",
"violation_violationlocationid_sources",
"violation_violationperpetratororganization",
"violation_violationenddate",
"violation_violationlocation",
"violation_violationlocationdescription_sources",
"violation_violationstartdate",
"violation_violationadminlevel2",
"violation_type",
"violation_violationosmid_sources",
"violation_violationlocationname",
"violation_violationtype_sources",
"violation_violationosmname",
"violation_violationadminlevel1",
"violation_violationfirstallegation",
"violation_violationlocationid",
"violation_violationdescription",
"violation_violationperpetratorclassification",
"violation_violationdivisionid",
"violation_violationdescription_sources",
"violation_violationdivisionid_sources",
"violation_violationosmid",
"violation_violationstartdate_sources",
"violation_violationperpetratorclassification_sources",
"violation_perpetratorclassification";
SELECT setval(pg_get_serial_sequence('"violation_violation"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationstartdate"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationfirstallegation"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationenddate"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationlastupdate"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationstatus"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationlocationdescription"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationadminlevel1"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationadminlevel2"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationosmname"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationosmid"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationdivisionid"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationlocation"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationlocationname"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationlocationid"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationdescription"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationperpetrator"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationperpetratororganization"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationtype"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_type"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_violationperpetratorclassification"','id'), 1, false);
SELECT setval(pg_get_serial_sequence('"violation_perpetratorclassification"','id'), 1, false);
COMMIT;
