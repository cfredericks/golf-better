-- Deploy golf-better:appschema to pg

begin;

create schema if not exists golfbetter;

commit;
