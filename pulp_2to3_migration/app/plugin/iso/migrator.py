from pulp_2to3_migration.app.plugin.api import (
    ContentMigrationFirstStage,
    DeclarativeContentMigration,
    Pulp2to3PluginMigrator,
)

from .pulp2_models import ISO
from .pulp_2to3_models import Pulp2ISO
from .repository import IsoImporter


class IsoMigrator(Pulp2to3PluginMigrator):
    """
    An entry point for migration the Pulp 2 ISO plugin to Pulp 3.

    Attributes:
        pulp2_plugin(str): Pulp 2 plugin name
        pulp2_content_models(dict): {'pulp2 content_type_id': 'content class to access MongoDB'}
        pulp2_collection(str): a pulp2 collection which existence signifies that a plugin
                               is installed in pulp2
        pulp3_plugin(str): Pulp 3 plugin name
        content_models(dict): {'pulp2 content_type_id': 'detail content class to pre-migrate to'}
        importer_migrators(dict): {'importer_type_id': 'pulp_2to3 importer interface/migrator'}

    """
    pulp2_plugin = 'iso'
    pulp2_content_models = {
        'iso': ISO,
    }
    pulp2_collection = 'units_iso'
    pulp3_plugin = 'pulp_file'
    content_models = {
        'iso': Pulp2ISO,
    }
    importer_migrators = {
        'iso_importer': IsoImporter,
    }

    @classmethod
    async def migrate_content_to_pulp3(cls):
        """
        Migrate pre-migrated Pulp 2 ISO content.
        """
        first_stage = ContentMigrationFirstStage(cls)
        dm = DeclarativeContentMigration(first_stage=first_stage)
        await dm.create()
