'''
PROJECT:     ReactOS rapps-db validator
LICENSE:     MIT (https://spdx.org/licenses/MIT)
PURPOSE:     Validate all rapps-db files
COPYRIGHT:   Copyright 2020-2023 Mark Jansen <mark.jansen@reactos.org>
'''
import os
import sys
from enum import Enum, unique

# TODO: make this even nicer by using https://github.com/pytorch/add-annotations-github-action

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_SECTION_KEYS = [
    b'Name',
    b'Category',
    b'URLDownload',
]

OPTIONAL_SECTION_KEYS = [
    b'Version',
    b'License',
    b'Description',
    b'URLSite',
    b'SHA1',
    b'SizeBytes',
    b'Icon',
    b'Screenshot1',
    b'LicenseType',
    b'Languages',
    b'RegName',
    b'Publisher',
    b'Installer',
    b'Scope',
]


KEYS = {
    b'Section': REQUIRED_SECTION_KEYS + OPTIONAL_SECTION_KEYS,
    b'Generate': [
        b'Files',
        b'Dir',
        b'Lnk',
        b'Icon',
        b'DelFile',
        b'DelDir',
        b'DelDirEmpty',
        b'DelReg',
        b'DelRegEmpty',
    ],
}

ALL_ARCH = [
    b'x86',
    b'amd64',
    b'arm',
    b'arm64',
    b'ia64',
    b'ppc',
]

LICENSE_TYPES = [
    1, # Open source
    2, # Freeware
    3, # Trial/Demo
]

def get_valid_keys(section_name):
    return KEYS[section_name]

all_names = {}
all_urls = {}
g_current_section = None


HEXDIGITS = b'0123456789abcdef'


@unique
class LineType(Enum):
    Section = 1
    KeyValue = 2
    Comment = 3


class Reporter:
    def __init__(self):
        self._problems = 0

    def add(self, line, column, problem):
        self._problems += 1
        print('{col}: {msg}'.format(col = line.location(column), msg = problem))
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
        self.main_section = False
        self.key = None
        self.val = None
        self._entries = []

    def add(self, line):
        # Cannot add keyvalues if this is a keyvalue!
        assert not self.key
        self._entries.append(line)

    def __getitem__(self, key):
        for entry in self._entries:
            if entry.key == key:
                return entry
        return None

    def parse(self, reporter):
        if not self._text.endswith(b'\r\n'):
            reporter.add(self, self._last_col, "Invalid line ending")
        parts = [part.strip() for part in self._text.split(b'=', 1)]
        first = parts[0]
        if first.startswith(b';') or (len(parts) == 1 and len(first) == 0):
            # comment or empty line, no further processing required!
            return LineType.Comment
        elif len(parts) == 1:
            self._parse_section(reporter, first)
            return LineType.Section
        else:
            self._parse_key_value(reporter, parts)
            return LineType.KeyValue

    def _parse_section(self, reporter, stripped):
        # [Header]
        if not stripped.startswith(b'['):
            reporter.add(self, 0, "Expected [")
            stripped = b'[' + stripped  # Add it so we can continue
        if not stripped.endswith(b']'):
            reporter.add(self, self._last_col, "Expected ]")
            stripped = stripped + b']'  # Add it so we can continue

        section_name, locale, extra_locale, arch = self._extract_section_info(stripped, reporter)
        global g_current_section
        g_current_section = section_name

        if section_name not in KEYS:
            help = 'should always be "Section"'
            reporter.add(self, self._text.index(section_name) + 1,
                         'Invalid section name: "{sec}", {msg}'.format(sec = section_name, msg = help))
        elif not locale:
            self.main_section = True

        if locale:
            if len(locale) not in (2, 4) or not all(c in HEXDIGITS for c in locale):
                reporter.add(self, self._text.index(locale) + 1,
                             'Invalid locale{extra}: "{loc}"'.format(extra = extra_locale, loc = locale))

        if arch:
            if arch not in ALL_ARCH:
                reporter.add(self, self._text.index(arch) + 1, 'Unknown architecture: "%s"' % arch)

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
                extra_locale = ' (and unknown architecture)'
        elif len(parts) == 3:
            locale = parts[1]
            arch = parts[2]
        else:
            locale = arch = None
            reporter.add(self, self._text.index(b'[') + 1, 'Unknown section format: "%s"' % text)
        return section_name, locale, extra_locale, arch

    def _parse_key_value(self, reporter, parts):
        # key = value
        assert len(parts) == 2, self
        self.key = parts[0]
        self.val = parts[1]
        textkey = self.key.decode()
        textval = self.val.decode()

        if self.key not in get_valid_keys(g_current_section):
            reporter.add(self, 0, 'Unknown key: "{key}"'.format(key = textkey))

        if self.key in [b'LicenseType']:
            v = int(textval, base=10)
            if v not in LICENSE_TYPES:
                reporter.add(self, 0, 'Invalid value: "{val}" in {key}'.format(val = v, key = textkey))

        if self.key in [b'License']:
            v = textval
            if v.casefold() == 'Unknown'.casefold():
                # TODO: Reporter should be enabled when the existing DB entries are fixed:
                # reporter.add(self, 0, 'Invalid value: "{val}" in {key}'.format(val = v, key = textkey))
                print('Warning: {key} is "{val}" ({file})'.format(val = v, key = textkey, file = self._file.filename))

        if self.key in [b'Scope']:
            v = textval
            if v.casefold() not in ['user', 'machine']:
                print('Warning: {key} is "{val}" ({file})'.format(val = v, key = textkey, file = self._file.filename))

    def location(self, column):
        return '{file}({line}:{col})'.format(file = self._file.filename, line = self._lineno, col = column)

    def text(self):
        return self._text


