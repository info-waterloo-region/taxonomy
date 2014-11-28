from flask import Flask, redirect, render_template, request, url_for

import urllib

import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

import config

def super_list(code):
  l = []
  if code != code[0]:
    l.append((code[0], code[0]))
    if code != code[0:2]:
      l.append((code[0:2], code[1:2]))
      if code != code[0:7]:
        l.append((code[0:7], code[3:7]))
        if code != code[0:12]:
          l.append((code[0:12], code[8:12]))
          if code != code[0:16]:
            l.append((code[0:16], code[13:16]))
  return l

def last_part(code):
  if code == code[0]:
    return code
  elif code == code[0:2]:
    return code[1:2]
  elif code == code[0:7]:
    return code[3:7]
  elif code == code[0:12]:
    return code[8:12]
  elif code == code[0:16]:
    return code[13:16]
  else:
    return code[17:]

def sub_pattern(code):
  p = None
  l = len(code)
  if l < 19:
    if l < 16:
      if l < 12:
        if l < 7:
          if l < 2:
            p = '_'
          else:
            p = '-____'
        else:
          p = '.____'
      else:
        p = '-___'
    else:
      p = '.__'
  return p

conn = psycopg2.connect(
  port=config.port,
  database=config.database,
  user=config.user,
  password=config.password)

app = Flask(__name__)

@app.route('/')
def index():
  c = conn.cursor()
  c.execute("""
    select
      code.code,
      code.name,
      detail.definition
    from
      taxonomy.import_code as code
      join
      taxonomy.import_detail as detail
      using (code, release)
    where
      code.is_preferred = 1
      and
      char_length(code.code) = 1
    order by
      code.code;
    """)

  results = []
  for row in c.fetchall():
    results.append(
      dict(
        code = row[0], 
        name = row[1], 
        definition = row[2]))

  c.close()

  return render_template("template.html", codes=results)

@app.route('/<code>/')
def code(code):
  c = conn.cursor()
  sql = """
    select
      preferred.name,
      detail.definition,
      array_agg(distinct used_for.name order by used_for.name)
    from
      taxonomy.import_code as preferred
      join
      taxonomy.import_detail as detail
      using (code, release)

      left outer join
      taxonomy.import_code as used_for
      on (
        preferred.code = used_for.code
        and
        preferred.release = used_for.release
        and
        used_for.is_preferred = 0)
    where
      preferred.code = %s
      and
      preferred.is_preferred = 1
    group by
      preferred.code,
      preferred.name,
      detail.definition
    order by
      preferred.code;
  """
  c.execute(sql, (code,))
  row = c.fetchone()
  result = dict()
  if row:
    result["code"] = code

    result["name"] = row[0]
    result["definition"] = row[1]
    result["used_for"] = row[2]

    c.close()

    result["crumbs"] = super_list(code)
    result["last_crumb"] = last_part(code)
             
    sql = """
      select
        also.also,
        code.name
      from
        taxonomy.import_also as also
        join
        taxonomy.import_code as code
        on (
          also.also = code.code
          and
          code.is_preferred = 1)
      where
        also.code = %s
      order by
        code.name;
    """
    c = conn.cursor()
    c.execute(sql, (code,))
    result["see_also"] = c.fetchall()
    c.close()

    result["subs"] = None
    if sub_pattern(code):
      sql = """
        select
          c.code,
          c.name
        from
          taxonomy.import_code as c
        where
          c.is_preferred = 1
          and
          c.code like %s || %s;
      """
      c = conn.cursor()
      c.execute(sql, (code, sub_pattern(code)))
      result["subs"] = c.fetchall()
      c.close()
    return render_template("code.html", code=result)
  else:
    c.close()
    return "Page not found", 404

@app.route("/search", methods=["POST"])
def search():
  q = request.form["search"].lower()
  return redirect(url_for("search_results", q=urllib.quote_plus(q)))

@app.route("/search/<q>/")
def search_results(q):
  sql = """
    select
      category.name,
      code.code,
      name.name
    from
      taxonomy.import_code as code
      join
      taxonomy.import_detail as detail
      using (code, release)

      join
      taxonomy.import_code as name
      on (
        code.code = name.code
        and
        name.is_preferred = 1)

      join
      taxonomy.import_code as category
      on (
        substring(code.code from 1 for 1) = category.code
        and
        category.is_preferred = 1)
    where
      to_tsvector('english', code.name) @@ plainto_tsquery('english', %s)
      or
      to_tsvector('english', detail.definition) @@ plainto_tsquery('english', %s)
    group by
      category.code,
      category.name,
      code.code,
      name.name
    order by
      category.code,
      name.name;
  """
  c = conn.cursor()
  c.execute(sql, (q,q))
  result = dict()
  result["results"] = []
  for row in c.fetchall():
    r = dict(
      cat = row[0],
      code = row[1],
      name = row[2])
    result["results"].append(r)
  result["query"] = urllib.unquote_plus(q)
  c.close()
  return render_template("search.html", result=result)

if __name__ == '__main__':
  app.debug = True
  app.run('0.0.0.0', 5001)

