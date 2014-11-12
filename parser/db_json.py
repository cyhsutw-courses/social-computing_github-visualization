import math
import json
import sqlite3

db_conn = sqlite3.connect('../db/user.db')
db_cursor = db_conn.cursor()

nodes = []
links = {}


for row in db_cursor.execute('SELECT * FROM star'):
    source = row[0]-1
    target = row[1]-1
    t = (source, target)
    if t in links:
        links[t]['value'] = links[t]['value'] + 1
    else:
        link = {
            'source':source,
            'target':target,
            'value':1
            }
        links[t] = link


max_cnt = 0
for row in db_cursor.execute('SELECT * FROM user ORDER BY id ASC'):
    name = row[1]
    uid = row[0]-1
    cnt = 1
    for k in links.keys():
        if uid == k[1]:
            cnt += 1

    if cnt > max_cnt:
        max_cnt = cnt

    node = {
        'idx': row[0]-1,
        'name': row[1],
        'group': 1,
        'weight':float(cnt),
        'fixed':True,
        #'x':640+300*math.cos(2*math.pi*uid/21.0),
        #'y':400+300*math.sin(2*math.pi*uid/21.0)
    }
    nodes.append(node)


sorted_nodes = sorted(nodes, key=lambda k:k['weight'], reverse=True)

node_map = {}

list_len = len(sorted_nodes)
print list_len
for i in range(list_len):
    node = sorted_nodes[i]
    node['weight'] = node['weight']/max_cnt
    node['x'] = 640+300*math.cos(2*math.pi*i/list_len)
    node['y'] = 400+300*math.sin(2*math.pi*i/list_len)
    node_map[node['idx']] = i

for link in links.values():
    link['source'] = node_map[link['source']]
    link['target'] = node_map[link['target']]

print sorted_nodes

graph = {
    'nodes':sorted_nodes,
    'links':links.values()
}

with open('../visualization/json/network.json', 'w') as output:
    json.dump(graph, output)
