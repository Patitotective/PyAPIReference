from setuptools import setup, find_packages

classifiers = [
  "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "Natural Language :: English",  
  "Operating System :: Microsoft :: Windows :: Windows 10",
  "Operating System :: POSIX :: Linux",  
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3.9", 
  "Environment :: X11 Applications :: Qt"
]
 
with open("README.md", "r") as file:
  long_description = file.read()

with open('requirements.txt') as f:
  requirements = f.read().splitlines()

github_url = "https://github.com/Patitotective/PyAPIReference"

setup(
  name="PyAPIReference",
  version="0.1.50",
  author="Cristobal Riaga",
  author_email="cristobalriaga@gmail.com",
  maintainer="Cristobal Riaga", 
  maintainer_email="cristobalriaga@gmail.com",
  url=github_url,  
  project_urls={
    "Website": "https://patitotective.github.io/PyAPIReference/", 
    'Source code': github_url,
    'Changelog': f'{github_url}/blob/main/CHANGELOG.md',
    'Issues': f'{github_url}/issues', 
    'Pull requests': f'{github_url}/pulls', 
    'Discord server': "https://discord.gg/as85Q4GnR6"
  },
  description="Generate API references for Python modules.",
  long_description=open("README.md").read(),
  classifiers=classifiers,
  platforms= ["Windows", "Linux"],
  keywords=["api reference", "api", "api-reference", "app", "application", "qt", "pyqt"],  
  license="MIT", 
  packages=find_packages(),
  install_requires=requirements, 
  long_description_content_type="text/markdown"
)
