import setuptools

setuptools.setup(
    name='markdownup',
    description='Markdown server',
    keywords=['markdown', 'server'],
    version='0.0.21',
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
        'pyjwt',
        'pyyaml',
        'requests'
    ]
)
