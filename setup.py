from setuptools import setup, find_packages
 
setup(
    name='nailbiter',
    version=__import__('nailbiter').__version__,
    description='thumbnail generation modeled after sorl-thumbnail, plays nice with storage backends',
    author='Luke Hutscal',
    author_email='luke@creaturecreative.com',
    url='http://github.com/girasquid/django-nailbiter/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)