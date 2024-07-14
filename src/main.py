from logicFunctions import *
from frameFunctions import *

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

x, y = zip(*points)

vertices = [go.Scatter(x=[x[i]], y=[y[i]], mode='markers', name=f'vertex_{i}', opacity=1, marker=dict(color='black')) for i in range(len(x))]
base_edges = [go.Scatter(x=[x[i]], y=[y[i]], mode='lines', name=f'edge_{i}', opacity=0, marker=dict(color='black')) for i in range(len(x))]
base_ec_edges = [go.Scatter(x=[1000], y=[1000], mode='lines', name=f'ec_edge_{i}', opacity=0, line=dict(color='red')) for i in range(3)]
base_ec_point = [go.Scatter(x=[1000], y=[1000], mode='markers', name=f'ec_point', opacity=0, marker=dict(color='red'))]
base_triangles = [go.Scatter(x=[1000], y=[1000], mode='lines', name=f'triangle_{i}', opacity=0, marker=dict(color='black')) for i in range(len(x) - 2)]
base_3c_triangle = [go.Scatter(x=[1000], y=[1000], mode='lines', name=f'3c_triangle', opacity=0, marker=dict(color='black'))]
base_3c_vertices = [go.Scatter(x=[x[i]], y=[y[i]], mode='lines', name=f'3c_vertex_{i}', opacity=0, line=dict(color='black')) for i in range(len(x))]

fig = go.Figure(
    data=vertices + base_edges + base_triangles +
    base_ec_edges + base_ec_point + base_3c_triangle + base_3c_vertices,
    layout=go.Layout(
        xaxis=dict(range=[min(x) - 6, max(x) + 6]),
        yaxis=dict(range=[min(y) - 3, max(y) + 3]),
        updatemenus=[dict(
            type="buttons",
            buttons=[dict(label="Play",
                          method="animate",
                          args=[
                              None,
                              {
                                "frame": {"duration": 10, "redraw": False},
                                "fromcurrent": True,
                                "transition": {"duration": 0},
                              }
                          ])])]
    )
)

pb_frames = create_pb_frames(x, y, vertices)

built_edges = [go.Scatter(
    x=[x[i], x[(i + 1) % len(x)]],
    y=[y[i], y[(i + 1) % len(x)]],
    mode='lines',
    line=dict(color='black'),
    opacity=1,
    name=f'edge_{i}') for i in range(len(x))]

built_polygon = vertices + built_edges
bp_copy = built_polygon.copy()
built_polygon_frame = go.Frame(data=built_polygon + base_triangles + base_ec_edges + base_ec_point + base_3c_triangle + base_3c_vertices)

built_triangles = [go.Scatter(
        x=[p[0] for p in triangle],
        y=[p[1] for p in triangle],
        mode='lines',
        line=dict(color='black'),
        opacity=1,
        name=f'triangle_{i}'
    ) for i, triangle in enumerate(triangles)]

built_triangles_frame = go.Frame(data=built_polygon + built_triangles + base_ec_edges + base_ec_point + base_3c_triangle + base_3c_vertices)

base_ec = base_ec_edges, base_ec_point, base_triangles
base_3c = base_3c_triangle, base_3c_vertices
ec_frames = create_ec_frames([(x[i], y[i]) for i in range(len(x))], ec_steps, bp_copy, base_ec)
# coloring_frames = create_coloring_frames(coloring_steps, bp_copy, base_ec, base_3c, built_triangles.copy())

fig.frames = list(fig.frames) + pb_frames + [built_polygon_frame] + ec_frames + [built_triangles_frame]
fig.show()
