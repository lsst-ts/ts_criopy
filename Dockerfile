FROM lsstts/develop-env:c0041.000

ARG cRIO_PY=develop

RUN source ~/.setup.sh \
    && mamba install -y pyside6 qasync numpy pytest

RUN cd /opt/lsst/tssw/ts_criopy && git fetch && git checkout $cRIO_PY && git pull

RUN echo > .criopy_setup.sh -e \
echo "Configuring environment for criopy" \\n\
source /home/saluser/.setup_salobj.sh \\n\
export PYTHONPATH="/home/saluser/repos/ts_criopy/python:\$PYTHONPATH" \\n\
export LSST_DDS_PARTITION_PREFIX="summit" \\n\
export QT_API="pyside6" \\n\
setup ts_salobj -t current \\n\
export LSST_TOPIC_SUBNAME=sal \\n\
export LSST_KAFKA_BROKER_ADDR="<fill>" \\n\
export LSST_SCHEMA_REGISTRY_URL="<fill>" \\n\
export LSST_KAFKA_REPLICATION_FACTOR=3 \\n\
export LSST_KAFKA_SECURITY_USERNAME="<fill>" \\n\
export LSST_KAFKA_SECURITY_PASSWORD="<fill>" \\n\
export LSST_KAFKA_SECURITY_PROTOCOL=SASL_SSL \\n\
export LSST_KAFKA_SECURITY_MECHANISM=SCRAM-SHA-512 \\n\
export LSST_KAFKA_LOCAL_SCHEMAS=/opt/lsst/tssw/ts_sal/kafka \\n\
\\n\
export LSST_KAFKA_HOST=${LSST_KAFKA_BROKER_ADDR%:*} \\n\
export LSST_KAFKA_BROKER_PORT=${LSST_KAFKA_BROKER_ADDR##*:} \\n\
export LSST_KAFKA_PREFIX=${LSST_TOPIC_SUBNAME} \\n

RUN source ~/.criopy_setup.sh && \
    cd /opt/lsst/tssw/ts_m1m3_utils && pip install . && \
    cd /opt/lsst/tssw/ts_criopy && pip install .

COPY startup.sh /home/saluser/

SHELL ["/bin/bash", "-lc"]
ENTRYPOINT ["/home/saluser/startup.sh"]
