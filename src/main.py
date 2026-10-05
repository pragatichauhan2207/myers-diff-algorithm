import sys


def read_lines(path):
    # "rb" = read binary. We get the exact bytes from the disk.
    # Text mode ("r") would turn \r\n into \n and could crash on bytes
    # that are not valid UTF-8. The spec forbids both.
    with open(path, "rb") as f:
        data = f.read()

    # Split on the newline BYTE. b"\n" (bytes), not "\n" (text),
    # because data is bytes. \r is not touched, so it stays in the line.
    lines = data.split(b"\n")

    # If the file ends with \n, split() leaves an empty piece at the end.
    # That piece is not a real line, so we drop it. This also turns an
    # empty file ([b""]) into zero lines ([]).
    if lines[-1] == b"":
        lines.pop()          # pop() removes the last item in O(1) time

    return lines


def intern_lines(lines_a, lines_b):
    # table maps each distinct line (bytes) to a small integer id.
    # ONE table for both files, so equal lines in A and B get the same id.
    table = {}

    def to_id(line):
        if line not in table:
            # A line we have not seen before gets the next free number:
            # 0 for the first new line, 1 for the second, and so on.
            table[line] = len(table)
        return table[line]

    # Convert every line of each file, keeping the original order.
    a = [to_id(line) for line in lines_a]
    b = [to_id(line) for line in lines_b]
    return a, b


def main() -> int:
    # sys.argv for: python src/main.py lines A.txt B.txt
    # is ["src/main.py", "lines", "A.txt", "B.txt"]; index 0 is the script.
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        # Errors go to stderr: the grader reads stdout as "the diff".
        print("usage: main.py lines|highlight FILE_A FILE_B", file=sys.stderr)
        return 2

    command = sys.argv[1]
    path_a = sys.argv[2]
    path_b = sys.argv[3]

    # Read both files BEFORE printing anything.
    # OSError covers "file not found", "permission denied", "is a folder", ...
    # On failure: nothing on stdout, an error on stderr, exit code 2.
    try:
        lines_a = read_lines(path_a)
        lines_b = read_lines(path_b)
    except OSError as err:
        print(f"error: cannot read file: {err}", file=sys.stderr)
        return 2

    # Lines -> integer ids. Myers will work on a and b.
    # We keep lines_a / lines_b too, because printing needs the real bytes.
    a, b = intern_lines(lines_a, lines_b)

    # TEMPORARY debug (stderr only)
    print("a:", a, file=sys.stderr)
    print("b:", b, file=sys.stderr)
    return 0


# Runs only when started directly (python src/main.py ...), not when imported.
# sys.exit() turns main()'s return value into the exit code: 0 = ok, 2 = error.
if __name__ == "__main__":
    sys.exit(main())
