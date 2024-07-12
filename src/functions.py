# reads points from file and returns a list of them in (x, y) format
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

# generates combinations of [1, ..., n] with 1 to k elements
def generateCombinations(n, k):
    total_combinations = [[i] for i in range(n)]

    for depth in range(1, k):
        starting_index = total_combinations.index(list(range(0, depth)))
        current_combinations = total_combinations.copy()
        for c in current_combinations[starting_index:]:
            max_c = max(c)
            for i in range(max_c + 1, n):
                total_combinations.append(c + [i])
    
    return total_combinations

# determines if a list of points is in clockwise order, using the signed area of the polygon
def arePointsClockwise(points):
    n = len(points)
    area = 0

    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - y1 * x2
    
    return area < 0

# returns the cross product of vectors (p1, p2) and (p1, p3)
def crossProduct(p1, p2, p3):
    return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])

# determines whether point q is inside or in a border of the triangle (p1, p2, p3)
def isPointInTriangle(p1, p2, p3, q):
    cross12 = crossProduct(p1, p2, q)
    cross23 = crossProduct(p2, p3, q)
    cross31 = crossProduct(p3, p1, q)
    result = not (cross12 < 0 or cross23 < 0 or cross31 < 0)
    return result

# determines whether line segments (p1, p2) and (p3, p4) intersect
def doLinesIntersect(p1, p2, p3, p4):
    cross123 = crossProduct(p1, p2, p3)
    cross124 = crossProduct(p1, p2, p4)
    cross341 = crossProduct(p3, p4, p1)
    cross342 = crossProduct(p3, p4, p2)
    return cross123 * cross124 < 0 and cross341 * cross342 < 0

# determines if a line is completely outside the given polygon
def isLineOutside(points, i, j):
    # print (f"checking if line {i}, {j} is outside the polygon")
    if j - i == 1:
        return False

    turn_count = 0
    has_turned_right = False
    for k in range(i, j):
        # print (f"checking direction to {k}")
        cross = crossProduct(points[i], points[j], points[k])
        if cross != 0:
            turn_count += 1
        if cross < 0:
            # print ("right turn, line is not entirely outside")
            has_turned_right = True
    
    if not has_turned_right and turn_count > 0:
        # print ("line is entirely outside")
        return True

    turn_count = 0
    has_turned_right = False
    for k in range(j, i + len(points)):
        # print (f"checking direction to {k % len(points)}")
        cross = crossProduct(points[j], points[i], points[k % len(points)])
        if cross != 0:
            turn_count += 1
        if cross < 0:
            # print ("right turn, line is not entirely outside")
            has_turned_right = True
        
    if not has_turned_right and turn_count > 0:
        # print ("line is entirely outside")
        return True
    
    return False

# finds an ear in the given polygon
# an ear is a triangle, formed by 3 consecutive vertices, that doesn't contain other vertices
def findEar(points):
    steps = []
    # print (f"\nsearching for an ear with {len(points)} points remaining")
    for i in range(len(points) - 2):
        triangle = [points[i], points[i + 1], points[i + 2]]
        if crossProduct(points[i], points[i + 1], points[i + 2]) <= 0:
            steps.append([1, triangle, None, f"triangle {triangle} makes a right turn"])
            # print (f"next ear doesn't start with point {points[i]}")
            continue
        
        # print (f"considering triangle {points[i]}, {points[i + 1]}, {points[i + 2]}")
        possible = True
        for j in range(len(points)):
            if j in [i, i + 1, i + 2]:
                continue
            # print (f"considering point {points[j]}")
            if isPointInTriangle(points[i], points[i + 1], points[i + 2], points[j]):
                possible = False
                steps.append([2, triangle, points[j], f"triangle {triangle} contains point {points[j]}"])
                # print (f"point in triangle {points[i]}, {points[i + 1]}, {points[i + 2]}")
                break
        
        if possible:
            # print ("ear found: ", [points[i], points[i + 1], points[i + 2]])
            steps.append([0, triangle, None, f"triangle {triangle} is an ear"])
            return steps

# finds all ears in a given polygon
# returns the steps relevant to the animation
def earClipping(points):
    total_steps = []
    remaining_points = points.copy()

    while len(remaining_points) > 3:
        steps = findEar(remaining_points)
        remaining_points.remove(steps[-1][1][1])
        total_steps.extend(steps)
    
    total_steps.append([0, remaining_points, None, f"triangle {remaining_points} is an ear"])
    # print (f"\nfinal ear: {remaining_points}")
    return total_steps

# determines whether triangles t1 and t2 share an edge (i.e. two vertices)
def shareEdge(t1, t2):
    first = set(t1)
    second = set(t2)
    return len(first & second) == 2
 
# returns a graph (with adjacency lists) formed by the triangulation given by 'triangles'
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

# returns a graph (with adjacency lists) where triangles are vertices and edges represent an edge shared by two triangles
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

