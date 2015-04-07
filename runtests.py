#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from django.test.utils import get_runner
from ctypes.util import find_library

# MacOSX + Homebrew
SPATIALITE_LIB_PATH = find_library('mod_spatialite')
# Probably everything else
# SPATIALITE_LIB_PATH = find_library('spatialite')

try:
    import django
    from django.conf import settings

    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        DATABASES={
            "default": {
                "ENGINE": "django.contrib.gis.db.backends.spatialite",
            }
        },
        ROOT_URLCONF="tests.urls",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sites",
            "features",
            "scenarios",
        ],
        MIDDLEWARE_CLASSES=(),  # Silence Django 1.7 warnings
        SITE_ID=1,
        NOSE_ARGS=['-s'],

        GEOMETRY_DB_SRID = 3857,
        GEOMETRY_CLIENT_SRID = 3857,
        GEOJSON_SRID = 3857,

        FIXTURE_DIRS=['tests/fixtures'],
        ORGS_TIMESTAMPED_MODEL='django_extensions.db.models.TimeStampedModel',
        SPATIALITE_LIBRARY_PATH=SPATIALITE_LIB_PATH,
    )
    if hasattr(django, 'setup'):
        django.setup()

    # from django_nose import NoseTestSuiteRunner
#except ImportError:
except ValueError:
    raise ImportError("Ensure this is run in an environment with Django and test requirements installed.")


def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    # Run tests
    # test_runner = NoseTestSuiteRunner(verbosity=1)
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(failures)


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
