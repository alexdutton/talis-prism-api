from distutils.core import setup

setup(
    name = 'talisprism',
    version = '0.1',
    url = 'http://github.com/alexsdutton/talis-prism-api',
    author = 'Alexander Dutton',
    author_email = 'dev@alexdutton.co.uk',
    license = 'http://creativecommons.org/publicdomain/zero/1.0/',
    description ="A simple wrapper around a Talis Prism patron services HTTP interface.",
    packages = ['talisprism'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: Public Domain',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Internet :: WWW/HTML',
    ],
)

