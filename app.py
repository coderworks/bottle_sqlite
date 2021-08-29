#!/usr/bin/env python3

from bottle import get, post, redirect, request, route, run, static_file, template, error
import bottle
from datetime import datetime
from api import sql


#### GlobVar section ####
_bottle = {
    "baseurl" : "/",
    "template": "index.html",
    "version" : str(bottle.__version__),
    "title"   : "News Paper!",
    "message" : ""
}

_columns = [ "timestamp", "value" ]
_db = sql.DB( r"database.db", "project", _columns, [ "INTEGER"  , "TEXT" ] )

def message(debug, message):
    
    if not debug:
        if message:
            _bottle["message"] = message

    else:
        _bottle["message"] = "Ow no. Something terrible happened!\n" + str( debug )
    
#### BottlePy section ####
# ------------------------------------------
''' Static Files'''
@route( '/static/:path#.+#', name='static' ) # supply a path for js and css files
def static( path ):
    return static_file( path, root='static' )


''' Create '''
@post( _bottle["baseurl"] )
def create_object():
    
    values = [datetime.now(), request.POST.get('value')]

    # returns the id of the one created. and an empty list item (row)
    rowId, notinuse, debug = _db.create_row( values )

    message( debug, "'" + request.POST.get('value') + "' added with ID " + str(rowId) + "!" )

    return redirect(  _bottle["baseurl"] )


''' Retreive '''
@get( _bottle["baseurl"] ) # (static route)
def present_all_objects():

    # returns a '0' and a list with the rows asked including the id of te row in the list
    rowid, rows, debug = _db.read_rows()

    message( debug, "" )

    return template( _bottle["template"], bottle = _bottle, db = _db.settings, values = rows )


''' Update '''
@post( _bottle["baseurl"] + '<identifier>' )
def post_object( identifier = "none" ):

    # exmple identifier = (1, '2021-08-22 16:57:21.725235', 'foo') from POST
    items = identifier.replace("(", "")
    items = identifier.split(",")
    searchId = items[0][-1:]
    values = []

    for column in _columns:
        values.append( request.POST.get(column) )
    
    # this seems to normally not be an SQLite 'problem'?
    rowid, rows, debug = _db.read_row(searchId)
    if (rows) == []:
        message( "This row got missing while updating was in progress!", "")

    else:
        # returns a '0' and an empty list item (row)
        rowid, rows, debug = _db.update_row( searchId, values )

        message( debug, "ID " + str( searchId ) + " updated with values '" + str( values )  + "' !" )

    return redirect( _bottle["baseurl"] )


''' Delete '''
@post( _bottle["baseurl"]  + 'delete/'+ '<identifier>' )
def delete_object( identifier = "" ):

    # returns a '0' and an empty list item (row)
    rowid, rows, debug = _db.delete_row( identifier )

    message( debug, "Row with ID '" + str( identifier ) + "' just got deleted!" )

    return redirect( _bottle["baseurl"] )

@error(404)
def error404(error):
    return 'Wow, you actually maded it here!!!. Sorry this is still a 404'
# ---------------------------------------------------

#### Main section ####

if "Error:" in _db.debug:
    print(_db.debug)

else:

    message( _db.debug, "Welcome! Breaking news will show up here... " )

    with _db.connection:
        run( host='localhost', port=8000, debug=True, reloader=True)
