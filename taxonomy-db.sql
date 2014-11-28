create schema taxonomy;

set search_path to taxonomy;

drop table if exists
  import_code,
  import_old,
  import_also,
  import_detail,
  release,
  code,
  name,
  meta,
  other,
  definition
cascade;

create table release (
  release timestamp primary key
);

create table import_detail (
  code varchar(19),
  definition text not null,
  created date,
  modified date,
  release timestamp references release,
  primary key (code, release)
);

create index search_definition
  on import_detail
  using gin(to_tsvector('english', definition));

create table import_code (
  code varchar(19),
  name varchar(100) not null,
  is_preferred int,
  release timestamp references release,
  foreign key (code, release) references import_detail
);

create index search_name
  on import_code
  using gin(to_tsvector('english', name));

create table import_old (
  code varchar(19),
  old varchar(19) not null,
  release timestamp references release,
  foreign key (code, release) references import_detail
);

create table import_also (
  code varchar(19),
  also varchar(19) not null,
  release timestamp references release,
  foreign key (code, release) references import_detail
);

create table code (
  id serial primary key,
  code varchar(19)
);

create table name (
  id serial primary key,
  name varchar(100),
  preferred boolean default false
);

create table meta (
  id serial primary key,
  created date,
  modified date
);

create table other (
  id serial primary key,
  other integer,
  kind integer
);

create table definition (
  id serial primary key,
  definition text
);

