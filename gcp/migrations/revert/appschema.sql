-- Revert golf-better:appschema from pg

begin;

drop schema if exists golfbetter;

commit;
