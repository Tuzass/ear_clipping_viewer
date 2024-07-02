def readPoints(file):
    points = []

    for line in file:
        try:
            space_index = line.find(" ")
            x_coord = float(line[:space_index])
            y_coord = float(line[space_index + 1:])
            points.append((x_coord, y_coord))
        except:
            return "Invalid format!"
    
    return points

def arePointsClockwise(points):
    n = len(points)
    area = 0

    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - y1 * x2
    
    return area < 0

def crossProduct(p1, p2, p3):
    return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])

def isPointInTriangle(p1, p2, p3, q):
    cross12 = crossProduct(p1, p2, q)
    cross23 = crossProduct(p2, p3, q)
    cross31 = crossProduct(p3, p1, q)
    return not (cross12 < 0 or cross23 < 0 or cross31 < 0)

def doLinesIntersect(p1, p2, p3, p4):
    cross123 = crossProduct(p1, p2, p3)
    cross124 = crossProduct(p1, p2, p4)
    cross341 = crossProduct(p3, p4, p1)
    cross342 = crossProduct(p3, p4, p2)
    return cross123 * cross124 < 0 and cross341 * cross342 < 0

def findEar(points):
    for i in range(len(points) - 2):
        if crossProduct(points[i], points[i + 1], points[i + 2]) <= 0:
            continue
        
        for j in range(len(points)):
            if j in [i, i + 1, i + 2]:
                continue
            if isPointInTriangle(points[i], points[i + 1], points[i + 2], points[j]):
                continue
            return [points[i], points[i + 1], points[i + 2]]
    
    raise ValueError("defective polygon")

def earClipping(points):
    triangles = []
    remaining_points = points.copy()

    while len(remaining_points) > 3:
        triangle = findEar(remaining_points)
        remaining_points.remove(triangle[1])
        triangles.append(triangle)
    
    triangles.append(remaining_points)
    return triangles

def shareEdge(t1, t2):
    first = set(t1)
    second = set(t2)
    return len(first & second) == 2

def createPointGraph(points, triangles):
    vertices = points.copy()
    alists = []
    for i in range(len(vertices)):
        alists.append(set())
    
    for i in range(len(triangles)):
        t = triangles[i]
        p0 = points.index(t[0])
        p1 = points.index(t[1])
        p2 = points.index(t[2])
        alists[p0] = alists[p0] | {p1, p2}
        alists[p1] = alists[p1] | {p0, p2}
        alists[p2] = alists[p2] | {p0, p1}
    
    return vertices, alists

def createTriangleGraph(triangles):
    vertices = triangles.copy()
    alists = []
    for i in range(len(vertices)):
        alists.append([])
    
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            if shareEdge(vertices[i], vertices[j]):
                alists[i].append(j)
                alists[j].append(i)
    
    return vertices, alists

def colorTriangle(p_vertices, p_colors, current_triangle):
    p0 = p_vertices.index(current_triangle[0])
    p1 = p_vertices.index(current_triangle[1])
    p2 = p_vertices.index(current_triangle[2])

    for i in range(len(p_vertices)):
        current_colors = [p_colors[p0], p_colors[p1], p_colors[p2]]
        if i in [p0, p1, p2] and p_colors[i] is None:
            for j in range(3):
                if j not in current_colors:
                    p_colors[i] = j
                    break
    
    return p_colors

def colorPointGraph(p_vertices, t_vertices, t_alists):
    p_colors = [None] * len(p_vertices)
    colored_triangles = []
    stack = [0]
    
    while (len(stack) > 0):
        current_index = stack[-1]
        p_colors = colorTriangle(p_vertices, p_colors, t_vertices[current_index])
        colored_triangles.append(current_index)
        stack.pop()
        
        for i in t_alists[current_index]:
            if i not in colored_triangles:
                stack.append(i)

    return p_colors

def generateVisibilitySets(points, edges):
    v_sets = []
    for i in range(len(points)):
        v_sets.append(set())

    for i in range(len(points)):
        state = 0
        v_sets[i].add(i)
        v_sets[i].add((i + 1) % len(points))
        v_sets[(i + 1) % len(points)].add(i)
        
        for j in range(i + 2, len(points)):
            # print (f"\nchecking {points[i]} {points[j]}, current state is {state}")
            cross = crossProduct(points[j - 2], points[j - 1], points[j])

            if state != 1 and cross < 0:
                # print (f"state not 1 and right turn, {points[j]} not visible and state is -1")
                state = -1
                continue

            if state != -1 and cross >= 0:
                # print (f"state not -1 left/no turn, {points[j]} visible and state is 1")
                state = 1
                v_sets[i].add(j)
                v_sets[j].add(i)
                continue

            if (state == 1 and cross <= 0) or (state == -1 and cross >= 0):
                """
                if cross > 0:
                    print (f"right turn on state 1, testing for interception")
                else:
                    print (f"left turn on state -1, testing for interception")
                """

                sees_j = True
                for k in range(i, j - 1):
                    if doLinesIntersect(points[i], points[j], points[k], points[k + 1]):
                        # print (f"edge {points[k]} {points[k + 1]} intercepts them, {points[j]} not visible and state is -1")
                        state = -1
                        sees_j = False
                        break
                
                if sees_j:
                    # print (f"no interceptions: {points[j]} visible and state is 1")
                    v_sets[i].add(j)
                    v_sets[j].add(i)
                    state = 1
    
    return v_sets

with open("points.txt") as points_file:
    points = readPoints(points_file)

edges = []
for i in range(len(points)):
    edges.append((points[i], points[(i + 1) % len(points)]))

if arePointsClockwise(points):
    # print ("points in clockwise order -> reversing list")
    points.reverse()

triangles = earClipping(points)
pgraph_vertices, pgraph_adjacency_lists = createPointGraph(points, triangles)
tgraph_vertices, tgraph_adjacency_lists = createTriangleGraph(triangles)
pgraph_colors = colorPointGraph(pgraph_vertices, tgraph_vertices, tgraph_adjacency_lists)
visibility_sets = generateVisibilitySets(points, edges)

for i, v_set in enumerate(visibility_sets):
    print (i, "sees", v_set)

print ("\ntriangles:")
for triangle in triangles:
    print (triangle)
