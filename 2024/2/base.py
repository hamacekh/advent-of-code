
def process_line(line: str) -> bool:
    numbers = [int(i) for i in line.split()]
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


def process_file(filename) -> int:
    safe_count = 0
    line_count = 0
    with open(filename, "r") as f:
        for line in f:
            safe = process_line(line)
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
