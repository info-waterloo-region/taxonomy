set search_path to taxonomy;

\copy release(release) from 'release.csv' csv;
\copy import_detail(code, definition, created, modified, release) from 'details.csv' csv;
\copy import_code(code, name, is_preferred, release) from 'taxonomy.csv' csv;
\copy import_old(code, old, release) from 'old_codes.csv' csv;
\copy import_also(code, also, release) from 'see_also.csv' csv;

