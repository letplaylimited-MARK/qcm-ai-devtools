"""
QCM工具系统安装配置
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='qcm-ai-devtools',
    version='0.4.0',
    description='QCM AI开发工具平台 - 与 ai-skill-system 无缝对接',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='QCM Team',
    author_email='qcm-team@example.com',
    url='https://github.com/qcm-ai-devtools/qcm-ai-devtools',
    
    packages=find_packages(exclude=['tests', 'examples']),
    
    install_requires=[
        'pyyaml>=6.0',
    ],
    
    extras_require={
        'cli': [
            'typer>=0.9.0',
            'rich>=13.0.0',
        ],
        'dev': [
            'pytest>=7.0',
            'pytest-cov>=4.0',
            'pylint>=2.15',
            'bandit>=1.7',
            'radon>=5.1',
        ],
        'quality': [
            'pylint>=2.15',
            'bandit>=1.7',
            'radon>=5.1',
            'pytest-cov>=4.0',
        ]
    },
    
    entry_points={
        'console_scripts': [
            'qcm=qcm_tools.cli:app',
        ],
    },
    
    python_requires='>=3.7',
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Quality Assurance',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    
    keywords='qcm ai development tools workflow automation',
)
