'''
PROJECT:     ReactOS rapps-db validator
LICENSE:     MIT (https://spdx.org/licenses/MIT)
PURPOSE:     Validate all rapps-db files
COPYRIGHT:   Copyright 2020,2021 Mark Jansen <mark.jansen@reactos.org>
'''
import os
import sys

# TODO: make this even nicer by using https://github.com/pytorch/add-annotations-github-action

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALL_KEYS = [
    b'Name',
    b'Version',
    b'License',
    b'Description',
    b'Size',
    b'Category',
    b'URLSite',
    b'URLDownload',
    b'SHA1',
    b'SizeBytes',
    b'SizeInBytes',
    b'Icon',
    b'Screenshot1',
    b'LicenseInfo',
    b'Languages',
]


ALL_ARCH = [
    b'x86',
    b'amd64',
    b'arm',
    b'arm64',
    b'ia64',
    b'ppc',
]


HEXDIGITS = b'0123456789abcdef'


class Reporter:
    def __init__(self):
        self._problems = 0

    def add(self, line, column, problem):
        self._problems += 1
        print(f'{line.location(column)}: {problem}')
        print(line.text())
        idx = column - 1 + len("b'")    # Offset the b' prefix
        print(' ' * idx + '^')

    def problems(self):
        return self._problems > 0


class RappsLine:
    def __init__(self, file, lineno, text):
        self._file = file
        self._lineno = lineno
        self._text = text
        self._last_col = len(self._text.rstrip())

    def parse(self, reporter):
        if not self._text.endswith(b'\r\n'):
            reporter.add(self, self._last_col, "Invalid line ending")
        parts = [part.strip() for part in self._text.split(b'=', 1)]
        first = parts[0]
        if first.startswith(b';') or (len(parts) == 1 and len(first) == 0):
            # comment or empty line, no further processing required!
            pass
        elif len(parts) == 1:
            self._parse_section(reporter, first)
        else:
            self._parse_key_value(reporter, parts)

    def _parse_section(self, reporter, stripped):
        # [Header]
        if not stripped.startswith(b'['):
            reporter.add(self, 0, "Expected [")
            stripped = b'[' + stripped  # Add it so we can continue
        if not stripped.endswith(b']'):
            reporter.add(self, self._last_col, "Expected ]")
            stripped = stripped + b']'  # Add it so we can continue

        section_name, locale, extra_locale, arch = self._extract_section_info(stripped, reporter)

        if section_name != b'Section':
            help = 'should always be "Section"'
            reporter.add(self, self._text.index(section_name) + 1, f'Invalid section name: "{section_name}", {help}')

        if locale:
            if len(locale) not in (2, 4) or not all(c in HEXDIGITS for c in locale):
                reporter.add(self, self._text.index(locale) + 1, f'Invalid locale{extra_locale}: "{locale}"')

        if arch:
            if arch not in ALL_ARCH:
                reporter.add(self, self._text.index(arch) + 1, f'Unknown architecture: "{arch}"')

    def _extract_section_info(self, text, reporter):
        text = text[1:-1]
        parts = text.split(b'.')
        section_name = parts[0]
        extra_locale = ''

        if len(parts) == 1:
            locale = arch = None
        elif len(parts) == 2:
            if parts[1] in ALL_ARCH:
                locale = None
                arch = parts[1]
            else:
                locale = parts[1]
                arch = None
                extra_locale = '(and unknown architecture)'
        elif len(parts) == 3:
            locale = parts[1]
            arch = parts[2]
        else:
            locale = arch = None
            reporter.add(self, self._text.index(b'[') + 1, f'Unknown section format: "{text}"')
        return section_name, locale, extra_locale, arch

    def _parse_key_value(self, reporter, parts):
        # key = value
        assert len(parts) == 2, self
        key = parts[0]

        if key not in ALL_KEYS:
            reporter.add(self, 0, f'Unknown key: "{key}"')

    def location(self, column):
        return f'{self._file.filename}({self._lineno}:{column})'

    def text(self):
        return self._text


class RappsFile:
    def __init__(self, fullname):
        self.path = fullname
        self.filename = os.path.basename(fullname)
        self._lines = None

    def parse(self, reporter):
        if not self._lines:
            with open(self.path, 'rb') as f:
                self._lines = [RappsLine(self, idx + 1, line) for idx, line in enumerate(f.readlines())]

        for line in self._lines:
            line.parse(reporter)


def validate_repo(dirname):
    reporter = Reporter()

    all_files = [RappsFile(filename) for filename in os.listdir(dirname) if filename.endswith('.txt')]
    for entry in all_files:
        entry.parse(reporter)

    if reporter.problems():
        print('Please check https://reactos.org/wiki/index.php?title=RAPPS for details on the file format')
        sys.exit(1)
    else:
        print('No problems found.')


if __name__ == '__main__':
    validate_repo(REPO_ROOT)
