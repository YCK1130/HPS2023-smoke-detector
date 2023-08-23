import json
import math
detectors = [
    "entryA",
    "bedroom",
    "aisleA",
    "studyroom",
    "BedroomC",
    "intersection",
    "aisleC",
    "aisleB",
    "kitchen",
    "meetingroom",
    "entryB",
    "BedroomB",
]
LOG = False
INF = 1e5
# Opening JSON file
f = open('./node-red/sensor-data-template/nodes.json')
 
# returns JSON object as a dictionary
data = json.load(f)
adjacentList = data["connection"]
select_type = ["smoke_detector","door","entry"]
nodes = []
node_data={}
for mytype in select_type:
    nodes = nodes+data[mytype]
for node in nodes:
    node_data[node["place"]] = (node["left"],node["top"])
# Closing file
f.close()

def check_digraph(adjacentList):
    for node in adjacentList:
        adj = adjacentList[node]
        for neighbor in adj:
            if node not  in adjacentList[neighbor]:
                print(f"{node} not in {neighbor}'s adj list!")
                return False
    print("This is a digraph!")
    return True
def convertToGraph(nodes ,node_data,select_type,adjacentList):
    adj_list = {}

    for node in nodes:
        place = node["place"]
        x,y=node_data[place]
        adjs = []
        for neighbor in adjacentList[place]:
            nx,ny = node_data[neighbor]
            dist = math.sqrt((x-nx)**2+(y-ny)**2)
            adjs.append((neighbor,dist))
        adj_list[place] = adjs
    return adj_list

def heuristic(nodes ,node_data,select_type,destinaiton:str):
    h = {}
    dx,dy = node_data[destinaiton]
    for node in nodes:
        place = node["place"]
        x,y=node_data[place]
        dist = math.sqrt((x-dx)**2+(y-dy)**2)
        h[place]=dist
    return h
# ref: https://stackabuse.com/courses/graphs-in-python-theory-and-implementation/lessons/a-star-search-algorithm/
class Graph:
    def __init__(self, adjacency_list,heuristic_map):
        self.adjacency_list = adjacency_list
        self.origin_adjacency_list = adjacency_list
        self.H = heuristic_map

    def get_neighbors(self, v):
        return self.adjacency_list[v]

    # heuristic function with equal values for all nodes
    def h(self, n):
        return self.H[n]

    def fire(self,place):
        neighbors = self.get_neighbors(place)
        for i in range(len(neighbors)-1):
            adj_1,_ = neighbors[i]
            for idx,x in enumerate(self.get_neighbors(adj_1)):
                neighbor,weight = x
                if neighbor==place:
                    if LOG:
                        print("del:",adj_1,neighbor)
                    del self.adjacency_list[adj_1][idx]
                    break
            for j in range(i+1,len(neighbors)):
                adj_2,_ = neighbors[j]
                for idx,x in enumerate(self.get_neighbors(adj_1)):
                    neighbor,weight = x
                    if neighbor==adj_2:
                        if LOG:
                            print("del:",adj_1,neighbor)
                        del self.adjacency_list[adj_1][idx]
                        break
                for idx,x in enumerate(self.get_neighbors(adj_2)):
                    neighbor,weight = x
                    if neighbor==adj_1:
                        if LOG:
                            print("del:",adj_2,neighbor)
                        del self.adjacency_list[adj_2][idx]
                        break
        adj_last,_=neighbors[-1]
        for idx,x in enumerate(self.get_neighbors(adj_last)):
            neighbor,weight = x
            if neighbor==place:
                if LOG:
                    print("del:",adj_last,neighbor)
                del self.adjacency_list[adj_last][idx]
                break

        self.adjacency_list[place]=[]                

    def a_star_algorithm(self, start_node, stop_node):
        # open_list is a list of nodes which have been visited, but who's neighbors
        # haven't all been inspected, starts off with the start node
        # closed_list is a list of nodes which have been visited
        # and who's neighbors have been inspected
        open_list = set([start_node])
        closed_list = set([])

        # g contains current distances from start_node to all other nodes
        # the default value (if it's not found in the map) is +infinity
        g = {}

        g[start_node] = 0

        # parents contains an adjacency map of all nodes
        parents = {}
        parents[start_node] = start_node

        while len(open_list) > 0:
            n = None

            # find a node with the lowest value of f() - evaluation function
            for v in open_list:
                if n == None or g[v] + self.h(v) < g[n] + self.h(n):
                    n = v

            if n == None:
                if LOG:
                    print('Path does not exist!')
                return None, INF

            # if the current node is the stop_node
            # then we begin reconstructin the path from it to the start_node
            if n == stop_node:
                reconst_path = []

                while parents[n] != n:
                    reconst_path.append(n)
                    n = parents[n]

                reconst_path.append(start_node)

                reconst_path.reverse()

                if LOG:
                    print('Path found: {}'.format(reconst_path))
                
                total_dist = 0
                node = reconst_path[0]
                next = 1
                while node!=stop_node:
                    for adj,dist in self.adjacency_list[node]:
                        if adj == reconst_path[next]:
                            total_dist+=dist
                            next+=1
                            node=adj
                            break
                return reconst_path,total_dist

            # for all neighbors of the current node do
            for (m, weight) in self.get_neighbors(n):
                # if the current node isn't in both open_list and closed_list
                # add it to open_list and note n as it's parent
                if m not in open_list and m not in closed_list:
                    open_list.add(m)
                    parents[m] = n
                    g[m] = g[n] + weight

                # otherwise, check if it's quicker to first visit n, then m
                # and if it is, update parent data and g data
                # and if the node was in the closed_list, move it to open_list
                else:
                    if g[m] > g[n] + weight:
                        g[m] = g[n] + weight
                        parents[m] = n

                        if m in closed_list:
                            closed_list.remove(m)
                            open_list.add(m)

            # remove n from the open_list, and add it to closed_list
            # because all of his neighbors were inspected
            open_list.remove(n)
            closed_list.add(n)
        if LOG:
            print('Path does not exist!')
        return None, INF

