from functions import *
import plotly.graph_objects as go

from dataGenerator import get_coloring_steps

points = []
with open("points.txt") as points_file:
    points = readPoints(points_file)

edges = []
for i in range(len(points)):
    edges.append((points[i], points[(i + 1) % len(points)]))

x, y = zip(*points)

# x = [0, 1, 2, 7, 5, 3, 4, -10, -10, -6, -1, -2]
# y = [0, 1, 4, 8, 9, 10, 15, 18, 0, 11, 7, 1]

vertices = [go.Scatter(x=[x[i]], y=[y[i]], mode='markers', name=f'vertex_{
                       i}', opacity=1, marker=dict(color='black')) for i in range(len(x))]
base_edges = [go.Scatter(x=[x[i]], y=[y[i]], mode='lines', name=f'edge_{
                         i}', opacity=1, marker=dict(color='black')) for i in range(len(x))]
base_ec_edges = [go.Scatter(x=[1000], y=[1000], mode='lines', name=f'ec_edge_{
                            i}', opacity=0, line=dict(color='red')) for i in range(3)]
base_ec_point = [go.Scatter(x=[1000], y=[
                            1000], mode='markers', name=f'ec_point', opacity=0, marker=dict(color='red'))]
base_triangles = [go.Scatter(x=[1000], y=[1000], mode='lines', name=f'triangle_{
                             i}', opacity=0, marker=dict(color='black')) for i in range(len(x) - 2)]
coloring_triangle = [go.Scatter(x=[1000], y=[
                                1000], mode='lines', name=f'3c_triangle', opacity=0, marker=dict(color='black'))]
coloring_points = [go.Scatter(x=[x[i]], y=[y[i]], mode='lines', name=f'edge_{
    i}', opacity=1, marker=dict(color='black')) for i in range(len(x))]

fig = go.Figure(
    data=vertices + base_edges + base_triangles +
    base_ec_edges + base_ec_point + coloring_triangle + coloring_points,
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

polygon_building_frames = [go.Frame(data=vertices + [go.Scatter(
    x=[x[i], x[i] + (x[(i + 1) % len(x)] - x[i]) * (j / 20)],
    y=[y[i], y[i] + (y[(i + 1) % len(x)] - y[i]) * (j / 20)],
    mode='lines',
    line=dict(color='black'),
    name='edge_{i}')
    for i in range(len(x))]
    + base_ec_edges + base_ec_point) for j in range(1, 21)]

built_edges = [go.Scatter(
    x=[x[i], x[(i + 1) % len(x)]],
    y=[y[i], y[(i + 1) % len(x)]],
    mode='lines',
    line=dict(color='black'),
    opacity=1,
    name=f'edge_{i}') for i in range(len(x))]

built_polygon = vertices + built_edges
fig.frames = list(fig.frames) + polygon_building_frames + \
    [go.Frame(data=built_polygon + base_triangles +
              base_ec_edges + base_ec_point)]
bp_copy = built_polygon.copy()


def create_ec_frames(points, ec_steps, bp_copy):
    frames = []
    triangle_index = 0
    triangles = []
    formed_triangles = []
    formed_edges = []

    for step in ec_steps:
        permanent_lines = []
        triangle = step[1]

        if step[0] == 1:
            p, q, r = tuple(triangle)

            for j in range(60):
                blue_lines = []

                if j // 20 == 0:
                    blue_lines.append(go.Scatter(
                        x=[p[0], p[0] + (q[0] - p[0]) * (j + 1) / 20],
                        y=[p[1], p[1] + (q[1] - p[1]) * (j + 1) / 20],
                        mode='lines',
                        line=dict(color='blue'),
                        opacity=1,
                        name=f'ec_edge_0'))

                elif j // 20 == 1:
                    blue_lines.append(go.Scatter(
                        x=[p[0], q[0]],
                        y=[p[1], q[1]],
                        mode='lines',
                        line=dict(color='blue'),
                        opacity=1,
                        name=f'ec_edge_0'))

                    blue_lines.append(go.Scatter(
                        x=[q[0], q[0] + (r[0] - q[0]) * ((j + 1) % 20) / 20],
                        y=[q[1], q[1] + (r[1] - q[1]) * ((j + 1) % 20) / 20],
                        mode='lines',
                        line=dict(color='blue'),
                        opacity=1,
                        name=f'ec_edge_1'))

                else:
                    blue_lines.append(go.Scatter(
                        x=[p[0] + (q[0] - p[0]) * (j % 20 + 1) / 20, q[0]],
                        y=[p[1] + (q[1] - p[1]) * (j % 20 + 1) / 20, q[1]],
                        mode='lines',
                        line=dict(color='blue'),
                        opacity=1,
                        name=f'ec_edge_0'))

                    blue_lines.append(go.Scatter(
                        x=[q[0], q[0] + (r[0] - q[0]) * (19 - j % 20) / 20],
                        y=[q[1], q[1] + (r[1] - q[1]) * (19 - j % 20) / 20],
                        mode='lines',
                        line=dict(color='blue'),
                        opacity=1,
                        name=f'ec_edge_1'))

                frames.append(go.Frame(data=bp_copy + formed_triangles +
                              base_triangles[triangle_index:] + blue_lines + base_ec_edges[2:] + base_ec_point))

        else:
            for i in range(4):
                p = triangle[i % 3]
                q = triangle[(i + 1) % 3]

                if i > 0:
                    permanent_lines.append(go.Scatter(
                        x=[triangle[i - 1][0], triangle[i % 3][0]],
                        y=[triangle[i - 1][1], triangle[i % 3][1]],
                        mode='lines+markers',
                        line=dict(color='blue'),
                        marker=dict(color='blue'),
                        opacity=1,
                        name=f"ec_edge_{i - 1}"))

                    if i == 3:
                        break

                for j in range(1, 21):
                    red_line = go.Scatter(
                        x=[p[0], p[0] + (q[0] - p[0]) * j / 20],
                        y=[p[1], p[1] + (q[1] - p[1]) * j / 20],
                        mode='lines',
                        line=dict(color='blue'),
                        opacity=1,
                        name=f'ec_edge_{i}')

                    frames.append(go.Frame(data=bp_copy + formed_triangles + base_triangles[triangle_index:] + permanent_lines + [
                                  red_line] + base_ec_edges[i + 1:] + base_ec_point))

            if step[0] == 2:
                lit_point = go.Scatter(
                    x=[step[2][0]],
                    y=[step[2][1]],
                    mode='markers',
                    marker=dict(color='red'),
                    opacity=1,
                    name='ec_point'
                )

                frames.extend([go.Frame(data=bp_copy + formed_triangles +
                              base_triangles[triangle_index:] + permanent_lines + [lit_point])] * 40)
                frames.append(go.Frame(data=bp_copy + formed_triangles +
                              base_triangles[triangle_index:] + permanent_lines + base_ec_point))

            else:
                triangles.append(triangle)
                p, q, r = tuple(triangle)
                p_index = points.index(p)
                q_index = points.index(q)
                r_index = points.index(r)

                for j in range(1, 21):
                    transparent_q = go.Scatter(
                        x=[q[0]],
                        y=[q[1]],
                        mode='markers',
                        marker=dict(color='black'),
                        opacity=1 - 0.03 * j,
                        name=f'vertex_{q_index}'
                    )

                    pq_label = f'edge_{p_index}' if (
                        q_index - p_index == 1) else f'triangle_{formed_edges.index([p, q])}'
                    qr_label = f'edge_{q_index}' if (
                        r_index - q_index == 1) else f'triangle_{formed_edges.index([q, r])}'

                    transparent_pq = go.Scatter(
                        x=[p[0], q[0]],
                        y=[p[1], q[1]],
                        mode='lines',
                        line=dict(color='black'),
                        opacity=1 - 0.03 * j,
                        name=pq_label
                    )

                    transparent_qr = go.Scatter(
                        x=[q[0], r[0]],
                        y=[q[1], r[1]],
                        mode='lines',
                        line=dict(color='black'),
                        opacity=1 - 0.03 * j,
                        name=qr_label
                    )

                    opaque_pr = go.Scatter(
                        x=[p[0], r[0]],
                        y=[p[1], r[1]],
                        mode='lines',
                        line=dict(color='black'),
                        opacity=j / 20,
                        name=f'triangle_{triangle_index}'
                    )

                    bp_copy = bp_copy[:q_index] + \
                        [transparent_q] + bp_copy[q_index + 1:]

                    if 'edge' in pq_label:
                        bp_copy = bp_copy[:len(
                            points) + p_index] + [transparent_pq] + bp_copy[len(points) + q_index:]
                    if 'edge' in qr_label:
                        bp_copy = bp_copy[:len(
                            points) + q_index] + [transparent_qr] + bp_copy[len(points) + q_index + 1:]

                    if 'triangle' in pq_label:
                        index = int(pq_label[9:])
                        formed_triangles = formed_triangles[:index] + [
                            transparent_pq] + formed_triangles[index + 1:]
                    if 'triangle' in qr_label:
                        index = int(qr_label[9:])
                        formed_triangles = formed_triangles[:index] + [
                            transparent_qr] + formed_triangles[index + 1:]

                    frames.append(go.Frame(data=bp_copy + formed_triangles + [
                                  opaque_pr] + base_triangles[triangle_index:] + base_ec_edges + base_ec_point))

                formed_edges.append([p, r])
                formed_triangles.append(go.Scatter(
                    x=[p[0], r[0]],
                    y=[p[1], r[1]],
                    mode='lines',
                    line=dict(color='black'),
                    opacity=1,
                    name=f'triangle_{triangle_index}'
                ))
                triangle_index += 1

        frames.append(go.Frame(data=bp_copy + formed_triangles +
                      base_ec_edges + base_ec_point))

    built_triangles = [go.Scatter(
        x=[p[0] for p in triangle],
        y=[p[1] for p in triangle],
        mode='lines',
        line=dict(color='black'),
        opacity=1,
        name=f'triangle_{i}'
    ) for i, triangle in enumerate(triangles)]

    return (frames + [go.Frame(data=built_polygon + built_triangles + base_ec_edges + base_ec_point)], built_triangles)


def create_coloring_frames(coloring_steps, bp_copy, ec_triangles):
    colors = {0: "red", 1: "green", 2: "yellow"}

    # Criação dos frames
    frames = []

    vertex_colors = []
    for i, step in enumerate(coloring_steps):
        points, color_indices = step

        frame_data = []
        for trace in bp_copy + ec_triangles:
            updated_trace = trace.update(opacity=0.2)
            frame_data.append(updated_trace)

        x_triangle, y_triangle = zip(*points)
        x_triangle = list(x_triangle) + [x_triangle[0]]
        y_triangle = list(y_triangle) + [y_triangle[0]]

        frame_data.append(go.Scatter(
            x=x_triangle, y=y_triangle, mode='lines', line=dict(color='#FF4500', width=2),
            name=f'3c_triangle', opacity=40 / 40
        ))

        # # Adiciona cada ponto com a cor correta
        for (x, y), color_index in zip(points, color_indices):

            if (color_index is not None):
                color = colors[color_index]

                # frame_data.append(triangle)

                vertex_color = go.Scatter(
                    x=[x], y=[y], mode='markers', marker=dict(color=color, size=10), name=f'3c_vertex_{i}', opacity=1)

                vertex_colors.append(vertex_color)
                frame_data.append(vertex_color)

            for vColor in vertex_colors:
                frame_data.append(vColor)

        frames.extend([go.Frame(data=frame_data)] * 40)

    return frames


ec_steps = [[0, [(0.0, 0.0), (1.0, 1.0), (2.0, 4.0)], None, 'triangle [(0.0, 0.0), (1.0, 1.0), (2.0, 4.0)] is an ear'],
            [1, [(0.0, 0.0), (2.0, 4.0), (7.0, 8.0)], None,
             'triangle [(0.0, 0.0), (2.0, 4.0), (7.0, 8.0)] makes a right turn'],
            [0, [(2.0, 4.0), (7.0, 8.0), (5.0, 9.0)], None,
             'triangle [(2.0, 4.0), (7.0, 8.0), (5.0, 9.0)] is an ear'],
            [1, [(0.0, 0.0), (2.0, 4.0), (5.0, 9.0)], None,
             'triangle [(0.0, 0.0), (2.0, 4.0), (5.0, 9.0)] makes a right turn'],
            [0, [(2.0, 4.0), (5.0, 9.0), (3.0, 10.0)], None,
             'triangle [(2.0, 4.0), (5.0, 9.0), (3.0, 10.0)] is an ear'],
            [0, [(0.0, 0.0), (2.0, 4.0), (3.0, 10.0)], None,
             'triangle [(0.0, 0.0), (2.0, 4.0), (3.0, 10.0)] is an ear'],
            [0, [(0.0, 0.0), (3.0, 10.0), (4.0, 15.0)], None,
             'triangle [(0.0, 0.0), (3.0, 10.0), (4.0, 15.0)] is an ear'],
            [2, [(0.0, 0.0), (4.0, 15.0), (-10.0, 18.0)], (-6.0, 11.0),
             'triangle [(0.0, 0.0), (4.0, 15.0), (-10.0, 18.0)] contains point (-6.0, 11.0)'],
            [2, [(4.0, 15.0), (-10.0, 18.0), (-10.0, 0.0)], (-6.0, 11.0),
             'triangle [(4.0, 15.0), (-10.0, 18.0), (-10.0, 0.0)] contains point (-6.0, 11.0)'],
            [0, [(-10.0, 18.0), (-10.0, 0.0), (-6.0, 11.0)], None,
             'triangle [(-10.0, 18.0), (-10.0, 0.0), (-6.0, 11.0)] is an ear'],
            [2, [(0.0, 0.0), (4.0, 15.0), (-10.0, 18.0)], (-6.0, 11.0),
             'triangle [(0.0, 0.0), (4.0, 15.0), (-10.0, 18.0)] contains point (-6.0, 11.0)'],
            [0, [(4.0, 15.0), (-10.0, 18.0), (-6.0, 11.0)], None,
             'triangle [(4.0, 15.0), (-10.0, 18.0), (-6.0, 11.0)] is an ear'],
            [2, [(0.0, 0.0), (4.0, 15.0), (-6.0, 11.0)], (-1.0, 7.0),
             'triangle [(0.0, 0.0), (4.0, 15.0), (-6.0, 11.0)] contains point (-1.0, 7.0)'],
            [0, [(4.0, 15.0), (-6.0, 11.0), (-1.0, 7.0)], None,
             'triangle [(4.0, 15.0), (-6.0, 11.0), (-1.0, 7.0)] is an ear'],
            [0, [(0.0, 0.0), (4.0, 15.0), (-1.0, 7.0)], None,
             'triangle [(0.0, 0.0), (4.0, 15.0), (-1.0, 7.0)] is an ear'],
            [0, [(0.0, 0.0), (-1.0, 7.0), (-2.0, 1.0)], None, 'triangle [(0.0, 0.0), (-1.0, 7.0), (-2.0, 1.0)] is an ear']]

ec_frames, built_triangles = create_ec_frames([(x[i], y[i])
                                               for i in range(len(x))], ec_steps, bp_copy)

coloring_frames = create_coloring_frames(coloring_steps=get_coloring_steps(),
                                         bp_copy=bp_copy, ec_triangles=built_triangles.copy())

fig.frames = list(fig.frames) + ec_frames + coloring_frames

fig.show()
