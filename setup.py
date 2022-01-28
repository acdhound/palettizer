from setuptools import setup

setup(
   name='palettizer',
   version='0.0.1',
   description='',
   author='Alexander Ivanov',
   author_email='adivanov95@gmail.com',
   packages=['palettizer', 'palettizerbot'],
   install_requires=[
      'scikit-image',
      'scikit-learn',
      'numpy',
      'python-telegram-bot',
      'pyyaml'
   ],
   python_requires=">=3.6",
   extras_require={
      'test': ['pytest']
   }
)
