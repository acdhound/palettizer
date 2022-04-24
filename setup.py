from setuptools import setup

setup(
   name='palettizer',
   version='0.0.1',
   description='',
   author='Alexander Ivanov',
   author_email='adivanov95@gmail.com',
   packages=['palettizer', 'palettizer.templates', 'palettizerbot'],
   install_requires=[
      'scikit-image >= 0.19.1',
      'scikit-learn >= 1.0.2',
      'numpy >= 1.22.0',
      'imageio >= 2.13.5',
      'python-telegram-bot',
      'pyyaml >= 6.0',
      'faiss-cpu >= 1.7.2',
      'Jinja2'
   ],
   python_requires=">=3.6",
   extras_require={
      'test': ['pytest']
   },
   package_data={
        "": ["resources/*.*"],
        "palettizer.templates": ["*.*"]
    }
)
