[![Build Status](https://travis-ci.org/fcollman/AnnotationEngine.svg?branch=master)](https://travis-ci.org/fcollman/AnnotationEngine)
[![codecov](https://codecov.io/gh/fcollman/AnnotationEngine/branch/master/graph/badge.svg)](https://codecov.io/gh/fcollman/AnnotationEngine)

# AnnotationEngine
This is a flask app for adding data to a [DynamicAnnotationDB](https://github.com/seung-lab/DynamicAnnotationDb), and defining the [schemas](annotationengine/schemas) for those annotations.  This is meant to work in concert with a PyChunkedGraph, and a MaterializationEngine to provide a constantly updated, searchable set of annotations in the face of a changing underlying segmentation.   

# Installation
download and install source
```
git clone https://github.com/fcollman/AnnotationEngine.git
cd AnnotationEngine
python setup.py install
```
Presently only python 3.6 is supported and tested.

# Configuration
DynamicAnnotationDb depends upon Google BigTable, so in order to run, you must configure your environment to be able to connect to your google account, so setup the google SDK on your system. 

Then you must edit a configuration file.  See [template](annotationengine/instance/dev_config.py) for example.  Note the emulate flag which will bypass credentials. To specify the path to the cloudvolume segmentation datasets and the bigtable instance that you wish to connect this server to.  You can then specify this configuration file by setting the environment variable ANNOTATION_ENGINE_SETTINGS to the path of the configuration. See (config)[annotationengine/config.py] for details on how the app is configured.

# Running
A development server can be started on port 7000 with
```
python run.py
```

A Dockerfile is provided for running app through uwsgi and nginx for more production deployments. 
