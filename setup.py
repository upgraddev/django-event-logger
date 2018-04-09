try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='django-event-logger',
    version='0.0.0',
    description="""Django app to log events based on model changes.""",
    long_description='...',
    author='UpGrad',
    packages=[
        'event_logger',
    ],
    include_package_data=True,
    keywords='django-event-logger',
)
