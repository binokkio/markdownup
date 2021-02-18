from pathlib import Path

import setuptools

setuptools.setup(
    name='markdownup',
    description='Markdown server',
    long_description=(Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown',
    keywords=['markdown', 'server'],
    version='0.0.40',
    author='Binokkio',
    author_email='binokkio@b.nana.technology',
    url='https://github.com/binokkio/markdownup',
    license='LGPLv3+',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'chevron',
        'gunicorn',
        'markdown',
        'pygments',
        'pyjwt>=2',
        'pyyaml',
        'requests'
    ]
)
