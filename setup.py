import setuptools

setuptools.setup(
    name='markdownup',
    description='Markdown server',
    keywords=['markdown', 'server'],
    version='0.0.7',
    author='Binokkio',
    author_email='binokkio@b.nana.technology',
    url='https://github.com/binokkio/markdownup',
    license='LGPLv3+',
    packages=['markdownup'],
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'chevron',
        'gunicorn',
        'markdown',
        'pygments',
        'pyyaml'
    ]
)
