class Astar:

    def __init__(self, matrix):
        self.mat = self.prepare_matrix(matrix)
        self.all_directions = [(1,0,0), (0,1,0), (-1,0,0), (0,-1,0), (0,0,1), (0,0,-1)]
        # self.all_directions = [(1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1)]

    class Node:
        def __init__(self, x, y, z, weight=0):
            self.x = x
            self.y = y
            self.z = z
            self.weight = weight
            self.heuristic = 0
            self.g = 0
            self.f = self.g+self.heuristic
            self.parent = None

        def __repr__(self):
            # return str(self.weight)
            return '('+str(self.x)+', '+str(self.y)+', '+str(self.z)+')'

    def prepare_matrix(self, mat):
        matrix_for_astar = []
        for x, line in enumerate(mat):
            tmp_line = []
            for y, col in enumerate(line):
                tmp_layer = []
                for z, weight in enumerate(col):
                    tmp_layer.append(self.Node(x, y, z, weight=weight))
                tmp_line.append(tmp_layer)
            matrix_for_astar.append(tmp_line)
        return matrix_for_astar

    def equal(self, current, end):
        return current.x == end.x and current.y == end.y

    def heuristic(self, current, other):
        return abs(current.x - other.x) + abs(current.y - other.y)


    def get_directions_from_action(self, act_idx, current):

        dx = current.x-current.parent.x
        dy = current.y-current.parent.y

        d_idx = (self.all_directions.index((dx, dy))+act_idx-1)%len(self.all_directions)

        return self.all_directions[d_idx]

    def neighbours(self, matrix, current):

        neighbours_list = []

        # self.all_directions = [(1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1)]
        # if current.parent is None:
        #     for d in self.all_directions:
        #         if 0<=current.x+d[0]<len(matrix) and 0<=current.y+d[1]<len(matrix[0]):
        #             if matrix[current.x+d[0]][current.y+d[1]].weight!=1:
        #                 neighbours_list.append(matrix[current.x+d[0]][current.y+d[1]])  
        # else:
        #     num_actions = 3
        #     for i in range(num_actions):
        #         d = self.get_directions_from_action(i, current)
        #         if 0<=current.x+d[0]<len(matrix) and 0<=current.y+d[1]<len(matrix[0]):
        #             if matrix[current.x+d[0]][current.y+d[1]].weight!=1:
        #                 neighbours_list.append(matrix[current.x+d[0]][current.y+d[1]])
        
        for d in self.all_directions:
            if 0<=current.x+d[0]<len(matrix) and 0<=current.y+d[1]<len(matrix[0]) and 0<=current.z+d[2]<len(matrix[0][0]):
                if matrix[current.x+d[0]][current.y+d[1]][current.z+d[2]].weight==0:
                    neighbours_list.append(matrix[current.x+d[0]][current.y+d[1]][current.z+d[2]])
        return neighbours_list

    def build(self, end):
        node_tmp = end
        path = []
        while (node_tmp):
            path.append([node_tmp.x, node_tmp.y, node_tmp.z])
            node_tmp = node_tmp.parent
        return list(reversed(path))

    def run(self, point_start, point_end):
        matrix = self.mat
        start = self.Node(point_start[0], point_start[1], point_start[2])
        end = self.Node(point_end[0], point_end[1], point_end[2])
        closed_list = []
        open_list = [start]

        while open_list:
            # current_node = open_list.pop()
            current_node = open_list[0]

            for node in open_list:
                if node.f < current_node.f:
                    current_node = node

            if self.equal(current_node, end):
                return self.build(current_node)

            for node in open_list:
                if self.equal(current_node, node):
                    open_list.remove(node)
                    break

            closed_list.append(current_node)

            for neighbour in self.neighbours(matrix, current_node):
                g = current_node.g + 1
                h = self.heuristic(neighbour, end)
                f = g+h

                if neighbour in closed_list or neighbour in open_list:
                    if f>neighbour.f:
                        continue

                neighbour.g = g
                neighbour.heuristic = h
                neighbour.f = f
                neighbour.parent = current_node
                if neighbour not in open_list:
                    open_list.append(neighbour)

        return None

