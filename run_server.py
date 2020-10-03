import flask
from flask import request, jsonify, render_template
import sqlite3
import json
import time

app = flask.Flask(__name__, template_folder='frontend')
app.config["DEBUG"] = False

def get_dict_from_query(conn, query_str):
    exec = conn.execute(query_str)

    fieldnames = [d[0] for d in exec.description]
    rows = exec.fetchall()
    results = []
    for row in rows:
        data = dict(zip(fieldnames, row)) 
        results.append(data)

    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/query', methods=['GET'])
def query():
    now = time.time()

    conn = sqlite3.connect('database.db')
    # entries = get_dict_from_query(conn, '''SELECT * FROM entries;''')
    data_tgs = get_dict_from_query(conn, '''SELECT * FROM talkgroups;''')
    for data_tg in data_tgs:
        id = data_tg['id']
        entries_active = get_dict_from_query(conn, '''SELECT * FROM entries WHERE DestinationID=%d AND Stop=0 ORDER BY Start DESC;''' % id)
        entries_inactive = get_dict_from_query(conn, '''SELECT * FROM entries WHERE DestinationID=%d AND Stop>0 ORDER BY Stop DESC;''' % id)
        
        data_tg['active'] = []
        data_tg['inactive'] = []
        for entry in entries_active:
            data_tg['active'].append({'sourceCall': entry['SourceCall'], 'sourceName': entry['SourceName'], 'elapsed': now-entry['Start']})
        for entry in entries_inactive:
            data_tg['inactive'].append({'sourceCall': entry['SourceCall'], 'sourceName': entry['SourceName'], 'elapsed': now-entry['Stop']})

    conn.close()
    return jsonify(data_tgs)


app.run()