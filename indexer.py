import sqlite3
import os
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.index import open_dir
from whoosh.index import EmptyIndexError

def db_close(conn):#close the db connection
   try:
     conn.close()
   except:
     pass
     
def db_connect(dbname, *tables):
  if dbname == '':#if database name is empty then specify one to connect to
       inp = input("Please specify a database name or press /N or /n to exit\n")#take input in
       if inp.startswith('/n') or inp.startswith('/N'):#exit if either input is given
         exit()
       else:#take in the databasename
         dbname = inp
  conn = sqlite3.connect(dbname)#connect to the databsee
  conn.row_factory = sqlite3.Row#grab rows
  if len(tables) == 0:#if tables is empty then go ahead and feth all data and append tables
     tables = []
     try:
       df = conn.execute('SELECT name FROM sqlite_master WHERE type = "table";')#grab everything in database
       data = df.fetchall()
       for row in data:
         for member in row:
           tables.append(member)
     except Exception as e:#if error then either continue or exit
       print("Error: " + str(e))
       inp = input("Continue? Yes or no\n")
       if 'y' in inp or 'Y' in inp:
         pass
       else:
         exit()
  return tables, conn, dbname#return tables connection and database

def index(dbnames_schemas = {}, indexdir = 'indexdir'):
  if len(dbnames_schemas) == 0:#if schema isnt define then go ahead and run db connect on empty schema
    tables, conn, dbname = db_connect('')
    schema = ''
    parse_db(tables, conn, indexname=dbname, schema='', indexdir = indexdir)#parse the database table indexing them empty schema
  else:
   for i in dbnames_schemas.keys():#given schema keys run rb connect on given schema
    tables, conn, dbname = db_connect(i)
    parse_db(tables, conn, indexname=i, schema= dbnames_schemas[i], indexdir=indexdir)#parse the database table indexing them given schema

    
def parse_db(tables, conn, indexname, schema, indexdir):
  try:
   ix = open_dir(indexdir, indexname)#open the index store in ix
   print('\nIndex: ' + indexname + ' already exists in directory: ' + indexdir + ' Overwrite?. YES or NO')#if exists overwrite or not
   inp = input("<> ")
   if 'y' in inp or 'Y' in inp:
     pass
   else:
     return
  except:
   pass
  print('\n\nDATABASE: ' + indexname + ' contains ' + str(len(tables)) + ' tables')#print length  
  for table in tables:
    print('Indexing table: ' + table + '...')
    t = tuple(table)#grab tubles
    c = conn.cursor()#start cursor
    c.execute('SELECT * FROM ' + table + ";")#select everything
    rows = c.fetchall()#grab all rows
    if len(rows) != 0:#if not empty
      keys = rows[0].keys()#first row is the keys
      while ('Schema' not in str(type(schema))):#make sure schema i
        if 'con' in str(type(schema)):#str exists in str type schema
         if not schema.strip() is '':#if empty break
           break
        inp = input("> You didn't provide a schema. Provide one? Yes or no (Use default schema): ")#ask for schema because it wasnt provided
        s = 'Schema('#grab first row for default schema
        for key in keys:
           s += key.replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '') + "=TEXT(stored=True), "
        s = s.rstrip(", ")
        s += ")"
        if inp.strip().startswith('y') or inp.strip().startswith('Y'):#if schema wants to be given then take in schema anything that begins with y
         print('Your database contains the following column names:')
         [print(x + ", ", end='') for x in keys]
         print('''\n\nPlease use them to generate a schema of the form: "Schema(COLUMN_NAME=whoosh.field.type, ...)"
            e.g. ''' + s)#print example of first row
         schema = input('Please input a schema: ')#continue asking for schema if one is not given
         while not schema or not schema.startswith('Schema') or not schema.endswith(')'):#if not given or doesnt start with Schema continue asking for intput
           schema = input('Please input a schema: ')
         schema.strip()
        else:
         print('Proceeding to use default schema: ' + s)#default schema is chosen
         schema = s
        break
      schema = eval(schema)#evaluate schema
      if not os.path.exists(indexdir):#make directory and create index with schema and index name
        os.mkdir(indexdir)
      ix = create_in(indexdir, schema=schema, indexname=indexname)
      writer = ix.writer()#to write into documents
      docline = ''#empty to begin
      print('Indexing ' + indexname)
      for row in rows:#add documents to docline
         docline = 'writer.add_document('
         for key in keys:#go through all keys(schema descriptions) and place items in the according columns
            val = row[key]
            if "'" in val: #needed to remove invalid syntax
             val = escape(val)
            val = val.replace("\t", "").replace("\n", "").replace("\r", "")#grab values and replace 
            print(val)  
            docline += key.replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', '') + "=u'" + val + "', "#append key with values and replace
         docline = docline.rstrip(", ")#remove ", "
         docline += ")"#close
         print('...', end='\r')
         try:
          eval(docline)#evaluate
         except Exception as e:#if error thrown then cancel writing and return
          print ('Error at: ' + docline)
          writer.cancel()
          print('Cancelled indexing due to error: ' + str(e))
          return
      writer.commit()#commit and print total
      print('Total data indexed: ' + str(len(rows)) )
    else:#nothing entered
      print('Database contains no valid rows')

def escape(s, obj = "'"):
  ret = ''
  for x in s:#go through entire string and compare and remove invalid sytax by appending
    if x == obj:
      ret += '\\'
    ret += x
  return ret
  
if __name__ in '__main__':#define the index dir and the db_schemas for our first example (dinosaur) we define the schemas for the rest we can input a 
   ix = None#new schema or go with a default one
   indexdir = "indexdir"
   dbnames_schemas = {'dinosaur.db' : 'Schema(Name=TEXT(stored=True), Description=TEXT(stored=True), Era=TEXT(stored=True), Url=ID(stored=True), Image=ID(stored=True))',
    'mmorpg.db' : '', 'superfamicom.db' : ''}
   print('Creating new index: ' + indexdir)
   index(
      dbnames_schemas, indexdir
      )
