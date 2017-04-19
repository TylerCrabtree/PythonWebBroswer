from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import scoring
from indexer import index
from whoosh.index import open_dir, exists_in
from whoosh.filedb.filestore import FileStorage
from flask import Flask, render_template, request, jsonify
from collections import defaultdict
import os.path
from mtranslate import translate


app = Flask(__name__)


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/_search')
def search():#to search through
  indexdir =  "indexdir"#have index dir
  a = request.args.get('a', 0, type=str)#grab search term
  if not a:#empty take in input
    a = 'none'
    return jsonify(result=a)
  a = translate(a,"en","auto")#translate it
  b = request.args.get('b', 0, type=str)#the database
  c = request.args.get('c', 0, type=int)#the limit
  if not c:#if limit empty set to None
    c = 'None'
  ix = open_dir(indexdir, b)#open dir
  qparsers = []#storage
  v = 0;#to store actual length of results
  with ix.searcher(weighting=scoring.TF_IDF()) as searcher:
    categories = list(ix.schema._fields.keys())#keys
    qparser = MultifieldParser(categories, ix.schema)#parse
    inp = a#take input 
    query = qparser.parse(inp.strip())#word stripped
    if c == 'None':#if none then search without limit and store actual length of results
      results = searcher.search(query, limit=None)
      v = len(results)
    else:#with limit then set limit and check if limit is greater than make len of results the limit
      results = searcher.search(query, limit=c)
      if c > len(results):
        v = len(results)
      else:
        v = c
    if not results:#empty return nothing
      a = 'none'
      return jsonify(result=a, results=v, resultss=c)
    result = defaultdict(list)
    for i in results:#make list
      for key,value in i.items():
        result[key].append(value)
    return jsonify(result=result, results=v, resultss=c)#return values



if '__main__' in __name__:
  app.run(debug=True)

