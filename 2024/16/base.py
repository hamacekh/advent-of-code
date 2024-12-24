import heapq

def parse_maze(maze_input):
    maze = [list(row) for row in maze_input.split("\n")]
    start = None
    end = None

    for r, row in enumerate(maze):
        for c, cell in enumerate(row):
            if cell == 'S':
                start = (r, c)
            elif cell == 'E':
                end = (r, c)

    return maze, start, end

def reindeer_maze_solver(maze_input):
    maze, start, end = parse_maze(maze_input)

    # Directions: (row_delta, col_delta, name)
    directions = [
        (-1, 0, 'N'),
        (0, 1, 'E'),
        (1, 0, 'S'),
        (0, -1, 'W')
    ]

    # Map direction names to indices for rotation
    direction_map = {d[2]: i for i, d in enumerate(directions)}

    def heuristic(pos):
        """Manhattan distance heuristic."""
        return abs(pos[0] - end[0]) + abs(pos[1] - end[1])

    def is_valid_position(r, c):
        return 0 <= r < len(maze) and 0 <= c < len(maze[0]) and maze[r][c] != '#'

    # Priority queue for A*
    pq = []
    # State: (total_score, current_position, current_direction)
    heapq.heappush(pq, (0, start, 'E'))

    # Visited states: (row, col, direction)
    visited = set()

    while pq:
        score, (r, c), direction = heapq.heappop(pq)

        # If we've reached the end, return the score
        if (r, c) == end:
            return score

        if (r, c, direction) in visited:
            continue

        visited.add((r, c, direction))

        # Explore all possible moves
        current_dir_idx = direction_map[direction]

        # 1. Move forward
        dr, dc, _ = directions[current_dir_idx]
        nr, nc = r + dr, c + dc
        if is_valid_position(nr, nc):
            heapq.heappush(pq, (score + 1, (nr, nc), direction))

        # 2. Turn clockwise or counterclockwise
        for turn_cost, new_dir_idx in [(1000, (current_dir_idx + 1) % 4), (1000, (current_dir_idx - 1) % 4)]:
            new_direction = directions[new_dir_idx][2]
            heapq.heappush(pq, (score + turn_cost, (r, c), new_direction))

    return float('inf')  # If no path is found

# Example usage
if __name__ == "__main__":
    with open("base_input.txt", "r") as file:
        maze_input = file.read()
    print(reindeer_maze_solver(maze_input))
