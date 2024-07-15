import plotly.graph_objects as go

# returns an annotation object with the given text
def getAnnotation(text):
    return go.layout.Annotation(
        text=text,
        xref="paper", yref="paper",
        x=1.8, y=0.5,
        showarrow=False,
        bordercolor="black",
        borderwidth=0
    )

# returns the frames for polygon building animation
def create_pb_frames(x, y, vertices):
    frame_count = 30
    frames = [go.Frame(
        name=f'pb_frame_{j}',
        data=vertices + [go.Scatter(
            x=[x[i], x[i] + (x[(i + 1) % len(x)] - x[i]) * (j / frame_count)],
            y=[y[i], y[i] + (y[(i + 1) % len(x)] - y[i]) * (j / frame_count)],
            mode='lines',
            line=dict(color='black'),
            opacity=1,
            name='edge_{i}')
            for i in range(len(x))])
    for j in range(1, frame_count + 1)]

    return frames

# returns the frames for ear-clipping animation
def create_ec_frames(points, ec_steps, bp_copy, base_ec):
    frames = []
    triangle_index = 0
    triangles = []
    formed_triangles = []
    formed_edges = []
    base_triangles, base_ec_edges, base_ec_point = base_ec

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
                              base_triangles[triangle_index:] + blue_lines + base_ec_edges[2:] + base_ec_point,
                              name=f'ec_frame_{len(frames) + 1}'))

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
                    blue_line = go.Scatter(
                        x=[p[0], p[0] + (q[0] - p[0]) * j / 20],
                        y=[p[1], p[1] + (q[1] - p[1]) * j / 20],
                        mode='lines',
                        line=dict(color='blue'),
                        opacity=1,
                        name=f'ec_edge_{i}')

                    frames.append(go.Frame(data=bp_copy + formed_triangles + base_triangles[triangle_index:] + permanent_lines
                                            + [blue_line] + base_ec_edges[i + 1:] + base_ec_point,
                                            name=f'ec_frame_{len(frames) + 1}'))

            if step[0] == 2:
                lit_point = go.Scatter(
                    x=[step[2][0]],
                    y=[step[2][1]],
                    mode='markers',
                    marker=dict(color='red'),
                    opacity=1,
                    name='ec_point'
                )

                for k in range(40):
                    frames.append(go.Frame(data=bp_copy + formed_triangles +
                              base_triangles[triangle_index:] + permanent_lines + [lit_point],
                              name=f'ec_frame_{len(frames) + 1}'))

                frames.append(go.Frame(data=bp_copy + formed_triangles +
                              base_triangles[triangle_index:] + permanent_lines + base_ec_point,
                              name=f'ec_frame_{len(frames) + 1}'))

            else:
                triangles.append(triangle)
                p, q, r = tuple(triangle[:3])
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

                    pq_label = f'edge_{p_index}' if (q_index - p_index == 1) else f'triangle_{formed_edges.index([p, q])}'
                    qr_label = f'edge_{q_index}' if (r_index - q_index == 1) else f'triangle_{formed_edges.index([q, r])}'

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

                    bp_copy = bp_copy[:q_index] + [transparent_q] + bp_copy[q_index + 1:]

                    if 'edge' in pq_label:
                        bp_copy = bp_copy[:len(points) + p_index] + [transparent_pq] + bp_copy[len(points) + q_index:]
                    if 'edge' in qr_label:
                        bp_copy = bp_copy[:len(points) + q_index] + [transparent_qr] + bp_copy[len(points) + q_index + 1:]

                    if 'triangle' in pq_label:
                        index = int(pq_label[9:])
                        formed_triangles = formed_triangles[:index] + [transparent_pq] + formed_triangles[index + 1:]
                    if 'triangle' in qr_label:
                        index = int(qr_label[9:])
                        formed_triangles = formed_triangles[:index] + [transparent_qr] + formed_triangles[index + 1:]

                    frames.append(go.Frame(data=bp_copy + formed_triangles + [opaque_pr]
                                           + base_triangles[triangle_index + 1:] + base_ec_edges + base_ec_point,
                                           name=f'ec_frame_{len(frames) + 1}'))

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

        frames.append(go.Frame(data=bp_copy + formed_triangles + base_triangles[triangle_index:] +
                      base_ec_edges + base_ec_point,
                      name=f'ec_frame_{len(frames) + 1}'))
    
    return frames

