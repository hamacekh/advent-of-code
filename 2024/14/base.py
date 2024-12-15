import sys
from dataclasses import dataclass
from math import floor, ceil
from typing import NamedTuple, Iterable
from math import prod


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

    # Modulo operator
    def __mod__(self, other):
        if isinstance(other, Point2):
            if other.x == 0 or other.y == 0:
                raise ZeroDivisionError("Modulo by zero is not allowed for Point2.")
            return Point2(self.x % other.x, self.y % other.y)
        raise TypeError("Modulo operation requires another Point2.")

    # True division with scalar
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Point2(int(self.x / other), int(self.y / other))
        raise TypeError("Can only divide Point2 by a scalar.")

    def is_positive(self):
        return self.x >= 0 and self.y >= 0

    def is_zero(self):
        return self.x == 0 and self.y == 0


@dataclass
class Robot:
    position: Point2
    velocity: Point2

    def move_time(self, seconds: int) -> None:
        self.position += self.velocity * seconds

    def roll_over_bounds(self, bounds: Point2) -> None:
        self.position %= bounds


@dataclass
class Square:
    bottom_left: Point2
    top_right: Point2

    def is_robot_inside(self, robot: Robot) -> bool:
        return (self.bottom_left.x <= robot.position.x < self.top_right.x and
                self.bottom_left.y <= robot.position.y < self.top_right.y)


class Space:

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.robots = []

    def add_robots(self, robots: Iterable[Robot]) -> None:
        self.robots.extend(robots)

    def simulate(self, seconds: int) -> None:
        for robot in self.robots:
            robot.move_time(seconds)
            robot.roll_over_bounds(Point2(self.width, self.height))

    def partition_to_quadrants(self) -> list[Square]:
        target_width = self.width // 2
        target_height = self.height // 2
        return [
            Square(Point2(0, 0), Point2(target_width, target_height)),
            Square(Point2(self.width - target_width, 0), Point2(self.width, target_height)),
            Square(Point2(0, self.height - target_height), Point2(target_width, self.height)),
            Square(Point2(self.width - target_width, self.height - target_height), Point2(self.width, self.height)),
        ]

    def print_robot_positions(self) -> None:
        for i, robot in enumerate(self.robots, start=1):
            print(f"Robot {i}: Position={robot.position}")

    def ascii_art_positions(self) -> None:
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for robot in self.robots:
            grid[robot.position.y % self.height][robot.position.x % self.width] += 1
        for row in reversed(grid):
            print(''.join(str(cell) if cell > 0 else '.' for cell in row))

    def count_robots_in_quadrants(self):
        squares = self.partition_to_quadrants()
        counts = [0] * len(squares)  # Initialize counts list for each quadrant
        for robot in self.robots:
            for i, square in enumerate(squares):
                if square.is_robot_inside(robot):
                    counts[i] += 1  # Increment count for the corresponding square
        return counts


def parse_robots_file(file_path: str) -> list[Robot]:
    import re
    robots = []

    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Remove whitespace
                line = line.strip()
                # Match position and velocity using regex
                match = re.match(r"p=(-?\d+),(-?\d+) v=(-?\d+),(-?\d+)", line)
                if not match:
                    raise ValueError(f"Invalid line format: {line}")
                # Extract position and velocity values
                position = Point2(int(match.group(1)), int(match.group(2)))
                velocity = Point2(int(match.group(3)), int(match.group(4)))
                # Create a Robot object and add to the list
                robots.append(Robot(position=position, velocity=velocity))

    except (IOError, ValueError) as e:
        print(f"Error occurred while parsing the file: {e}")

    return robots


def main():
    input_file = "base_example.txt"
    robots = parse_robots_file(input_file)
    #  space = Space(width=101, height=103)
    space = Space(width=11, height=7)
    space.add_robots(robots)
    space.simulate(seconds=100)
    robots_in_quadrants = space.count_robots_in_quadrants()
    for quadrant in space.partition_to_quadrants():
        print(quadrant)
    space.print_robot_positions()
    space.ascii_art_positions()
    print(f"Robot counts in quadrants: {robots_in_quadrants}")
    print(f"Safety result: {prod(robots_in_quadrants)}")


if __name__ == "__main__":
    main()
