# coding=utf-8
import os
from setuptools import setup, find_packages
from version import get_version

version = get_version()

setup(name='Products.GSContentManager',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
      "Development Status :: 4 - Beta",
      "Environment :: Web Environment",
      "Framework :: Zope2",
      "Intended Audience :: Developers",
      "License :: Other/Proprietary License",
      "Natural Language :: English",
      "Operating System :: POSIX :: Linux"
      "Programming Language :: Python",
      "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Michael JasonSmith',
      author_email='mpj17@onlinegroups.net',
      url='http://groupserver.org',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            'setuptools',
            'pytz',
            'zope.app.apidoc',
            'zope.app.form',
            'zope.app.publisher',
            'zope.component',
            'zope.contentprovider',
            'zope.formlib',
            'zope.interface',
            'zope.pagetemplate',
            'zope.publisher',
            'zope.schema',
            'zope.size',
            'zope.viewlet',
            'Zope2',
            'AccessControl',
            'gs.content.base',
            'gs.content.form',
            'Products.GSAuditTrail',
            'Products.CustomUserFolder',
            'Products.XWFCore',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
