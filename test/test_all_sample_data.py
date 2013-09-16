#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
from nose.tools import assert_equal
from os.path import join, dirname
import os

from pdftables.pdftables import page_to_tables
from pdftables.display import to_string
from pdftables.diagnostics import render_page, make_annotations

from fixtures import fixture

SAMPLE_DIR = join(dirname(__file__), '..', 'fixtures', 'sample_data')
RENDERED_DIR = join(dirname(__file__), '..', 'fixtures', 'rendered')
EXPECTED_DIR = join(dirname(__file__), '..', 'fixtures', 'expected_output')
ACTUAL_DIR = join(dirname(__file__), '..', 'fixtures', 'actual_output')


def _test_sample_data():
    for filename in os.listdir(SAMPLE_DIR):
        yield _test_sample_pdf, filename


def _test_sample_pdf(short_filename):
    doc = fixture(short_filename)
    for page_number, page in enumerate(doc.get_pages()):

        tables = page_to_tables(page)
        annotations = make_annotations(tables)

        basename = '{0}_{1}'.format(short_filename, page_number)

        render_page(
            join(SAMPLE_DIR, short_filename),
            page_number,
            annotations,
            svg_file=join(RENDERED_DIR, 'svgs', basename + '.svg'),
            png_file=join(RENDERED_DIR, 'pngs', basename + '.png')
        )

    assert_equal(get_expected_number_of_tables(short_filename), len(tables))
    for table_num, table in enumerate(tables):
        table_filename = "{}_{}.txt".format(short_filename, table_num)
        expected_filename = join(EXPECTED_DIR, table_filename)
        actual_filename = join(ACTUAL_DIR, table_filename)

        with open(actual_filename, 'w') as f:
            f.write(to_string(table).encode('utf-8'))

        diff_table_files(expected_filename, actual_filename)


def get_expected_number_of_tables(short_filename):
    result = len([fn for fn in os.listdir(EXPECTED_DIR)
                  if fn.startswith(short_filename)])
    if result == 0:
        print("NOTE: there is no 'expected' data for {0} in {1}: you probably "
              "want to review then copy files from {2}".format(
                  short_filename, EXPECTED_DIR, ACTUAL_DIR))
    return result


def diff_table_files(expected, result):
    with open(expected) as f:
        with open(result) as g:
            for line, (expected_line, actual_line) in enumerate(zip(f, g)):
                try:
                    assert_equal(expected_line, actual_line)
                except AssertionError:
                    print("{} and {} differ @ line {}".format(
                        expected, result, line + 1))
                    raise
