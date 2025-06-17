import tkinter as tk
import math
import random
from tkinter import Button, Frame

n1, n2, n3, n4 = 4, 2, 3, 0
num_peaks = 10 + n3
width = 800
height = 800

random.seed(f"{n1}{n2}{n3}{n4}")


def directed_matrix():
    k = 1 - n3 * 0.01 - n4 * 0.005 - 0.05
    matrix = []
    for i in range(num_peaks):
        row = []
        for j in range(num_peaks):
            element = random.uniform(0, 2) * k
            element = 0 if element < 1 else 1
            row.append(element)
        matrix.append(row)
    return matrix


def undirected_matrix(directed_matrix):
    undir_matrix = [[0] * num_peaks for _ in range(num_peaks)]
    for i in range(num_peaks):
        for j in range(i, num_peaks):
            if directed_matrix[i][j] == 1 or directed_matrix[j][i] == 1:
                undir_matrix[i][j] = 1
                undir_matrix[j][i] = 1
    return undir_matrix


def create_weight_matrix(undirected_matrix):
    B = [[random.uniform(0, 2) for _ in range(num_peaks)] for _ in range(num_peaks)]
    C = [[int(math.ceil(B[i][j] * 100 * undirected_matrix[i][j])) for j in range(num_peaks)] for i in range(num_peaks)]
    D = [[1 if C[i][j] > 0 else 0 for j in range(num_peaks)] for i in range(num_peaks)]
    H = [[1 if D[i][j] != D[j][i] else 0 for j in range(num_peaks)] for i in range(num_peaks)]
    Tr = [[1 if i < j else 0 for j in range(num_peaks)] for i in range(num_peaks)]
    W = [[0 for _ in range(num_peaks)] for _ in range(num_peaks)]
    for i in range(num_peaks):
        for j in range(num_peaks):
            if i == j:
                W[i][j] = 0
            elif C[i][j] > 0:
                weight = (D[i][j] + H[i][j] * Tr[i][j]) * C[i][j]
                W[i][j] = weight
                W[j][i] = weight

    return W


def print_matrix(matrix):
    max_digits = 0
    for row in matrix:
        for element in row:
            digits = len(str(element))
            max_digits = max(max_digits, digits)

    for row in matrix:
        formatted_row = [str(element).rjust(max_digits) for element in row]
        print("[" + ", ".join(formatted_row) + "]")
    print()


def arrow(canvas, lx, ly, rx, ry):
    canvas.create_line(lx, ly, rx, ry, fill="gray", width=2)

    angle = math.atan2(ry - ly, rx - lx)
    arrow_length = 12
    angle1 = angle + math.radians(20)
    angle2 = angle - math.radians(20)

    lx2 = rx - arrow_length * math.cos(angle1)
    ly2 = ry - arrow_length * math.sin(angle1)
    rx2 = rx - arrow_length * math.cos(angle2)
    ry2 = ry - arrow_length * math.sin(angle2)

    canvas.create_line(rx, ry, lx2, ly2, fill="gray", width=2)
    canvas.create_line(rx, ry, rx2, ry2, fill="gray", width=2)


def initialize_window():
    root = tk.Tk()
    root.title("Lab 6 by Mariia Khorunzha IM-42")
    root.geometry(f"{int(width)}x{int(height)}")
    canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas.pack()
    return root, canvas


class Graph:
    def __init__(self, num_vertices):
        self.vertices = num_vertices
        self.graph = []
        self.mst = []

    def add_edge(self, u, v, w):
        self.graph.append([u, v, w])

    def find(self, parent, i):
        if parent[i] == i:
            return i
        return self.find(parent, parent[i])

    def union(self, parent, rank, x, y):
        root_x = self.find(parent, x)
        root_y = self.find(parent, y)

        if rank[root_x] < rank[root_y]:
            parent[root_x] = root_y
        elif rank[root_x] > rank[root_y]:
            parent[root_y] = root_x
        else:
            parent[root_y] = root_x
            rank[root_x] += 1

    def kruskal_mst(self):
        result = []
        i, e = 0, 0

        self.graph = sorted(self.graph, key=lambda item: item[2])

        parent = []
        rank = []

        for node in range(self.vertices):
            parent.append(node)
            rank.append(0)

        steps = []

        while e < self.vertices - 1:
            if i >= len(self.graph):
                break

            u, v, w = self.graph[i]
            i += 1

            x = self.find(parent, u)
            y = self.find(parent, v)

            if x != y:
                e += 1
                result.append([u, v, w])
                steps.append([u, v, w])
                self.union(parent, rank, x, y)

        return steps


