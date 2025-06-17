import tkinter as tk
import math
import random
from collections import defaultdict

n1, n2, n3, n4 = 4, 2, 3, 0
num_peaks = 10 + n3
width = 800
height = 800

random.seed(f"{n1}{n2}{n3}{n4}")

def create_directed_matrix(k_formula=1):
    if k_formula == 1:
        k = 1.0 - n3 * 0.01 - n4 * 0.01 - 0.3
    else:
        k = 1.0 - n3 * 0.005 - n4 * 0.005 - 0.27
        
    matrix = []
    for i in range(num_peaks):
        row = []
        for j in range(num_peaks):
            element = random.uniform(0, 2.0) * k
            element = 0 if element < 1.0 else 1
            row.append(element)
        matrix.append(row)
    return matrix

def create_undirected_matrix(directed_matrix):
    undir_matrix = [[0] * num_peaks for _ in range(num_peaks)]
    for i in range(num_peaks):
        for j in range(i, num_peaks):
            if directed_matrix[i][j] == 1 or directed_matrix[j][i] == 1:
                undir_matrix[i][j] = 1
                undir_matrix[j][i] = 1
    return undir_matrix

def print_matrix(matrix, name="Matrix"):
    print(f"\n{name}:")
    for row in matrix:
        print(" ".join(str(element) for element in row))
    print()

def get_vertex_degrees(matrix, directed=False):
    if directed:
        out_degrees = []
        in_degrees = []
        total_degrees = []
        
        for i in range(num_peaks):
            out_deg = sum(matrix[i])
            in_deg = sum(matrix[j][i] for j in range(num_peaks))
            out_degrees.append(out_deg)
            in_degrees.append(in_deg)
            total_degrees.append(out_deg + in_deg)
            
        return total_degrees, out_degrees, in_degrees
    else:
        degrees = []
        for i in range(num_peaks):
            degrees.append(sum(matrix[i]))
        return degrees

def is_regular_graph(degrees):
    if not degrees:
        return False, 0
    
    if isinstance(degrees, tuple):
        degrees = degrees[0]
    
    first_degree = degrees[0]
    is_regular = all(d == first_degree for d in degrees)
    return is_regular, first_degree if is_regular else 0

def find_hanging_isolated_vertices(degrees, directed=False):
    hanging = []
    isolated = []
    
    if directed:
        total_degrees, out_degrees, in_degrees = degrees
        for i in range(num_peaks):
            if out_degrees[i] == 0 and in_degrees[i] == 0:
                isolated.append(i + 1)
            elif (out_degrees[i] == 1 and in_degrees[i] == 0) or (out_degrees[i] == 0 and in_degrees[i] == 1):
                hanging.append(i + 1)
    else:
        for i, degree in enumerate(degrees):
            if degree == 0:
                isolated.append(i + 1)
            elif degree == 1:
                hanging.append(i + 1)
    
    return hanging, isolated

