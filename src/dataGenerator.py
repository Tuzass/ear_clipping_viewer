from functions import *

points = []
with open("points.txt") as points_file:
    points = readPoints(points_file)

edges = []
for i in range(len(points)):
    edges.append((points[i], points[(i + 1) % len(points)]))

if arePointsClockwise(points):
    # print ("points in clockwise order -> reversing list")
    points.reverse()

visibility_sets = generateVisibilitySets(points, edges)
# ec = ear-clipping
ec_steps = earClipping(points)

triangles = []
for step in ec_steps:
    if step[0] == 0:
        triangles.append(step[1])

# pgraph = point graph, tgraph = triangle graph
pgraph_vertices, pgraph_adjacency_lists = createPointGraph(points, triangles)
tgraph_vertices, tgraph_adjacency_lists = createTriangleGraph(triangles)
pgraph_colors, coloring_steps = colorPointGraph(pgraph_vertices, tgraph_vertices, tgraph_adjacency_lists)
lower_bound, minimal_combinations = reduceUpperBound(pgraph_colors, visibility_sets)

print (f"visibility-checking found a lower bound of {lower_bound} vertices")
for i, mc in enumerate(minimal_combinations):
    points_list = [str(points[j]) for j in mc]
    print (f"combination {i + 1}:", ", ".join(points_list))
