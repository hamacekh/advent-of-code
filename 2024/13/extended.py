import heapq
from typing import NamedTuple, Generator
import re
import math


def lcm(a, b):
    return a * b // math.gcd(a, b)


class Point2(NamedTuple):
    x: int
    y: int

    # Addition operator
    def __add__(self, other):
        if isinstance(other, Point2):
            return Point2(self.x + other.x, self.y + other.y)
        raise TypeError("Can only add Point2 to another Point2.")

    # Subtraction operator
    def __sub__(self, other):
        if isinstance(other, Point2):
            return Point2(self.x - other.x, self.y - other.y)
        raise TypeError("Can only subtract Point2 from another Point2.")

    # Multiplication with scalar or point
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Point2(int(self.x * other), int(self.y * other))
        elif isinstance(other, Point2):
            return Point2(self.x * other.x, self.y * other.y)  # Element-wise multiplication
        raise TypeError("Can multiply Point2 only by scalar or another Point2.")

    # Reverse multiplication with scalar
    def __rmul__(self, other):
        return self.__mul__(other)

    # True division with scalar
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Point2(int(self.x / other), int(self.y / other))
        raise TypeError("Can only divide Point2 by a scalar.")

    def is_positive(self):
        return self.x >= 0 and self.y >= 0

    def is_zero(self):
        return self.x == 0 and self.y == 0


class SpacePosition(NamedTuple):
    cost: int
    point: Point2


class SearchSpace:

    def __init__(self, target: Point2, a_move: Point2, b_move: Point2):
        self.target = target
        self.a_move = a_move
        self.b_move = b_move
        self.a_price = 3
        self.b_price = 1

    def move_target(self, move: Point2):
        self.target += move

    def bfs(self) -> int | None:
        return self._bfs(self.target)

    def _bfs(self, actual_target: Point2) -> int | None:
        priority_queue: list[SpacePosition] = []
        visited: set[Point2] = set()

        # Initialize
        start_position = SpacePosition(0, Point2(0, 0))  # Assuming starting point (0, 0)
        heapq.heappush(priority_queue, start_position)  # Push cost and position as a tuple

        while priority_queue:
            # Retrieve current node
            current = heapq.heappop(priority_queue)

            # Check if target is reached
            if current.point == actual_target:
                return current.cost

            # Skip if already visited
            if current.point in visited:
                continue
            visited.add(current.point)

            # Generate neighbors
            for move, price in [(self.a_move, self.a_price), (self.b_move, self.b_price)]:
                next_point = current.point + move
                next_cost = current.cost + price
                if (self.target - next_point).is_positive():  # didn't overshoot
                    heapq.heappush(priority_queue, SpacePosition(next_cost, next_point))

        return None  # Target unreachable

    def numerical_solution(self) -> int | None:
        a = self.a_move
        b = self.b_move
        x = self.target.x
        y = self.target.y
        d = a.x * b.y - a.y * b.x
        if d == 0:
            d_target = a.x * y - a.y * x
            if d_target != 0:
                return None  # target doesn't lie on the same line, there is no solution
            common_move = Point2(lcm(a.x, b.x), lcm(a.y, b.y))

            common_a_moves = common_move.x // a.x
            common_b_moves = common_move.x // b.x
            common_move_price = min(common_a_moves * self.a_price, common_b_moves * self.b_price)
            common_move_count = x // common_move.x
            rest_price = self._bfs(self.target - common_move * common_move_count)
            if rest_price is None: # there is no integral solution
                return None
            return common_move_count * common_move_price + rest_price

        else:
            # vectors are independent, there is at most one integral solution
            a_num = x * b.y - y * b.x
            b_num = -x * a.y + y * a.x
            if a_num % d == 0 and b_num % d == 0:
                a_moves = a_num // d
                b_moves = b_num // d
                return a_moves * self.a_price + b_moves * self.b_price
            else:
                return None


def parse_search_spaces(file_path: str) -> Generator[SearchSpace, None, None]:
    """
    Parses a text file into a generator of SearchSpace objects as the file is read line by line.

    :param file_path: Path to the text file containing SearchSpace definitions.
    :return: A generator that yields SearchSpace objects.
    """
    # Use a buffer to accumulate lines of a single block (3 lines per block)
    buffer = []

    # Open the file and process it lazily
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  # Remove whitespace (e.g., newlines)
            if line:  # Add non-empty lines to the buffer
                buffer.append(line)

            # A block is complete when we have 3 lines (Button A, Button B, Prize)
            if len(buffer) == 3:
                # Process the block to create a SearchSpace object
                yield _create_search_space_from_block(buffer)
                buffer = []  # Clear the buffer for the next block


def _create_search_space_from_block(block: list) -> SearchSpace:
    """
    Helper function to create a SearchSpace object from a block of 3 lines.

    :param block: A list containing 3 lines (Button A, Button B, Prize).
    :return: A constructed SearchSpace object.
    """
    # Example block:
    # Button A: X+94, Y+34
    # Button B: X+22, Y+67
    # Prize: X=8400, Y=5400

    # Regex patterns to extract the coordinates from each line
    button_pattern = re.compile(r"X\+(\d+), Y\+(\d+)")
    prize_pattern = re.compile(r"X=(\d+), Y=(\d+)")

    # Parse Button A
    a_match = button_pattern.search(block[0])
    a_x, a_y = map(int, a_match.groups())

    # Parse Button B
    b_match = button_pattern.search(block[1])
    b_x, b_y = map(int, b_match.groups())

    # Parse Prize
    prize_match = prize_pattern.search(block[2])
    prize_x, prize_y = map(int, prize_match.groups())

    # Return the constructed SearchSpace
    return SearchSpace(
        target=Point2(prize_x, prize_y),
        a_move=Point2(a_x, a_y),
        b_move=Point2(b_x, b_y),
    )


def main():
    """
    Main function to process input file, run DFS for each SearchSpace, and display the results.
    """
    input_file = "base_input.txt"
    total_cost = 0

    # Parse the file using the generator
    for index, search_space in enumerate(parse_search_spaces(input_file), start=1):
        #  for advanced mode, move target by 10000000000000 in both axes
        search_space.move_target(move=Point2(10000000000000, 10000000000000))
        # Run DFS on the current SearchSpace
        result = search_space.numerical_solution()

        # Check if the target was reachable
        if result is not None:
            print(f"SearchSpace {index}: Target reached with cost {result}")
            total_cost += result  # Add the cost to the total cost
        else:
            print(f"SearchSpace {index}: Target unreachable")

    # Print the total cost (excluding unreachable ones)
    print(f"\nTotal Cost (excluding unreachable targets): {total_cost}")


if __name__ == "__main__":
    main()
