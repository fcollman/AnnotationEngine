# Define the application directory
import os
from annotationengine.utils import get_app_base_path


class BaseConfig(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # Statement for enabling the development environment
    DEBUG = True
    proj_dir = os.path.split(get_app_base_path())[0]
    DATASETS = [{
        'name': 'pinky40',
        'CV_SEGMENTATION_PATH': "gs://neuroglancer/svenmd/pinky40_v11/watershed"
        .format(proj_dir)
    }]

    NEUROGLANCER_URL = "https://neuroglancer-demo.appspot.com"
    BIGTABLE_CONFIG = {
        'instance_id': 'pychunkedgraph',
        'project_id': "neuromancer-seung-import"
    }

    CHUNKGRAPH_TABLE_ID = "pinky40_fanout2_v7"

config = {
    "development": "annotationengine.config.BaseConfig",
    "testing": "annotationengine.config.BaseConfig",
    "default": "annotationengine.config.BaseConfig"
}


def configure_app(app):
    config_name = os.getenv('FLASK_CONFIGURATION', 'default')
    # object-based default configuration
    app.config.from_object(config[config_name])
    if 'ANNOTATION_ENGINE_SETTINGS' in os.environ.keys():
        app.config.from_envvar('ANNOTATION_ENGINE_SETTINGS')
    # instance-folders configuration
    app.config.from_pyfile('config.cfg', silent=True)

    return app
