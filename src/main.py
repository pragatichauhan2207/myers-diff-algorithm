import sys


def main() -> int:
    # sys.argv is the list of words typed on the command line.
    # For:  python src/main.py lines A.txt B.txt
    # it is: ["src/main.py", "lines", "A.txt", "B.txt"]
    #          index 0        1        2        3
    # Index 0 is the script's own name, so our real input starts at index 1.

    # We need exactly 4 items, and the command must be one of the two we support.
    # Anything else is a usage error.
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        # Errors go to stderr, never stdout. The grader reads stdout as
        # "the diff", so any extra text there would make the output wrong.
        print("usage: main.py lines|highlight FILE_A FILE_B", file=sys.stderr)
        return 2

    command = sys.argv[1]
    path_a = sys.argv[2]
    path_b = sys.argv[3]

    # TEMPORARY: show what we read, so we can test this step.
    # It goes to stderr, so it can never break the real output.
    # We will delete this line in Step 2.
    print(f"command={command}  a={path_a}  b={path_b}", file=sys.stderr)
    return 0


# This block runs only when the file is started directly (python src/main.py ...),
# not when another file imports it. main() returns a number, and sys.exit()
# turns it into the program's exit code: 0 = success, 2 = error.
if __name__ == "__main__":
    sys.exit(main())

