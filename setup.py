import io
from setuptools import setup

with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='ptb-pagination',
    version='0.0.1',
    url='https://github.com/wiltonsr/ptb-pagination',
    license='MIT',
    author='Wilton Rodrigues',
    author_email='wiltonsr94@gmail.com',
    description='Python inline keyboard pagination for Telegram Bot API.',
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    platforms='any',
    install_requires=[
        'python-telegram-bot>=13.6',
    ],
)
