def parse_line(line: str) -> list[int]:
    return [int(i) for i in line.split()]


def process_line(numbers: list[int]) -> bool:
    #print(f"processing {numbers}")
    if len(numbers) == 0:
        return False  # skip empty lines
    if len(numbers) == 1:
        return True
    ascending_direction = numbers[1] > numbers[0]
    previous = numbers[0]
    for number in numbers[1:]:
        if number <= previous and ascending_direction:
            return False
        if number >= previous and not ascending_direction:
            return False
        if abs(number - previous) > 3:
            return False
        previous = number
    return True

def process_scrambled_line(numbers: list[int]) -> bool:
    missing = [process_line(numbers[:i] + numbers[i+1:]) for i in range(len(numbers) + 1)]
    return any(missing)


def process_file(filename) -> int:
    safe_count = 0
    line_count = 0
    with open(filename, "r") as f:
        for line in f:
            safe = process_scrambled_line(parse_line(line))
            print(f"Line {line_count} safety: {safe}")
            if safe:
                safe_count += 1
            line_count += 1
    return safe_count

def main():
    res = process_file("base_input.txt")
    print(res)



if __name__ == "__main__":
    main()
