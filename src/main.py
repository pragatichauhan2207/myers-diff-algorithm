import sys


def read_lines(path):
    with open(path, "rb") as f:
        data = f.read()

    lines = data.split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    return lines


def intern_lines(lines_a, lines_b):
    table = {}

    def to_id(line):
        if line not in table:
            table[line] = len(table)
        return table[line]

    a = [to_id(line) for line in lines_a]
    b = [to_id(line) for line in lines_b]
    return a, b


def myers_distance(a, b):
    n = len(a)
    m = len(b)
    max_d = n + m

    # k runs from -max_d to +max_d; V[k] is stored at v[offset + k]
    # because Python lists cannot use negative indices here.
    offset = max_d + 1
    v = [0] * (2 * max_d + 3)

    for d in range(max_d + 1):
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[offset + k - 1] < v[offset + k + 1]):
                x = v[offset + k + 1]
            else:
                x = v[offset + k - 1] + 1
            y = x - k

            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            v[offset + k] = x

            if x >= n and y >= m:
                return d

    return max_d


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        print("usage: main.py lines|highlight FILE_A FILE_B", file=sys.stderr)
        return 2

    command = sys.argv[1]
    path_a = sys.argv[2]
    path_b = sys.argv[3]

    try:
        lines_a = read_lines(path_a)
        lines_b = read_lines(path_b)
    except OSError as err:
        print(f"error: cannot read file: {err}", file=sys.stderr)
        return 2

    a, b = intern_lines(lines_a, lines_b)

    d = myers_distance(a, b)
    print("D =", d, file=sys.stderr)   # TEMPORARY debug (stderr only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
