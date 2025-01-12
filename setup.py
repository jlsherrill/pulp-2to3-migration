#!/usr/bin/env python3

from setuptools import find_packages, setup

requirements = [
    'pulpcore~=3.0rc1',
    'mongoengine',
    'semantic_version',
    'jsonschema'
]

setup(
    name='pulp-2to3-migration',
    version='0.0.1a1.dev',
    description='Pulp 2 to Pulp 3 migration tool',
    license='GPLv2+',
    author='Pulp Team',
    author_email='pulp-list@redhat.com',
    url='http://www.pulpproject.org',
    python_requires='>=3.6',
    install_requires=requirements,
    include_package_data=True,
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=(
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: POSIX :: Linux',
        'Framework :: Django',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ),
    entry_points={
        'pulpcore.plugin': [
            'pulp_2to3_migration = pulp_2to3_migration:default_app_config',
        ],
        'migrators': [
            'iso = pulp_2to3_migration.app.plugin.iso.migrator:IsoMigrator',
            'docker = pulp_2to3_migration.app.plugin.docker.migrator:DockerMigrator',
        ]
    }
)
