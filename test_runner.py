#!/usr/bin/env python3
import subprocess
import sys
import io
import contextlib
import argparse


def parse_in_file(path):
    """Parse a .in file into a list of test blocks.

    Supported block syntax (based on attached `init-test.in`):
    - Python block starts with a line beginning with `py>` followed by code
      (either on same line or subsequent indented lines). The next line
      after the block should start with `<<<` followed by expected stdout.
    - Shell block starts with a line beginning with `sh>` followed by the
      command on the same line. The next line should be `<<<` with expected
      stdout after it.

    Returns a list of dicts with keys: 'type' ('py'|'sh'), 'code'/'cmd', 'expected'.
    """
    tests = []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip('\n')
        if not line.strip():
            i += 1
            continue

        stripped = line.lstrip()
        if stripped.startswith('py>'):
            # collect code: may be on same line or in following indented lines
            rest = stripped[len('py>'):].lstrip()
            code_lines = []
            if rest:
                code_lines.append(rest)
                i += 1
                # also accept following indented lines as continuation
                while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                    code_lines.append(lines[i].lstrip())
                    i += 1
            else:
                i += 1
                while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                    code_lines.append(lines[i].lstrip().rstrip('\n'))
                    i += 1

            # expect a '<<<' line next (skip blank lines)
            while i < len(lines) and not lines[i].strip():
                i += 1
            expected = ''
            if i < len(lines) and lines[i].lstrip().startswith('<<<'):
                expected = lines[i].lstrip()[3:].lstrip().rstrip('\n')
                i += 1

            tests.append({'type': 'py', 'code': '\n'.join(code_lines), 'expected': expected})
            continue

        if stripped.startswith('sh>'):
            cmd = stripped[len('sh>'):].lstrip()
            i += 1
            # skip blanks then read expected marker
            while i < len(lines) and not lines[i].strip():
                i += 1
            expected = ''
            if i < len(lines) and lines[i].lstrip().startswith('<<<'):
                expected = lines[i].lstrip()[3:].lstrip().rstrip('\n')
                i += 1

            tests.append({'type': 'sh', 'cmd': cmd, 'expected': expected})
            continue

        # unknown line, skip
        i += 1

    return tests


def run_command(cmd, name=None):
    print(f"--- Running: {name or cmd} ---")
    print(f"Command: {cmd}")
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        stdout = proc.stdout
        stderr = proc.stderr
        ret = proc.returncode

        if ret == 0:
            print("\033[92mPASS\033[0m")
            if stdout:
                print("STDOUT:")
                print(stdout, end='')
            if stderr:
                print("STDERR:")
                print(stderr, end='')
            return True, stdout
        else:
            print("\033[91mFAIL\033[0m")
            print(f"Return code: {ret}")
            if stdout:
                print("STDOUT:")
                print(stdout, end='')
            if stderr:
                print("STDERR:")
                print(stderr, end='')
            return False, stdout

    except Exception as e:
        print(f"\033[91mERROR\033[0m: exception while running command: {e}")
        return False, ''


def main():
    parser = argparse.ArgumentParser(description='Run commands from a .in file. Supports embedded python via "py { ... }"')
    parser.add_argument('infile', nargs='?', default='UnitTest/init-test.in', help='path to .in file')
    args = parser.parse_args()

    commands = parse_in_file(args.infile)

    passed = 0
    failed = 0

    for i, block in enumerate(commands, start=1):
        if block['type'] == 'sh':
            ok, out = run_command(block['cmd'], name=f"Step {i}")
            expected = block.get('expected', '')
        elif block['type'] == 'py':
            # print header like sh blocks do
            print(f"--- Running: Step {i} ---")
            code_display = block.get('code', '')
            print("Code:")
            print(code_display)

            # execute python code and capture stdout
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    exec(block.get('code', ''), {})
            except Exception as e:
                print(f"\033[91mFAIL\033[0m")
                print(f"ERROR: executing python block failed: {e}")
                ok = False
                out = buf.getvalue()
            else:
                out = buf.getvalue()
                ok = True
                print("\033[92mPASS\033[0m")
                if out:
                    print("STDOUT:")
                    print(out, end='')
            expected = block.get('expected', '')

        else:
            print(f"Unknown block type: {block.get('type')}")
            ok = False
            out = ''
            expected = block.get('expected', '')

        # normalize output: remove lines that start with 'DEBUG:' and strip trailing newline
        def normalize(s):
            if s is None:
                return ''
            lines = s.splitlines()
            filtered = []
            skip_indented_after_debug = False
            for ln in lines:
                if ln.lstrip().startswith('DEBUG:'):
                    skip_indented_after_debug = True
                    continue
                if skip_indented_after_debug and (ln.startswith(' ') or ln.startswith('\t')):
                    # continuation line of a DEBUG block
                    continue
                skip_indented_after_debug = False
                filtered.append(ln)
            return '\n'.join(filtered).rstrip('\n')

        got_norm = normalize(out)
        exp_norm = normalize(expected)

        if got_norm == exp_norm and ok:
            passed += 1
            print("\033[92mMATCH\033[0m: output matches expected")
        else:
            failed += 1
            print("\033[91mMISMATCH\033[0m:")
            print(f"  Expected: {expected!r}")
            print(f"  Got:      {out!r}")

        print('-' * 40)

    print('\n--- Test Summary ---')
    print(f"\033[92m{passed} passed\033[0m, \033[91m{failed} failed\033[0m")

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