def create_weight_label(canvas, x, y, weight, bg_color="white", text_color="black"):
    padding = 3
    text_item = canvas.create_text(x, y, text=str(weight), font=("Arial", 10, "bold"), fill=text_color)

    bbox = canvas.bbox(text_item)

    rect_item = canvas.create_rectangle(
        bbox[0] - padding, bbox[1] - padding,
        bbox[2] + padding, bbox[3] + padding,
        fill=bg_color, outline="black", width=1
    )

    canvas.tag_lower(rect_item, text_item)

    return rect_item, text_item


def draw_graph(canvas, matrix, weight_matrix, positions=None, mst_edges=None, step_edge=None, directed=False,
               is_complete=False):
    canvas.delete("all")

    big_radius = 330
    center_x = width * 0.5
    center_y = height * 0.5

    nn = [str(i + 1) for i in range(num_peaks)]
    small_radius = 18

    if positions is None:
        positions = []
        for i in range(num_peaks):
            angle = 2 * math.pi * i / num_peaks
            x = center_x + big_radius * math.cos(angle)
            y = center_y + big_radius * math.sin(angle)
            positions.append((x, y))

    mst_vertices = set()
    if mst_edges:
        for u, v, _ in mst_edges:
            mst_vertices.add(u)
            mst_vertices.add(v)

    current_edge_vertices = set()
    if step_edge and not is_complete:
        current_edge_vertices.add(step_edge[0])
        current_edge_vertices.add(step_edge[1])

    def fix_len(x1, y1, x2, y2, radius):
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length == 0:
            return x1, y1, x2, y2
        scale = (length - radius) / length
        return x1 + dx * (1 - scale), y1 + dy * (1 - scale), x2 - dx * (1 - scale), y2 - dy * (1 - scale)

    for i in range(num_peaks):
        for j in range(num_peaks):
            if matrix[i][j] == 0:
                continue

            edge_color = "gray"
            edge_width = 2
            label_bg_color = "white"

            in_mst = mst_edges is not None and any(
                (i == u and j == v) or (j == u and i == v) for u, v, _ in mst_edges)
            if in_mst:
                edge_color = "green"
                edge_width = 3
                label_bg_color = "#CCFFCC"

            is_current_edge = step_edge is not None and (
                    (i == step_edge[0] and j == step_edge[1]) or (j == step_edge[0] and i == step_edge[1]))
            if is_current_edge and not is_complete:
                edge_color = "red"
                edge_width = 4
                label_bg_color = "#FFCCCC"

            x1, y1 = positions[i]

            if i == j:
                angle = 2 * math.pi * i / num_peaks
                loop_len = 50
                spread_angle = math.radians(30)

                x_start, y_start = x1 + math.cos(angle) * small_radius, y1 + math.sin(angle) * small_radius
                x_first, y_first = x1 + math.cos(angle) * (small_radius + 15), y1 + math.sin(angle) * (
                            small_radius + 15)
                x_mid, y_mid = x1 + math.cos(angle) * (small_radius + loop_len), y1 + math.sin(angle) * (
                            small_radius + loop_len)
                x_end, y_end = x1 + math.cos(angle + spread_angle) * (small_radius + loop_len), y1 + math.sin(
                    angle + spread_angle) * (small_radius + loop_len)

                for (x1_, y1_, x2_, y2_) in [(x_start, y_start, x_first, y_first),
                                             (x_first, y_first, x_mid, y_mid),
                                             (x_mid, y_mid, x_end, y_end)]:
                    canvas.create_line(x1_, y1_, x2_, y2_, fill=edge_color, width=edge_width)

                canvas.create_line(x_end, y_end, x_start, y_start, fill=edge_color, width=edge_width)

                continue

            if i > j and not directed:
                continue

            x2, y2 = positions[j]

            x1_, y1_, x2_, y2_ = fix_len(x1, y1, x2, y2, small_radius)

            canvas.create_line(x1_, y1_, x2_, y2_, fill=edge_color, width=edge_width)

            if directed:
                arrow(canvas, x1_, y1_, x2_, y2_)

            if weight_matrix[i][j] > 0:
                label_x = x1_ + (x2_ - x1_) / 4
                label_y = y1_ + (y2_ - y1_) / 4

                create_weight_label(canvas, label_x, label_y, weight_matrix[i][j], label_bg_color)

    for i, (x, y) in enumerate(positions):
        vertex_outline = "blue"
        vertex_fill = "white"

        if i in mst_vertices:
            vertex_fill = "#CCFFCC"

        if i in current_edge_vertices:
            vertex_outline = "red"
            vertex_fill = "#FFCCCC"

        canvas.create_oval(x - small_radius, y - small_radius, x + small_radius, y + small_radius,
                           outline=vertex_outline, width=2, fill=vertex_fill)
        canvas.create_text(x, y, text=nn[i], font=("Arial", 10, "bold"))


