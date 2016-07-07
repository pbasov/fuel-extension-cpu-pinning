import os

from setuptools import setup
from setuptools.command.install import install

from nailgun.db import db
from nailgun.db.sqlalchemy.models import Cluster
from nailgun.db.sqlalchemy.models import Release


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('migrations')


class ExtInstall(install):
    @classmethod
    def _set_extensions(self, nailgun_objects):
        for obj, extensions in nailgun_objects.items():
            extensions.append(u'cpu_pinning_override')
            extensions = list(set(extensions))
            obj.extensions = extensions
            db().flush()

    def run(self):
        install.run(self)
        clusters = {cl: cl['extensions'] for cl in db().query(Cluster).all()}
        releases = {rl: rl['extensions'] for rl in db().query(Release).all()}
        ExtInstall._set_extensions(clusters)
        ExtInstall._set_extensions(releases)
        db().commit()

setup(
       name='fuel_extension_cpu_pinning',
       version='1.0',
       description='CPU pinning overrides',
       author='Pavel Basov, Dmitry Ukov',
       author_email='pbasov@mirantis.com',
       url='http://example.com',
       classifiers=['Development Status :: 3 - Alpha',
                    'License :: OSI Approved :: Apache Software License',
                    'Programming Language :: Python',
                    'Programming Language :: Python :: 2',
                    'Environment :: Console',
                    ],
       packages=['fuel_extension_cpu_pinning'],
       package_data={'fuel_extension_cpu_pinning': extra_files},
       cmdclass={'install': ExtInstall},
       entry_points={
          'nailgun.extensions': [
             'fuel_extension_cpu_pinning = fuel_extension_cpu_pinning.extension:CpuPinningExtension',
           ],
           'fuelclient': [
              'cpu-pinning-set = fuel_extension_cpu_pinning.fuelclient:SetPinning',
              'cpu-pinning-get = fuel_extension_cpu_pinning.fuelclient:GetPinning',
              'cpu-pinning-del = fuel_extension_cpu_pinning.fuelclient:DelPinning',
           ]
       },
       zip_safe=False,
)
