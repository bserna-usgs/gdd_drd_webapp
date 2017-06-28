'''
simple python flask web application to act as a webservice to data created from the
UW GeoDeepDive infastructure
'''
from flask import Flask, render_template
import requests
import psycopg2

app = Flask(__name__)

# usgs bcb data service
r = requests.get('https://gc2.datadistillery.org/api/v1/sql/bcb?q=select%20*%20from%20drip.gdd_results').json()['features']

mentions = []  # collect all mentions returned from the database
for i in r:
    mentions.append(i['properties']['dam_name'])

unique_dam_candidates = set(mentions)  # get unique mentions

store = {}  # dictionary storing unique "dams" and related attributes
for i in r:
    name = i['properties']['dam_name']
    if name not in store.keys():
        flag = i['properties']['flag']
        river_name = i['properties']['river_name']
        sentence = i['properties']['sentence']
        url = i['properties']['url']
        store[name] = [(river_name, flag, sentence, url)]
    else:
        flag = i['properties']['flag']
        river_name = i['properties']['river_name']
        sentence = i['properties']['sentence']
        url = i['properties']['url']
        store[name].append((river_name, flag, sentence, url))

def getUniqueItems(d):
    result = {}
    for key,value in d.items():
        if value not in result.values():
            result[key] = value
    return result
store = getUniqueItems(store)  # attempt to remove dups

'''
Top level
'''
@app.route("/")
def hello():
    return "USGS Dam Removal Literature using GeoDeepDive"

'''
list of unique dams
'''
@app.route("/dam_mentions")
def dam_mentions():
    return render_template('dam_candidates.html', mentions = unique_dam_candidates)

'''
dynamic dam page
'''
@app.route('/dam/<variable>', methods=['GET'])
def dams(variable):
    dam_attrs = store[variable]
    #return str(x)
    return render_template("dam_template.html", dam_attrs=dam_attrs, name=variable)

@app.route("/dam")
def dam():
    return render_template('dam_candidates.html', mentions = unique_dam_candidates)

@app.route('/candidates')
def candidates():
    try:
        conn = psycopg2.connect("dbname='strom_dam_demo' user='postgres' host='localhost' password=''")
        print "db connected"
    except:
        print "unable to connect to the database"

    cur = conn.cursor()
    cur.execute("""SELECT strat_phrase,docid from strat_phrases""")
    all = cur.fetchall()
    print all[:10]
    conn.close()

    return render_template('candidates.html', cand=all)


if __name__ == '__main__':
    app.run()
