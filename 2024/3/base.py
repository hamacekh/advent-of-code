from collections import namedtuple

ComputationResult = namedtuple("ComputationResult",["value", "next_index"])


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
    """Parses the first occurrence of `mul(X,Y)` from the line starting at index. Returns None if
     a valid mul is not found."""
    if index >= len(line):
        return None
    mul_index = line.find("mul(", index)
    if mul_index == -1:
        return None
    pos = mul_index + 4
    x = parse_number(line, pos)
    if x is None:
        return parse_mul(line, pos)
    pos = x.next_index
    if line[pos] != ",":
        return parse_mul(line, pos)
    pos += 1
    y = parse_number(line, pos)
    if y is None:
        return parse_mul(line, pos)
    pos = y.next_index
    if line[pos] != ")":
        return parse_mul(line, pos)
    return ComputationResult(value=x.value * y.value, next_index=pos)



def main():
    with open("base_input.txt", "r") as f:
        data = f.read()
        num = 0
        idx = 0
        mul_res = parse_mul(data, idx)
        while mul_res is not None:
            num += mul_res.value
            idx = mul_res.next_index
            mul_res = parse_mul(data, idx)
        print(num)


if __name__ == "__main__":
    main()
