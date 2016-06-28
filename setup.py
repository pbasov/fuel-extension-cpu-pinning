from setuptools import setup

setup(
       name='fuel-extension-cpu-pinning',
       version='1.0',
       description='Demonstration package for Nailgun Extensions',
       author='Fuel Nailgman',
       author_email='fuel@nailgman.com',
       url='http://example.com',
       classifiers=['Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: Apache Software License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Environment :: Console',
                   ],
       packages=['fuel-extension-cpu-pinning'],
       entry_points={
          'nailgun.extensions': [
             'test_ext = fuel-extension-cpu-pinning.extension:CpuPinningExtension',
           ],
       },
       zip_safe=False,
)