class RappsFile:
    def __init__(self, fullname):
        self.path = fullname
        self.filename = os.path.basename(fullname)
        self._sections = []

    def parse(self, reporter):
        with open(self.path, 'rb') as f:
            lines = [RappsLine(self, idx + 1, line) for idx, line in enumerate(f.readlines())]

        # Create sections from all lines, and add keyvalue entries in their own section
        section = None
        for line in lines:
            linetype = line.parse(reporter)
            if linetype == LineType.Comment:
                continue
            if linetype == LineType.Section:
                section = line
                self._sections.append(section)
            elif linetype == LineType.KeyValue:
                assert section, "Got no section yet?"
                section.add(line)

        all_sections = []
        main_section = None
        name = None
        ver = None
        url = None

        for section in self._sections:
            uniq_section = section._text.strip().upper()
            if uniq_section in all_sections:
                reporter.add(section, 0, 'Duplicate section found!')
            else:
                all_sections.append(uniq_section)
            if not main_section and section.main_section:
                main_section = section
                for key in REQUIRED_SECTION_KEYS:
                    if not section[key]:
                        reporter.add(section, 0, 'Main section has no {key} key!'.format(key = key))
            if section[b'URLDownload'] and not section[b'SizeBytes']:
                # We allow this, if the main section has a SizeBytes (alternate mirror without duplicating the info)
                if section == main_section or main_section and not main_section[b'SizeBytes']:
                    reporter.add(section, 0, 'Section has URLDownload but no SizeBytes!')

            if section[b'Name'] and not name:
                name = section[b'Name']
            if section[b'Version'] and not ver:
                ver = section[b'Version']
            if section[b'URLDownload'] and not url:
                url = section[b'URLDownload']

        # Verify that the application name and version is unique
        if name:
            global all_names
            if ver:
                verify_unique(reporter, all_names, name, name.val + b', version ' + ver.val)
            else:
                verify_unique(reporter, all_names, name, name.val)

        # Verify that the download URL is unique
        if url:
            global all_urls
            verify_unique(reporter, all_urls, url, url.val)


def verify_unique(reporter, lines, line, name):
    first = lines.get(name, None)
    if first:
        reporter.add(line, 0, 'Duplicate value found: {name}'.format(name = name))
        reporter.add(first, 0, 'First occurence:')
    else:
        lines[name] = line


def validate_repo(dirname):
    reporter = Reporter()

    all_files = [RappsFile(filename) for filename in os.listdir(dirname) if filename.endswith('.txt')]
    for entry in all_files:
        entry.parse(reporter)

    if reporter.problems():
        print('Please check https://reactos.org/wiki/RAPPS for details on the file format.')
        sys.exit(1)
    else:
        print('No problems found.')


if __name__ == '__main__':
    validate_repo(REPO_ROOT)