# 3-colors a triangle based on the vertices and colors given
def colorTriangle(p_vertices, p_colors, current_triangle):
    p0 = p_vertices.index(current_triangle[0])
    p1 = p_vertices.index(current_triangle[1])
    p2 = p_vertices.index(current_triangle[2])
    step = [current_triangle, [None] * 3]

    for i in range(len(p_vertices)):
        current_colors = [p_colors[p0], p_colors[p1], p_colors[p2]]
        if i in [p0, p1, p2] and p_colors[i] is None:
            for j in range(3):
                if j not in current_colors:
                    p_colors[i] = j
                    step[1][[p0, p1, p2].index(i)] = j
                    break
    
    return p_colors, step

# 3-colors all vertices in the given graph
# returns the steps relevant to the animation
def colorPointGraph(p_vertices, t_vertices, t_alists):
    p_colors = [None] * len(p_vertices)
    steps = []
    colored_triangles = []
    stack = [0]
    
    while (len(stack) > 0):
        current_index = stack[-1]
        p_colors, step = colorTriangle(p_vertices, p_colors, t_vertices[current_index])
        steps.append(step)
        colored_triangles.append(current_index)
        stack.pop()
        
        for i in t_alists[current_index]:
            if i not in colored_triangles:
                stack.append(i)

    return p_colors, steps

# returns a list containing the edges that each vertex completely sees
def generateVisibilitySets(points, edges):
    # print ("\ngenerating visibility sets")
    visible_vertices = []
    v_sets = []
    for i in range(len(points)):
        visible_vertices.append(set())
        v_sets.append(set())

    for i in range(len(points)):
        visible_vertices[i].add(i)
        visible_vertices[i].add((i + 1) % len(points))
        visible_vertices[(i + 1) % len(points)].add(i)
        
        for j in range(i + 2, len(points)):
            # print (f"\nchecking for interception for line {points[i]}, {points[j]}")
            sees_j = True
            for e in edges:
                if doLinesIntersect(points[i], points[j], e[0], e[1]):
                    # print (f"edge {e[0]}, {e[1]} intercepts them, {points[j]} not visible")
                    sees_j = False
                    break
                
            if sees_j:
                # print (f"no interceptions, checking for outside line")
                if not isLineOutside(points, i, j):
                    # print (f"line inside the polygon, {points[j]} visible")
                    visible_vertices[i].add(j)
                    visible_vertices[j].add(i)
                    continue
                # print (f"line {points[i]}, {points[j]} is outside the polygon, {points[j]} not visible")

    for i in range(len(points)):
        for j in range(len(points)):
            if j in visible_vertices[i] and (j + 1) % len(points) in visible_vertices[i]:
                v_sets[i].add(j)

    return v_sets

# determines the length of the smallest subset of vertices that still see the entire polygon and all subsets of that size
def findLowerBound(vertices, v_sets, upper_bound):
    # print (f"\ntrying to reduce vertices {vertices}")
    n_vertices = len(v_sets)
    lower_bound = None
    minimal_combinations = []
    combinations = generateCombinations(len(vertices), upper_bound)
    # print (f"generated {len(combinations)} combinations of {len(vertices)} vertices up to choose {upper_bound}")

    for c in combinations:
        # print (f"\ntesting combination {[vertices[i] for i in c]}")
        vertices_covered = set()

        if lower_bound is not None and len(c) > lower_bound:
            # print (f"combination has more points than the lower bound ({lower_bound}), returning\n")
            break

        for i in c:
            vertex = vertices[i]
            # print (f"edges covered by vertex {vertices[i]}: {v_sets[i]}")
            vertices_covered = vertices_covered.union(v_sets[vertex])

        # print (f"vertices covered: {vertices_covered}")
        if vertices_covered == set(range(n_vertices)):
            if lower_bound is None:
                # print (f"lower bound found: {len(c)}")
                lower_bound = len(c)
            
            # print(f"combination added")
            minimal_combinations.append([vertices[i] for i in c])
        
        vertices_covered.clear()
        
    return minimal_combinations

# returns the overall lower bound and all combinations of that size
def reduceUpperBound(pgraph_colors, visibility_sets):
    c0_vertices, c1_vertices, c2_vertices = ([], [], [])
    for i in range(len(pgraph_colors)):
        if pgraph_colors[i] == 0:
            c0_vertices.append(i)
        elif pgraph_colors[i] == 1:
            c1_vertices.append(i)
        else:
            c2_vertices.append(i)
    
    upper_bound = min(len(c0_vertices), len(c1_vertices), len(c2_vertices))
    minimal_c0_combinations = findLowerBound(c0_vertices, visibility_sets, upper_bound)
    minimal_c1_combinations = findLowerBound(c1_vertices, visibility_sets, upper_bound)
    minimal_c2_combinations = findLowerBound(c2_vertices, visibility_sets, upper_bound)
    lower_bound = min(len(minimal_c0_combinations[0]), len(minimal_c1_combinations[0]), len(minimal_c2_combinations[0]))

    minimal_combinations = []
    for mc in minimal_c0_combinations + minimal_c1_combinations + minimal_c2_combinations:
        if len(mc) == lower_bound:
            minimal_combinations.append(mc)

    return lower_bound, minimal_combinations
