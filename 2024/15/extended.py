import abc
from collections import deque
from dataclasses import dataclass
from enum import Enum
from types import new_class
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

    def move_all(self, points: Iterable[Point2]) -> frozenset[Point2]:
        return frozenset(self.move(p) for p in points)

    @classmethod
    def from_char(cls, char: str) -> "Orientation":
        """Loads an Orientation instance from its character value."""
        for orientation in cls:
            if orientation.value == char:
                return orientation
        raise ValueError(f"No Orientation found for character: {char}")


@dataclass
class Item:
    positions: frozenset[Point2]

    @abc.abstractmethod
    def get_width(self) -> int:
        pass

    @abc.abstractmethod
    def is_movable(self) -> bool:
        pass

    def min_x(self) -> int:
        return min(x for x, _ in self.positions)


@dataclass
class MovableItem(Item):

    def is_movable(self) -> bool:
        return True


class Wall(Item):

    def get_width(self) -> int:
        return 2

    def is_movable(self) -> bool:
        return False

    def __repr__(self):
        return "##"


class Box(MovableItem):

    def get_width(self) -> int:
        return 2

    def value(self, size: Point2) -> int:
        position_with_min_x = min(self.positions, key=lambda p: p.x)
        return position_with_min_x.x + 100 * position_with_min_x.y

    def __repr__(self):
        return "[]"


class Robot(MovableItem):

    def get_width(self) -> int:
        return 1

    def __repr__(self):
        return "@"


class Warehouse:

    def __init__(self, robot: Robot, walls: list[Wall], boxes: list[Box], width: int, height: int):
        self.items: dict[Point2, Item] = dict()
        self.boxes: list[Box] = boxes
        self.items.update((p, w) for w in walls for p in w.positions)
        self.items.update((p, b) for b in boxes for p in b.positions)
        self.items.update((p, robot) for p in robot.positions)
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
        width = 2 * width  # extended version
        robot: Robot | None = None
        walls: list[Wall] = []
        boxes: list[Box] = []

        for y, line in enumerate(lines):
            for x, input_char in enumerate(line):
                position = Point2(2 * x, y)
                if input_char == "#":
                    walls.append(Wall(frozenset([position, Orientation.RIGHT.move(position)])))
                elif input_char == "O":
                    boxes.append(Box(frozenset([position, Orientation.RIGHT.move(position)])))
                elif input_char == "@":
                    robot = Robot((frozenset([position])))
        if not robot:
            raise ValueError("No robot found in the warehouse.")
        return Warehouse(robot, walls, boxes, width, height)

    def advance(self, orientation: Orientation) -> None:
        """Advance the simulation by one step."""
        assert len(self.robot.positions) == 1
        pos = list(self.robot.positions)[0]
        new_position = orientation.move(pos)
        deps = self.can_push_item(new_position, orientation)
        if deps is None:
            return
        self.push_items(reversed(deps), orientation)
        self.push_items([self.robot], orientation)


    def value(self) -> int:
        size = Point2(self.width, self.height)
        return sum(b.value(size) for b in self.boxes)

    def can_push_item(self, pos: Point2, orientation: Orientation) -> list[Item] | None:
        """If an item on position can be pushed, return the list of affected other (movable) items.
         Otherwise, return None. When pushing, the list should be iterated over backwards."""
        if pos not in self.items:
            return []  # empty space, nothing to push
        plan: deque[Item] = deque([self.items[pos]])
        order: list[Item] = []
        visited: set[frozenset[Point2]] = set()
        board = self.items
        while plan:
            item = plan.popleft()
            if item.positions in visited:
                continue
            visited.add(item.positions)
            order.append(item)
            if not item.is_movable():
                return None
            new_position = orientation.move_all(item.positions)
            colliding_items = {board[p].positions: board[p]
                               for p in new_position
                               if p in board
                               if board[p].positions != item.positions}
            plan.extend(colliding_items.values())
        return order

    def push_items(self, items: Iterable[Item], orientation: Orientation) -> None:
        """Push a list of items in the selected orientation."""
        for item in items:
            new_position = orientation.move_all(item.positions)
            for p in item.positions:
                assert p in self.items
                del self.items[p]
            for p in new_position:
                self.items[p] = item
            item.positions = new_position

    def __repr__(self):
        result = []
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                item = self.items.get(Point2(x, y), None)
                if item is not None:
                    rel_pos = x - item.min_x()
                    row += repr(item)[rel_pos]
                else:
                    row += "."
            result.append(row)
        return "\n".join(result)

    def __str__(self):
        return self.__repr__()


if __name__ == "__main__":
    with open("base_input.txt", "r") as file:
        warehouse = Warehouse.load(file)
        # print(warehouse)
        step = 1
        for char in file.read():
            if char.strip():
                print(step)
                # print(warehouse)
                # print(char)
                orientation = Orientation.from_char(char)
                warehouse.advance(orientation)
                step += 1

    print(warehouse)
    print(warehouse.value())
