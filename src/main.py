from logicFunctions import *
from frameFunctions import *
from texts import *

points = []
with open("points.txt") as points_file:
    points = readPoints(points_file)
x, y = zip(*points)

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

vertices = [go.Scatter(x=[x[i]], y=[y[i]], mode='markers', name=f'vertex_{i}', opacity=1, marker=dict(color='black'), showlegend=False) for i in range(len(x))]
base_edges = [go.Scatter(x=[x[i]], y=[y[i]], mode='lines', name=f'edge_{i}', opacity=0, marker=dict(color='black'), showlegend=False) for i in range(len(x))]
base_ec_edges = [go.Scatter(x=[1000], y=[1000], mode='lines', name=f'ec_edge_{i}', opacity=0, line=dict(color='red'), showlegend=False) for i in range(3)]
base_ec_point = [go.Scatter(x=[1000], y=[1000], mode='markers', name=f'ec_point', opacity=0, marker=dict(color='red'), showlegend=False)]
base_triangles = [go.Scatter(x=[1000], y=[1000], mode='lines', name=f'triangle_{i}', opacity=0, marker=dict(color='black'), showlegend=False) for i in range(len(x) - 2)]
base_3c_triangle = [go.Scatter(x=[1000], y=[1000], mode='lines', name=f'3c_triangle', opacity=0, marker=dict(color='black'), showlegend=False)]
base_3c_vertices = [go.Scatter(x=[x[i]], y=[y[i]], mode='lines', name=f'3c_vertex_{i}', opacity=0, line=dict(color='black'), showlegend=False) for i in range(len(x))]

fig = go.Figure(data=vertices + base_edges + base_triangles +
    base_ec_edges + base_ec_point + base_3c_triangle + base_3c_vertices,
    layout=go.Layout(
        xaxis=dict(range=[min(x) - 6, max(x) + 6]),
        yaxis=dict(range=[min(y) - 3, max(y) + 3]))
)

pb_frames = create_pb_frames(x, y, vertices)
pb_frame_count = len(pb_frames)

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
ec_frame_count = len(ec_frames)

# tc_frames = create_tc_frames(coloring_steps, bp_copy, base_ec, base_3c, built_triangles.copy())
# tc_frame_count = len(tc_frames)

# ms_frames = create_ms_frames()
# ms_frame_count = len(ms_frames)

checkpoint_frames = [
    {
        'name': 'start_frame',
        'data': vertices + base_edges,
        'layout': {'annotations': [getAnnotation(start_text)]},
    },
    {
        'name': 'pb_frame_0',
        'data': vertices + base_edges,
        'layout': {'annotations': [getAnnotation(bp_text)]},
    },
    {
        'name': 'ec_frame_0',
        'data': built_polygon,
        'layout': {'annotations': [getAnnotation(ec_text)]},
    },
    {
        'name': 'tc_frame_0',
        'data': built_triangles,
        'layout': {'annotations': [getAnnotation(tc_text)]},
    },
    {
        'name': 'ms_frame_0',
        'data': [],
        'layout': {'annotations': [getAnnotation(ms_text)]},
    }
]

fig.frames = checkpoint_frames + pb_frames + [built_polygon_frame] + ec_frames + [built_triangles_frame]

fig.update_layout(
    annotations=[getAnnotation(start_text)],
    updatemenus=[
        {
            'buttons': [
                {
                    'label': 'Start<br>Início',
                    'method': 'animate',
                    'args': [['start_frame'], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate'}],
                },
                {
                    'label': 'Build Polygon<br>Construir Polígono',
                    'method': 'animate',
                    'args': [[f'pb_frame_{i}' for i in range(pb_frame_count + 1)], {'frame': {'duration': 10, 'redraw': False}, 'mode': 'immediate'}],
                },
                {
                    'label': 'Ear-Clipping<br>Corte-de-Orelhas',
                    'method': 'animate',
                    'args': [[f'ec_frame_{i}' for i in range(ec_frame_count + 1)], {'frame': {'duration': 10, 'redraw': False}, 'mode': 'immediate'}],
                },
                {
                    'label': '3-Coloring<br>3-Coloração',
                    'method': 'animate',
                    'args': ['tc_frame_0', {'frame': {'duration': 10, 'redraw': False}, 'mode': 'immediate'}],
                },
                {
                    'label': 'Minimal Subsets<br>Subconjuntos Mínimos',
                    'method': 'animate',
                    'args': [['ms_frame_0'], {'frame': {'duration': 10, 'redraw': False}, 'mode': 'immediate'}],
                }
            ],
            'direction': 'right',
            'x': 0.5,
            'y': -0.2,
        },
    ],
    margin=dict(r=600, b=150)
)

fig.show()
