import abc
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple, IO, TextIO, Iterable


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


class Orientation(Enum):
    UP = "^"
    DOWN = "v"
    LEFT = "<"
    RIGHT = ">"

    def move(self, point: Point2) -> Point2:
        """Moves a Point2 one step in the direction of the Orientation."""
        if self == Orientation.UP:
            return point + Point2(0, -1)
        elif self == Orientation.DOWN:
            return point + Point2(0, 1)
        elif self == Orientation.LEFT:
            return point + Point2(-1, 0)
        elif self == Orientation.RIGHT:
            return point + Point2(1, 0)

    @classmethod
    def from_char(cls, char: str) -> "Orientation":
        """Loads an Orientation instance from its character value."""
        for orientation in cls:
            if orientation.value == char:
                return orientation
        raise ValueError(f"No Orientation found for character: {char}")


@dataclass
class Item:
    position: Point2

    @abc.abstractmethod
    def move(self, orientation: Orientation, board: "dict[Point2, Item]") -> Point2 | None:
        """Moves this item in the selected orientation.
        Tries to push an obstacle if it is there.
        Returns none if immovable (either itself or blocked)"""
        pass


@dataclass
class MovableItem(Item):

    def move(self, orientation: Orientation, board: "dict[Point2, Item]") -> Point2 | None:
        new_position = orientation.move(self.position)
        if new_position in board:
            move_attempt = board[new_position].move(orientation, board)
            if move_attempt is None:
                return None
        del board[self.position]
        self.position = new_position
        board[new_position] = self
        return new_position

class Wall(Item):

    def move(self, orientation: Orientation, board: "dict[Point2, Item]") -> Point2 | None:
        return None

    def __repr__(self):
        return "#"

class Box(MovableItem):

    def value(self, size: Point2) -> int:
        return self.position.x + 100 * self.position.y

    def __repr__(self):
        return "O"

class Robot(MovableItem):

    def __repr__(self):
        return "@"


class Warehouse:

    def __init__(self, robot: Robot, walls: list[Wall], boxes: list[Box], width: int, height: int):
        self.items: dict[Point2, Item] = dict()
        self.boxes: list[Box] = boxes
        self.items.update((w.position, w) for w in walls)
        self.items.update((b.position, b) for b in boxes)
        self.items[robot.position] = robot
        self.robot = robot
        self.width = width
        self.height = height

    @staticmethod
    def load(input_stream: TextIO) -> "Warehouse":
        """Load everything up to an empty line."""
        lines = []

        for line in input_stream:
            line = line.rstrip("\n")
            if not line:
                break
            lines.append(line)

        height = len(lines)
        width = len(lines[0]) if height > 0 else 0
        robot: Robot | None = None
        walls: list[Wall] = []
        boxes: list[Box] = []

        for y, line in enumerate(lines):
            for x, input_char in enumerate(line):
                position = Point2(x, y)
                if input_char == "#":
                    walls.append(Wall(position))
                elif input_char == "O":
                    boxes.append(Box(position))
                elif input_char == "@":
                    robot = Robot(position)
        if not robot:
            raise ValueError("No robot found in the warehouse.")
        return Warehouse(robot, walls, boxes, width, height)

    def advance(self, orientation: Orientation) -> None:
        """Advance the simulation by one step."""
        self.robot.move(orientation, self.items)

    def value(self) -> int:
        size = Point2(self.width, self.height)
        return sum(b.value(size) for b in self.boxes)


    def __repr__(self):
        result = []
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                row += str(self.items.get(Point2(x, y), "."))
            result.append(row)
        return "\n".join(result)

    def __str__(self):
        return self.__repr__()


if __name__ == "__main__":
    with open("base_input.txt", "r") as file:
        warehouse = Warehouse.load(file)

        for char in file.read():
            if char.strip():
                #print(warehouse)
                #print(char)
                orientation = Orientation.from_char(char)
                warehouse.advance(orientation)

    print(warehouse)
    print(warehouse.value())
