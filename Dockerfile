FROM continuumio/miniconda3

COPY requirements.txt /tmp/requirements.txt 
RUN apt-get update && \
    apt-get install -y build-essential nginx supervisor && \
    conda install numpy && \
    pip install --upgrade pip && \
    pip install flask && \
    pip install git+https://github.com/seung-lab/DynamicAnnotationDB.git#egg=dynamicannotationdb && \
    pip install git+https://github.com/seung-lab/PyChunkedGraph.git#egg=pychunkedgraph && \
    pip install git+https://github.com/seung-lab/EMAnnotationSchemas.git#egg=emannotationschemas && \
    pip install -r /tmp/requirements.txt && \
    apt-get remove -y build-essential && apt autoremove -y && \
    rm -rf /root/.cache && \
    rm -rf /var/lib/apt/lists/*
RUN conda update -n base conda
RUN conda install -c conda-forge uwsgi 
# ENV ANNOTATION_ENGINE_SETTINGS /annotationengine/annotationengine/instance/dev_config.py

# Copy the Nginx global conf
COPY ./docker/nginx.conf /etc/nginx/
# Copy the Flask Nginx site conf
COPY ./docker/flask-site-nginx.conf /etc/nginx/conf.d/
# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY ./docker/uwsgi.ini /etc/uwsgi/
# Custom Supervisord config
COPY ./docker/supervisord.conf /etc/supervisord.conf

COPY gcloud/install_gcloud.sh /root/install_gcloud.sh
RUN /bin/bash -c /root/install_gcloud.sh

# Add demo app
COPY . /annotationengine
WORKDIR /annotationengine
RUN python setup.py install
RUN useradd -ms /bin/bash nginx
RUN mkdir -p /home/nginx/.cloudvolume/secrets && chown -R nginx /home/nginx
EXPOSE 4000
ENV PYTHONPATH=/annotationengine
ENTRYPOINT ["/annotationengine/docker/entrypoint.sh"]
CMD ["/usr/bin/supervisord","-c","/etc/supervisord.conf"]