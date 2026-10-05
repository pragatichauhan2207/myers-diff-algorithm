import sys

KEEP = " "
DELETE = "-"
INSERT = "+"


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


def myers_trace(a, b):
    n = len(a)
    m = len(b)
    max_d = n + m

    # V[k] is stored at v[offset + k] so negative k works as a list index.
    offset = max_d + 1
    v = [0] * (2 * max_d + 3)

    # trace[d] is the slice of v (k from -d-1 to d+1) at the start of round d.
    trace = []

    for d in range(max_d + 1):
        trace.append(v[offset - d - 1 : offset + d + 2])

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
                return trace

    return trace


def backtrack(trace, n, m):
    edits = []
    x, y = n, m

    for d in range(len(trace) - 1, -1, -1):
        snap = trace[d]
        k = x - y

        # V[k] sits at snap[k + d + 1]
        if k == -d or (k != d and snap[k - 1 + d + 1] < snap[k + 1 + d + 1]):
            prev_k = k + 1
        else:
            prev_k = k - 1

        prev_x = snap[prev_k + d + 1]
        prev_y = prev_x - prev_k

        while x > prev_x and y > prev_y:
            edits.append((KEEP, x - 1, y - 1))
            x -= 1
            y -= 1

        if d > 0:
            if x == prev_x:
                edits.append((INSERT, None, prev_y))
            else:
                edits.append((DELETE, prev_x, None))

        x, y = prev_x, prev_y

    edits.reverse()
    return edits


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

    trace = myers_trace(a, b)
    edits = backtrack(trace, len(a), len(b))

    # TEMPORARY debug (stderr only)
    for kind, i, j in edits:
        line = lines_b[j] if kind == INSERT else lines_a[i]
        print(kind + repr(line), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
