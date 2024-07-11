from functions import *

points = []
with open("points.txt") as points_file:
    points = readPoints(points_file)

edges = []
for i in range(len(points)):
    edges.append((points[i], points[(i + 1) % len(points)]))

if arePointsClockwise(points):
    print ("points in clockwise order -> reversing list")
    points.reverse()

visibility_sets = generateVisibilitySets(points, edges)
ec_steps = earClipping(points)
for step in ec_steps:
    print (step)

triangles = []
for step in ec_steps:
    if step[0] == 0:
        triangles.append(step[1])

pgraph_vertices, pgraph_adjacency_lists = createPointGraph(points, triangles)
tgraph_vertices, tgraph_adjacency_lists = createTriangleGraph(triangles)
pgraph_colors = colorPointGraph(pgraph_vertices, tgraph_vertices, tgraph_adjacency_lists)

color0_vertices = []
color1_vertices = []
color2_vertices = []
for i in range(len(pgraph_colors)):
    if pgraph_colors[i] == 0:
        color0_vertices.append(i)
    elif pgraph_colors[i] == 1:
        color1_vertices.append(i)
    else:
        color2_vertices.append(i)

upper_bound = min(len(color0_vertices), len(color1_vertices), len(color2_vertices))
minimal_color0_combinations = findLowerBound(color0_vertices, visibility_sets, upper_bound)
minimal_color1_combinations = findLowerBound(color1_vertices, visibility_sets, upper_bound)
minimal_color2_combinations = findLowerBound(color2_vertices, visibility_sets, upper_bound)
lower_bound = min(len(minimal_color0_combinations[0]), len(minimal_color1_combinations), len(minimal_color2_combinations[0]))

print (f"ear-clipping found {len(triangles)} triangles")
for i, triangle in enumerate(triangles):
    print (f"triangle {i + 1}:", ", ". join([str(point) for point in triangle]))

print (f"\n3-coloring found an upper bound of {upper_bound} vertices")
print ("color 0: ", ", ".join([str(points[i]) for i in color0_vertices]))
print ("color 1: ", ", ".join([str(points[i]) for i in color1_vertices]))
print ("color 2: ", ", ".join([str(points[i]) for i in color2_vertices]))

minimal_combinations = []
for mc in minimal_color0_combinations + minimal_color1_combinations + minimal_color2_combinations:
    if len(mc) == lower_bound:
        minimal_combinations.append(mc)

print (f"\nvisibility-checking found a lower bound of {lower_bound} vertices")
for i, mc in enumerate(minimal_combinations):
    points_list = [str(points[j]) for j in mc]
    print (f"combination {i + 1}:", ", ".join(points_list))
