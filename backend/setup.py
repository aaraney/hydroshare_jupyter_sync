# comment outs were to test different package install methods while troubleshooting server incapability
from distutils.core import setup
# import setuptools

# setuptools.setup(
#     name='hydroshare_gui',
#     version='0.1.0',
#     author='CUAHSI SCOPE team 2019',
#     author_email='scope-cuahsi@olin.edu',
#     packages=[],
#     url='',
#     license='',
#     description='hydroshare gui app.',
#     install_requires=['notebook>=5.5.0', 'tornado'],
# )

setup(
    name='hydroshare_gui',
    version='0.1.0',
    author='CUAHSI SCOPE team 2019',
    author_email='scope-cuahsi@olin.edu',
    packages=[],
    url='',
    license='',
    description='hydroshare gui app.',
    install_requires=['notebook>=5.5.0', 'tornado'],
)