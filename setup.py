from setuptools import setup, find_packages

setup(
    name = 'vk_photo_downloader',
    version = '0.1',
    scripts = ['vk_photo_downloader.py'],
    install_requires = ['requests>=2.1.0'],
)
