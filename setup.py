import setuptools
import re, ast

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('vdu_nlp_services/__init__.py', 'rb') as f:
	version = str(ast.literal_eval(_version_re.search(
		f.read().decode('utf-8')).group(1)))

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = []
with open('requirements.txt', 'r') as f:
  for line in f:
    if line.strip():
      install_requires.append(line.strip())

setuptools.setup(
    name="vdu_nlp_services",
    version=version,
    author="Aleksas Pielikis",
    author_email="ant.kampo@gmail.com",
    description="Python wrapper for VDU NLP online services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aleksas/vdu-nlp-services",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
    install_requires=install_requires
)