def matrix_multiply(A, B):
    n = len(A)
    C = [[0 for _ in range(n)] for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C

def matrix_power(matrix, power):
    n = len(matrix)
    
    if power == 0:
        result = [[0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            result[i][i] = 1
        return result
    
    if power == 1:
        return [row[:] for row in matrix]
    
    if power % 2 == 0:
        half_power = matrix_power(matrix, power // 2)
        return matrix_multiply(half_power, half_power)
    else:
        return matrix_multiply(matrix, matrix_power(matrix, power - 1))


def find_paths(matrix, length):
    paths = []
    def find_path_rec(current, end, path, current_length):
        if current_length == length:
            if current == end:
                path_with_end = path + [end + 1]
                paths.append(path_with_end)
            return

        for next_v in range(num_peaks):
            if matrix[current][next_v] == 1:
                find_path_rec(next_v, end, path + [current + 1], current_length + 1)

    for start in range(num_peaks):
        for end in range(num_peaks):
            find_path_rec(start, end, [], 0)

    return paths


def calculate_reachability_matrix(matrix):
    n = len(matrix)
    reach_matrix = [row[:] for row in matrix]
    
    for i in range(n):
        reach_matrix[i][i] = 1
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach_matrix[i][k] and reach_matrix[k][j]:
                    reach_matrix[i][j] = 1
    
    return reach_matrix

def calculate_strong_connectivity_matrix(reach_matrix):
    n = len(reach_matrix)
    strong_matrix = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            strong_matrix[i][j] = reach_matrix[i][j] and reach_matrix[j][i]
    
    return strong_matrix

def find_strongly_connected_components(strong_matrix):
    n = len(strong_matrix)
    visited = [False] * n
    components = []
    
    for i in range(n):
        if not visited[i]:
            component = []
            for j in range(n):
                if strong_matrix[i][j] == 1:
                    component.append(j + 1)
                    visited[j] = True
            
            if component:
                components.append(component)
    
    return components

def create_condensation_graph(matrix, components):
    n = len(components)
    condensation_matrix = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if i != j:
                for v1 in [x-1 for x in components[i]]:
                    for v2 in [x-1 for x in components[j]]:
                        if matrix[v1][v2] == 1:
                            condensation_matrix[i][j] = 1
                            break
                    if condensation_matrix[i][j] == 1:
                        break
    
    return condensation_matrix

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

def initialize_window(title="Graph Visualization"):
    root = tk.Tk()
    root.title(title)
    root.geometry(f"{int(width)}x{int(height)}")
    canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas.pack()
    return root, canvas

def draw_graph(canvas, matrix, directed=False, title=""):
    canvas.delete("all")
    
    if title:
        canvas.create_text(width/2, 30, text=title, font=("Arial", 14, "bold"))
    
    big_radius = 250
    center_x = width * 0.5
    center_y = height * 0.5

    nn = [str(i + 1) for i in range(len(matrix))]
    small_radius = 16

    positions = []
    for i in range(len(matrix)):
        angle = 2 * math.pi * i / len(matrix)
        x = center_x + big_radius * math.cos(angle)
        y = center_y + big_radius * math.sin(angle)
        positions.append((x, y))

        canvas.create_oval(x - small_radius, y - small_radius, x + small_radius, y + small_radius, outline="blue", width=2)
        canvas.create_text(x, y, text=nn[i], font=("Arial", 10, "bold"))

    def fix_len(x1, y1, x2, y2, radius):
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length == 0:
            return x1, y1, x2, y2
        scale = (length - radius) / length
        return x1 + dx * (1 - scale), y1 + dy * (1 - scale), x2 - dx * (1 - scale), y2 - dy * (1 - scale)

    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i][j]:
                x1, y1 = positions[i]
                x2, y2 = positions[j]

                if i == j:
                    angle = 2 * math.pi * i / len(matrix)
                    loop_len = 50
                    spread_angle = math.radians(30)

                    x_start, y_start = x1 + math.cos(angle) * small_radius, y1 + math.sin(angle) * small_radius
                    x_first, y_first = x1 + math.cos(angle) * (small_radius + 15), y1 + math.sin(angle) * (small_radius + 15)
                    x_mid, y_mid = x1 + math.cos(angle) * (small_radius + loop_len), y1 + math.sin(angle) * (small_radius + loop_len)
                    x_end, y_end = x1 + math.cos(angle + spread_angle) * (small_radius + loop_len), y1 + math.sin(angle + spread_angle) * (small_radius + loop_len)

                    for (x1, y1, x2, y2) in [(x_start, y_start, x_first, y_first), (x_first, y_first, x_mid, y_mid),
                                             (x_mid, y_mid, x_end, y_end)]:
                        canvas.create_line(x1, y1, x2, y2, fill="gray", width=2)
                    if directed:
                        arrow(canvas, x_end, y_end, x_start, y_start)
                    else:
                        canvas.create_line(x_end, y_end, x_start, y_start, fill="gray", width=2)
                else:
                    x1, y1, x2, y2 = fix_len(x1, y1, x2, y2, small_radius)
                    if directed:
                        arrow(canvas, x1, y1, x2, y2)
                    else:
                        canvas.create_line(x1, y1, x2, y2, fill="gray", width=2)

def main():
    root, canvas = initialize_window("Lab 4 by Mariia Khorunzha IM-42")
    
    print(f"Variant: {n1}{n2}{n3}{n4}")
    print(f"Number of vertices: {num_peaks}")
    
    matrix_dir1 = create_directed_matrix(k_formula=1)
    print_matrix(matrix_dir1, "Directed Graph Matrix (First Formula)")
    
    matrix_undir1 = create_undirected_matrix(matrix_dir1)
    print_matrix(matrix_undir1, "Undirected Graph Matrix")
    
    dir_degrees = get_vertex_degrees(matrix_dir1, directed=True)
    total_degrees, out_degrees, in_degrees = dir_degrees
    
    print("\nDirected Graph Vertex Properties:")
    print("Vertex: " + ", ".join(f"{i+1}" for i in range(num_peaks)))
    print("Total:  " + ", ".join(f"{total_degrees[i]}" for i in range(num_peaks)))
    print("Out:    " + ", ".join(f"{out_degrees[i]}" for i in range(num_peaks)))
    print("In:     " + ", ".join(f"{in_degrees[i]}" for i in range(num_peaks)))
    
    undir_degrees = get_vertex_degrees(matrix_undir1, directed=False)
    print("\nUndirected Graph Vertex Degrees:")
    print("Vertex: " + ", ".join(f"{i+1}" for i in range(num_peaks)))
    print("Degree: " + ", ".join(f"{undir_degrees[i]}" for i in range(num_peaks)))
    
    is_dir_regular, dir_reg_degree = is_regular_graph(dir_degrees)
    is_undir_regular, undir_reg_degree = is_regular_graph(undir_degrees)
    
    print("\nGraph Regularity:")
    print(f"Directed graph regular: {is_dir_regular}")
    if is_dir_regular:
        print(f"Regularity degree: {dir_reg_degree}")
    
    print(f"Undirected graph regular: {is_undir_regular}")
    if is_undir_regular:
        print(f"Regularity degree: {undir_reg_degree}")
    
    dir_hanging, dir_isolated = find_hanging_isolated_vertices(dir_degrees, directed=True)
    undir_hanging, undir_isolated = find_hanging_isolated_vertices(undir_degrees, directed=False)
    
    print("\nHanging and Isolated Vertices:")
    print(f"Directed graph hanging vertices: {dir_hanging or 'None'}")
    print(f"Directed graph isolated vertices: {dir_isolated or 'None'}")
    print(f"Undirected graph hanging vertices: {undir_hanging or 'None'}")
    print(f"Undirected graph isolated vertices: {undir_isolated or 'None'}")
    
    matrix_dir2 = create_directed_matrix(k_formula=2)
    print_matrix(matrix_dir2, "New Directed Graph Matrix (Second Formula)")
        
    dir2_degrees = get_vertex_degrees(matrix_dir2, directed=True)
    total_degrees2, out_degrees2, in_degrees2 = dir2_degrees
    
    print("\nNew Directed Graph Vertex Properties:")
    print("Vertex: " + ", ".join(f"{i+1}" for i in range(num_peaks)))
    print("Total:  " + ", ".join(f"{total_degrees2[i]}" for i in range(num_peaks)))
    print("Out:    " + ", ".join(f"{out_degrees2[i]}" for i in range(num_peaks)))
    print("In:     " + ", ".join(f"{in_degrees2[i]}" for i in range(num_peaks)))
    
    paths2 = find_paths(matrix_dir2, 2)
    paths3 = find_paths(matrix_dir2, 3)
    
    print(f"\nPaths of length 2 ({len(paths2)} paths):")
    for path in paths2:
        path_str = " -> ".join(str(v) for v in path)
        print(path_str)
    
    print(f"\nPaths of length 3 ({len(paths3)} paths):")
    for path in paths3:
        path_str = " -> ".join(str(v) for v in path)
        print(path_str)
    
    reach_matrix = calculate_reachability_matrix(matrix_dir2)
    print_matrix(reach_matrix, "Reachability Matrix")
    
    strong_matrix = calculate_strong_connectivity_matrix(reach_matrix)
    print_matrix(strong_matrix, "Strong Connectivity Matrix")
    
    components = find_strongly_connected_components(strong_matrix)
    print("\nStrongly Connected Components:")
    for i, comp in enumerate(components):
        print(f"Component {i+1}: {comp}")
    
    condensation_matrix = create_condensation_graph(matrix_dir2, components)
    print_matrix(condensation_matrix, "Condensation Graph Matrix")
    
    graphs = {
        "1": (matrix_dir1, True, "Directed Graph (First Formula)"),
        "2": (matrix_undir1, False, "Undirected Graph"),
        "3": (matrix_dir2, True, "Directed Graph (Second Formula)"),
        "4": (condensation_matrix, True, "Condensation Graph")
    }
    
    def show_instructions():
        instructions = (
            "Press keys to switch between graphs:\n"
            "1: Directed Graph 1\n"
            "2: Undirected Graph\n"
            "3: Directed Graph 2\n" 
            "4: Condensation Graph"
        )
        
        canvas.create_rectangle(10, 10, 300, 120, fill="white", outline="black")
        canvas.create_text(155, 65, text=instructions, font=("Arial", 10))
    
    def key_pressed(event):
        key = event.char
        if key in graphs:
            matrix, directed, title = graphs[key]
            draw_graph(canvas, matrix, directed, title)
            show_instructions()
    
    root.bind("<Key>", key_pressed)
    
    matrix, directed, title = graphs["1"]
    draw_graph(canvas, matrix, directed, title)
    
    root.mainloop()

if __name__ == "__main__":
    main()