def main():
    root, canvas = initialize_window()

    matrix_dir = directed_matrix()
    print("The directed graph matrix has form:")
    print_matrix(matrix_dir)

    matrix_undir = undirected_matrix(matrix_dir)
    print("The undirected graph matrix has form:")
    print_matrix(matrix_undir)

    weight_matrix = create_weight_matrix(matrix_undir)
    print("The weight matrix has form:")
    print_matrix(weight_matrix)

    positions = []
    big_radius = 330
    center_x = width * 0.5
    center_y = height * 0.5
    for i in range(num_peaks):
        angle = 2 * math.pi * i / num_peaks
        x = center_x + big_radius * math.cos(angle)
        y = center_y + big_radius * math.sin(angle)
        positions.append((x, y))

    g = Graph(num_peaks)
    for i in range(num_peaks):
        for j in range(i + 1, num_peaks):
            if matrix_undir[i][j] == 1 and weight_matrix[i][j] > 0:
                g.add_edge(i, j, weight_matrix[i][j])

    kruskal_steps = g.kruskal_mst()

    draw_graph(canvas, matrix_undir, weight_matrix, positions)

    current_step = [0]
    mst_edges = []
    total_weight = [0]

    def next_step():
        if current_step[0] < len(kruskal_steps):
            edge = kruskal_steps[current_step[0]]
            mst_edges.append(edge)

            total_weight[0] += edge[2]

            is_last_step = current_step[0] == len(kruskal_steps) - 1

            draw_graph(canvas, matrix_undir, weight_matrix, positions, mst_edges, edge, is_complete=is_last_step)

            status_text.set(
                f"Step {current_step[0] + 1}/{len(kruskal_steps)}: Added edge {edge[0] + 1}-{edge[1] + 1} with weight {edge[2]} | Total MST Weight: {total_weight[0]}")
            current_step[0] += 1

        else:
            status_text.set(f"Minimum Spanning Tree completed! Total Weight: {total_weight[0]}")

    def reset():
        current_step[0] = 0
        mst_edges.clear()
        total_weight[0] = 0
        draw_graph(canvas, matrix_undir, weight_matrix, positions)
        status_text.set("Reset. Press Next to start Kruskal's algorithm")

    controls_frame = Frame(root)
    controls_frame.pack(side="bottom", pady=10)

    next_button = Button(controls_frame, text="Next Step", command=next_step)
    next_button.pack(side="left", padx=5)

    reset_button = Button(controls_frame, text="Reset", command=reset)
    reset_button.pack(side="left", padx=5)

    status_text = tk.StringVar()
    status_text.set("Press Next to start Kruskal's algorithm")
    status_label = tk.Label(root, textvariable=status_text, bd=1, relief="sunken", anchor="w", height=2)
    status_label.pack(side="bottom", fill="x")

    root.bind("<Right>", lambda event: next_step())
    root.bind("<space>", lambda event: next_step())
    root.bind("r", lambda event: reset())

    root.mainloop()


if __name__ == "__main__":
    main()