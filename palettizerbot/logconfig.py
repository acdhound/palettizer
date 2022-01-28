import logging.config
import os
import yaml


def configure_local():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )


def configure(path):
    is_local = str(os.environ.get('LOCAL_SERVER')).lower() == 'true'
    if is_local:
        configure_local()
    else:
        if os.path.exists(path):
            with open(path, 'rt') as f:
                try:
                    config = yaml.safe_load(f.read())
                    logging.config.dictConfig(config)
                except Exception as e:
                    print(e)
                    print('Error in Logging Configuration. Using default configs')
                    configure_local()
        else:
            print("Can't find the logging configuration file {}. Using default configs"
                  .format(path))
            configure_local()
