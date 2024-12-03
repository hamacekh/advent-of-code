from collections import namedtuple
import re

ComputationResult = namedtuple("ComputationResult",["value", "next_index"])
CallToken = namedtuple("CallToken", ["name", "index_position"])


def parse_number(line: str, index: int) -> ComputationResult | None:
    """Parses 1-3 digit integral from the line starting at index. Returns None if a valid number is not found."""
    result_number = 0
    if index >= len(line) or not line[index].isdigit():
        return None
    for i in range(index, index + 3):
        if i < len(line) and line[i].isdigit():
            result_number = result_number * 10 + int(line[i])
        else:
            return ComputationResult(value=result_number, next_index=i)
    return ComputationResult(value=result_number, next_index=index + 3)


def parse_mul(line: str, index: int = 0) -> ComputationResult | None:
    """Parses a single occurrence of `mul(X,Y)` from the line starting at index. Returns None if
     a valid mul is not there."""
    if index >= len(line):
        return None
    if line[index:index + 4] != "mul(":
        return None
    pos = index + 4
    x = parse_number(line, pos)
    if x is None:
        return None
    pos = x.next_index
    if line[pos] != ",":
        return None
    pos += 1
    y = parse_number(line, pos)
    if y is None:
        return None
    pos = y.next_index
    if line[pos] != ")":
        return None
    return ComputationResult(value=x.value * y.value, next_index=pos)

def parse_empty_call(line: str, index: int, name: str) -> int | None:
    """Parses a single occurrence of `<name>()` call. Returns None if a valid call is not found.
    Returns the index of the next character if a valid call is found."""
    end_index = index + len(name) + 2
    if end_index > len(line):
        return None
    if line[index:end_index] == f"{name}()":
        return end_index
    return None

def find_next_call(line: str, index: int) -> CallToken | None:
    """Finds the first call in form of `call(arg1,arg2,..)` at `line[index:]` substring.
     Returns None if no call is found."""
    regex = r"([a-zA-Z']+)\([^\)]*\)"
    match = re.search(regex, line[index:])
    if match is None:
        return None
    return CallToken(name=match.group(1), index_position=index + match.start())

def main():
    with open("base_input.txt", "r") as f:
        data = f.read()
        num = 0
        idx = 0
        do_enabled = True
        call = find_next_call(data, idx)
        while call is not None:
            if call.name == "mul":
                result = parse_mul(data, call.index_position)
                if result:
                    if do_enabled:
                        num += result.value
                    idx = result.next_index
                else:
                    idx = call.index_position + 1
            elif call.name == "do":
                result = parse_empty_call(data, call.index_position, "do")
                if result is None:
                    idx = call.index_position + 1
                else:
                    do_enabled = True
                    idx = result
            elif call.name == "don't":
                result = parse_empty_call(data, call.index_position, "don't")
                if result is None:
                    idx = call.index_position + 1
                else:
                    do_enabled = False
                    idx = result
            else:
                idx = call.index_position + 1
            call = find_next_call(data, idx)
        print(num)


if __name__ == "__main__":
    main()
