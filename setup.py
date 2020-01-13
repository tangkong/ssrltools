"""
Packaging setup for ssrltools
"""

from setuptools import setup
import ssrltools as package


setup(
    author           = package.__author__,
    version          = package.__version__,
    author_email     = package.__author_email__,
    classifiers      = package.__classifiers__,
    description      = package.__description__,
    #entry_points     = __entry_points__,
    license          = package.__license__,
    long_description = package.__long_description__,
    #install_requires = package.__install_requires__,
    name             = package.__project__,
    #platforms        = package.__platforms__,
    #packages         = find_packages(exclude=package.__exclude_project_dirs__),
    #url              = package.__url__,
    #version          = versioneer.get_version(),
    #cmdclass         = versioneer.get_cmdclass(),
    zip_safe         = package.__zip_safe__,
    python_requires  = package.__python_version_required__,
 )