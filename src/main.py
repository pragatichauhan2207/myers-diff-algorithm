import sys
from array import array

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

    # trace[d] keeps v at the start of round d, only for k = -d-1, -d+1, ..., d+1.
    # Round d reads only these (same parity), so every 2nd entry is enough.
    # array('i') uses 4 bytes per value instead of a list's 8 + int object.
    trace = []

    for d in range(max_d + 1):
        trace.append(array("i", v[offset - d - 1 : offset + d + 2 : 2]))

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

        # V[k] sits at snap[(k + d + 1) // 2]
        if k == -d or (k != d and snap[(k + d) // 2] < snap[(k + d + 2) // 2]):
            prev_k = k + 1
        else:
            prev_k = k - 1

        prev_x = snap[(prev_k + d + 1) // 2]
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


def char_ranges(old, new):
    # Myers on the characters of one paired - / + line.
    # Returns the changed ranges as text: "3-5,9-12" or "." for none.
    # "surrogateescape" keeps odd bytes as one character each instead of failing.
    s1 = old.decode("utf-8", "surrogateescape")
    s2 = new.decode("utf-8", "surrogateescape")

    # Common start and end can never be changed, so skip them (faster).
    limit = min(len(s1), len(s2))
    p = 0
    while p < limit and s1[p] == s2[p]:
        p += 1
    q = 0
    while q < limit - p and s1[len(s1) - 1 - q] == s2[len(s2) - 1 - q]:
        q += 1

    mid_a = s1[p : len(s1) - q]
    mid_b = s2[p : len(s2) - q]
    edits = backtrack(myers_trace(mid_a, mid_b), len(mid_a), len(mid_b))

    old_idx = [i + p for kind, i, _ in edits if kind == DELETE]
    new_idx = [j + p for kind, _, j in edits if kind == INSERT]
    return format_ranges(old_idx), format_ranges(new_idx)


def format_ranges(indexes):
    # indexes are increasing; touching ones merge into one range (3,4,5 -> 3-6).
    if not indexes:
        return "."
    parts = []
    start = prev = indexes[0]
    for i in indexes[1:]:
        if i != prev + 1:
            parts.append(f"{start}-{prev + 1}")
            start = i
        prev = i
    parts.append(f"{start}-{prev + 1}")
    return ",".join(parts)


def write_diff(edits, lines_a, lines_b, highlight):
    out = []
    dels = []
    inss = []

    def flush():
        # A change block: all - lines first, then all + lines.
        # With highlight, each paired + line is followed by its ? line.
        for i in dels:
            out.append(b"-" + lines_a[i] + b"\n")
        for pos, j in enumerate(inss):
            out.append(b"+" + lines_b[j] + b"\n")
            if highlight and pos < len(dels):
                old_r, new_r = char_ranges(lines_a[dels[pos]], lines_b[j])
                out.append(f"? {old_r} | {new_r}\n".encode())
        dels.clear()
        inss.clear()

    for kind, i, j in edits:
        if kind == KEEP:
            flush()
            out.append(b" " + lines_a[i] + b"\n")
        elif kind == DELETE:
            dels.append(i)
        else:
            inss.append(j)
    flush()
    sys.stdout.buffer.write(b"".join(out))


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
    write_diff(edits, lines_a, lines_b, command == "highlight")
    return 0


if __name__ == "__main__":
    sys.exit(main())
