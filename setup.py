from setuptools import setup

setup(
       name='fuel_extension_cpu_pinning',
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
       packages=['fuel_extension_cpu_pinning'],
       entry_points={
          'nailgun.extensions': [
             'fuel_extension_cpu_pinning = fuel_extension_cpu_pinning.extension:CpuPinningExtension',
           ],
           'fuelclient': [
              'cpu-pinning-set = fuel_extension_cpu_pinning.fuelclient:SetPinning',
              'cpu-pinning-get = fuel_extension_cpu_pinning.fuelclient:GetPinning',
           ]
       },
       zip_safe=False,
)
