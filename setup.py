from distutils.core import setup

setup(
    name='ogame',
    packages=['ogame'],
    version='7.3.0.14',
    license='MIT',
    description='lib for the popular browsergame ogame',
    author='PapeprPieceCode',
    author_email='marcos.gam@hotmail.com',
    url='https://github.com/PiecePaperCode/pyogame2',
    download_url='https://github.com/PiecePaperCode/pyogame2.git',
    keywords=['OGame', 'lib', 'for bots', 'bot'],
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
)
