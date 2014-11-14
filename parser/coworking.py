import json
import sqlite3
import itertools

db_conn = sqlite3.connect('../db/objc.db')
db_cursor = db_conn.cursor()

repos = {}

nodes = []
links = []

for row in db_cursor.execute('SELECT * FROM user ORDER BY id ASC'):
    node = {
        'name': row[1]
        #'group': 1,
        #'fixed':True,
        #'x':640+300*math.cos(2*math.pi*uid/21.0),
        #'y':400+300*math.sin(2*math.pi*uid/21.0)
    }
    nodes.append(node)

for row in db_cursor.execute('SELECT * FROM contributor'):
	repo_name = row[0].split('/')[1]
	user = row[-1]-1

	if repo_name not in repos:
		con_set = set([user])
		repos[repo_name] = con_set
	else:
		repos[repo_name].add(user)


keys = set()
cnt = 0
for key in repos:
	if len(repos[key]) <= 1:
		keys.add(key)
	else:
		cnt += len(repos[key])*(len(repos[key])-1)/2

for key in keys:
	repos.pop(key, None)

all_links = {}

for key in repos:
	combination = itertools.combinations(repos[key], 2)
	for pair in combination:
		if pair not in all_links:
			link1 = {
				'source': pair[0],
				'target': pair[1],
				'value':1
			}
			link2 = {
				'source': pair[1],
				'target': pair[0],
				'value':1
			}
			all_links[tuple(list([pair[0], pair[1]]))] = link1
			all_links[tuple(list([pair[1], pair[0]]))] = link2
		else:
			all_links[tuple(list([pair[0], pair[1]]))]['value'] += 1
			all_links[tuple(list([pair[1], pair[0]]))]['value'] += 1

print all_links.values()

graph = {
	'nodes':nodes,
	'links':all_links.values()
}

with open('../visualization/json/cowork.json', 'w') as output:
    json.dump(graph, output)

