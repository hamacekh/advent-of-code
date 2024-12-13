from typing import Generator


class SearchGrid:

    def __init__(self, file_name):
        self.grid = self._load_file_to_str_list(file_name)
        self.width = len(self.grid[0])
        self.height = len(self.grid)

    def verticals(self) -> Generator[str, None, None]:
        for i in range(self.height):
            yield self.grid[i]
            
    def reverse_verticals(self) -> Generator[str, None, None]:
        for i in range(self.height-1, -1, -1):
            yield self.grid[i][::-1]

    @staticmethod
    def _load_file_to_str_list(file_name: str) -> list[str]:
        with open(file_name) as f:
            return [l for l in f.read().splitlines() if len(l) > 0]