# returns the frames for 3-coloring animation
def create_tc_frames(points, coloring_steps, base_ec, base_3c, triangles):
    colors = {0: "red", 1: "blue", 2: "yellow"}
    frames = []
    base_ec_triangles, base_ec_edges, base_ec_point = base_ec
    base_3c_triangle, tc_vertices = base_3c

    transparent_vertices = [go.Scatter(x=[points[i][0]], y=[points[i][1]],
                                       mode='markers', name=f'vertex_{i}', opacity=1, marker=dict(color='black'),
                                       showlegend=False) for i in range(len(points))]
    
    transparent_edges = [go.Scatter(x=[points[i][0], points[(i + 1) % len(points)][0]], y=[points[i][1], points[(i + 1) % len(points)][1]],
                                    mode='lines', name=f'edge_{i}', opacity=0, marker=dict(color='black'),
                                    showlegend=False, hoverinfo='skip') for i in range(len(points))]
    
    transparent_triangles = [go.Scatter(
        x=[p[0] for p in triangles[i]], y=[p[1] for p in triangles[i]],
        mode='lines', name=f'triangle_{i}', opacity=0.8, marker=dict(color='black'),
        showlegend=False, hoverinfo='skip') for i in range(len(triangles))]

    for step in coloring_steps:
        triangles, color_indices = step
        frame_data = transparent_vertices + transparent_edges + transparent_triangles
        frame_data = frame_data + base_ec_edges + base_ec_point
        x_triangle, y_triangle = zip(*triangles)
        x_triangle = list(x_triangle) + [x_triangle[0]]
        y_triangle = list(y_triangle) + [y_triangle[0]]

        for i in range(1, 6):
            frames.append(go.Frame(
                data=frame_data +
                [go.Scatter(x=x_triangle, y=y_triangle, mode='lines', line=dict(color='#FF4500', width=2), name=f'3c_triangle', opacity=i * 0.2)]
                + tc_vertices, name=f'tc_frame_{len(frames) + 1}'))

        for p, color_index in zip(triangles, color_indices):
            if (color_index is not None):
                color = colors[color_index]
                index = points.index(p)
                colored_vertex = go.Scatter(x=[p[0]], y=[p[1]], mode='markers', marker=dict(color=color, size=10), name=f'3c_vertex_{index}', opacity=1)
                tc_vertices = tc_vertices[:index] + [colored_vertex] + tc_vertices[index + 1:]

        for i in range(1, 6):
            frames.append(go.Frame(
                data=frame_data +
                [go.Scatter(x=x_triangle, y=y_triangle, mode='lines', line=dict(color='#FF4500', width=2), name=f'3c_triangle', opacity=1 - i * 0.2)]
                + tc_vertices, name=f'tc_frame_{len(frames) + 1}'))
        
        frames.append(go.Frame(data=frame_data + base_3c_triangle + tc_vertices, name=f'tc_frame_{len(frames) + 1}'))

    return frames

# returns the frames for minimal subsets animation
def create_ms_frames(points, visibility_sets, minimal_combinations, base_polygon, base_ec, base_3c):
    frames = []
    base_ec_triangles, base_ec_edges, base_ec_point = base_ec
    base_3c_triangle, base_3c_vertices = base_3c
    joined_ec3c = base_ec_triangles + base_ec_edges + base_ec_point + base_3c_triangle + base_3c_vertices
    fully_colored_edges = [go.Scatter(
        x=[points[i][0], points[(i + 1) % len(points)][0]],
        y=[points[i][1], points[(i + 1) % len(points)][1]],
        mode='lines',
        line=dict(color='blue', width=2),
        opacity=1,
        showlegend=False,
        name=f'edge_{i}'
    ) for i in range(len(points))]

    for combination in minimal_combinations:
        colored_edges = []
        bp_copy = base_polygon.copy()
        for v_index in combination:
            colored_vertex = go.Scatter(x=[points[v_index][0]], y=[points[v_index][1]], mode='markers', marker=dict(color='blue', size=10), name=f'vertex_{v_index}', opacity=1)
            bp_copy = bp_copy[:v_index] + [colored_vertex] + bp_copy[v_index + 1:]
            edges = []
            for e_index in range(len(points)):
                p = points[e_index]
                q = points[(e_index + 1) % len(points)]

                if e_index in colored_edges:
                    edges.append(go.Scatter(x=[p[0], q[0]], y=[p[1], q[1]], mode='lines', line=dict(color='blue', width=2), name=f'edge_{e_index}', opacity=1))
                    continue

                if e_index in visibility_sets[v_index]:
                    edges.append(go.Scatter(x=[p[0], q[0]], y=[p[1], q[1]], mode='lines', line=dict(color='blue', width=2), name=f'edge_{e_index}', opacity=1))
                    colored_edges.append(e_index)
                else:
                    edges.append(bp_copy[len(points) + e_index])
            
            frames.append(go.Frame(data=bp_copy[:len(points)] + edges + joined_ec3c, name=f'ms_frame_{len(frames) + 1}'))
        
        frames.append(go.Frame(data=bp_copy[:len(points)] + fully_colored_edges + joined_ec3c, name=f'ms_frame_{len(frames) + 1}'))
        frames.append(go.Frame(data=base_polygon + joined_ec3c, name=f'ms_frame_{len(frames) + 1}'))

    frames.append(go.Frame(data=base_polygon + joined_ec3c, name=f'ms_frame_{len(frames) + 1}'))
    return frames