def cal_deg(node ,next_node,node_data):
    nx,ny = node_data[next_node]
    x,y = node_data[node]
    # because in web map, y is opposite, y add negation
    vx,vy = nx-x , -(ny-y)
    # basic vector
    bx,by = -1,0

    vlen = math.sqrt(vx**2+vy**2)
    blen = math.sqrt(bx**2+by**2)
    deg = math.acos((vx*bx+vy*by)/(vlen*blen))

    if vy < 0:
        deg = 2*math.pi - deg
    
    if deg < 0:
        deg = (deg + 2*math.pi)
    if deg > 2*math.pi:
        deg = (deg - 2*math.pi)
    return math.floor(deg*180/math.pi)

# check_digraph(adjacentList)


#### default ####
map_graph_to_E1 = Graph(convertToGraph(nodes ,node_data,select_type,adjacentList),heuristic(nodes ,node_data,select_type,"E1"))
map_graph_to_E2 = Graph(convertToGraph(nodes ,node_data,select_type,adjacentList),heuristic(nodes ,node_data,select_type,"E2"))
# usage: map_graph_to_E1.a_star_algorithm('bedroom', 'E1')
# reconst_path,total_dist = map_graph_to_E1.a_star_algorithm('aisleA', 'E1')
# print(reconst_path,total_dist)
escape_next = {}

for detector in detectors:
    reconst_path1,dist1 =  map_graph_to_E1.a_star_algorithm(detector, 'E1')
    reconst_path2,dist2 =  map_graph_to_E2.a_star_algorithm(detector, 'E2')

    if dist1<=dist2:
       escape_next[detector]=reconst_path1[1]
    else:
       escape_next[detector]=reconst_path2[1]
if LOG:
    print("escape_next: ",escape_next)

escape_deg = {}
for node in detectors:
    escape_deg[node] = cal_deg(node,escape_next[node],node_data)
# print(escape_deg)

defualt_deg = escape_deg
defualt_next = escape_next
##### fire ####
map_graph_to_E1 = Graph(convertToGraph(nodes ,node_data,select_type,adjacentList),heuristic(nodes ,node_data,select_type,"E1"))
map_graph_to_E2 = Graph(convertToGraph(nodes ,node_data,select_type,adjacentList),heuristic(nodes ,node_data,select_type,"E2"))


import sys
try:
    f = open('./node-red/data/fire.txt','r')

    for place in f:
        try:
            map_graph_to_E1.fire(place)
            map_graph_to_E2.fire(place)
        except Exception as e:
            if LOG:
                print("when fire: ", e,file=sys.stderr)
    f.close()
except Exception as e:
    if LOG:
        print("when open file: ", e,file=sys.stderr)
escape_next = {}

for detector in detectors:
    reconst_path1,dist1 =  map_graph_to_E1.a_star_algorithm(detector, 'E1')
    reconst_path2,dist2 =  map_graph_to_E2.a_star_algorithm(detector, 'E2')

    if dist1 < dist2:
            escape_next[detector] = reconst_path1[1]
    elif dist1 > dist2:
        escape_next[detector] = reconst_path2[1]
    elif dist1== dist2==INF:
        escape_next[detector] = defualt_next[detector]
    elif LOG:
        print("ERROR:")
        print(reconst_path1,dist1)
        print(reconst_path2,dist2)
        print("------------------")
if LOG:
    print(detectors)
    print("escape_next: ",escape_next)

escape_deg = {}
for node in detectors:
    escape_deg[node] = cal_deg(node,escape_next[node],node_data)
print(escape_deg)
