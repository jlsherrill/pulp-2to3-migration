# pulp-2to3-migration

A [Pulp 3](https://pulpproject.org/) plugin to migrate from Pulp 2 to Pulp 3.

### Requirements

* /var/lib/pulp is shared from Pulp 2 machine
* access to Pulp 2 database

### Configuration
On Pulp 2 machine:

1. Make sure MongoDB listens on the IP address accesible outside, it should be configured as
one of the `bindIP`s in /etc/mongod.conf.

2. In case /var/lib/pulp is not on a shared filesystem, configure NFS server and share
that directory. E.g. on Fedora/CentOS:

```
$ sudo dnf install nfs-utils
$ sudo systemctl start nfs-server
$ sudo vi /etc/exports:

        /var/lib/pulp          <Pulp 3 IP address>(rw,sync,no_root_squash,no_subtree_check)

$ sudo exportfs -a
```

On Pulp 3 machine:
1. Mount /var/lib/pulp to your Pulp 3 storage location. By default, it's /var/lib/pulp. E.g. on
Fedora/Centos:

```
$ sudo dnf install nfs-utils
$ sudo mount <IP address of machine which exports /var/lib/pulp>:/var/lib/pulp /var/lib/pulp
```

2. Configure your connection to MongoDB in /etc/pulp/settings.py. You can use the same configuration
 as you have in Pulp 2 (only seeds might need to be different, it depends on your setup).

E.g.
```python
PULP2_MONGODB = {
    'name': 'pulp_database',
    'seeds': '<your MongoDB bindIP>:27017',
    'username': '',
    'password': '',
    'replica_set': '',
    'ssl': False,
    'ssl_keyfile': '',
    'ssl_certfile': '',
    'verify_ssl': True,
    'ca_path': '/etc/pki/tls/certs/ca-bundle.crt',
}
```

### Installation

Clone the repository and install it.
```
$ git clone https://github.com/pulp/pulp-2to3-migration.git
$ pip install -e pulp-2to3-migration
```

### User Guide

All the commands should be run on Pulp 3 machine.

1. Create a Migration Plan
```
$ # migrate content for Pulp 2 ISO plugin
$ http POST :24817/pulp/api/v3/migration-plans/ plan='{"plugins": [{"type": "iso"}]}'

HTTP/1.1 201 Created
{
    "pulp_created": "2019-07-23T08:18:12.927007Z",
    "pulp_href": "/pulp/api/v3/migration-plans/59f8a786-c7d7-4e2b-ad07-701479d403c5/",
    "plan": "{ \"plugins\": [{\"type\": \"iso\"}]}"
}

```

2. Use the ``pulp_href`` of the created Migration Plan to run the migration
```
$ http POST :24817/pulp/api/v3/migration-plans/59f8a786-c7d7-4e2b-ad07-701479d403c5/run/

HTTP/1.1 202 Accepted
{
    "task": "/pulp/api/v3/tasks/55db2086-cf2e-438f-b5b7-cd0dbb7c8cf4/"
}

```

### Plugin Writer's Guide

If you are extending this migration tool to be able to migrate the plugin of your interest
from Pulp 2 to Pulp 3, here are some guidelines.


1. Create a migrator class (subclass the provided `Pulp2to3PluginMigrator` class). There should be
 one migrator class per plugin. Define all the necessary attributes and methods for it (see
  `Pulp2to3PluginMigrator` for more details)

2. Discovery of the plugins is done via entry_points. Add your migrator class defined in step 1
 to the list of the "migrators" entry_points in setup.py.

3. Add a Content model to communicate with Pulp 2.
 - It has to have a field `type` which will correspond to the `_content_type_id` of your Content
 in Pulp 2. Don't forget to add it to PULP_2TO3_CONTENT_MODEL_MAP in step 1.

4. Add a Content model to pre-migrate Pulp 2 content to (subclass the provided `Pulp2to3Content`
class). It has to have:
 - a field `type` which will correspond to the `_content_type_id` of your Content in Pulp 2.
 - on a Meta class a `default_related_name` set to `<your pulp 2 content type>_detail_model`
 - a classmethod `pre_migrate_content_detail` (see `Pulp2to3Content` for more details)
 - a method `create_pulp3_content` (see `Pulp2to3Content` for more details)

 If your content has one artifact and if you are willing to use the default implementation of the
 first stage of DeclarativeContentMigration, on your Content model you also need:
 - an `expected_digests` property to provide expected digests for artifact creation/validation
 - an `expected_size` property to provide the expected size for artifact creation/validation
 - a `relative_path_for_content_artifact` property to provide the relative path for content
 artifact creation.

 5. Subclass the provided `Pulp2to3Importer` class and define `migrate_to_pulp3` method which
  create a plugin Remote instance based on the provided pre-migrated `Pulp2Importer`.
