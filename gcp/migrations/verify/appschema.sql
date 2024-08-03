-- Verify golf-better:appschema on pg

begin;

select pg_catalog.has_schema_privilege('golfbetter', 'usage');

rollback;
