ARG DEVELOP_TAG=c0026.010

FROM lsstts/develop-env:$DEVELOP_TAG AS crio-develop

ARG cRIO_PY=develop

USER root
RUN yum install -y openssh
USER saluser

WORKDIR /home/saluser

RUN source .setup.sh \
    && mamba install -y pyside2 asyncqt numpy pytest \
    && mamba install -y -c lsstts ts-salobj ts-idl

RUN cd repos && git clone --branch $cRIO_PY https://github.com/lsst-ts/ts_cRIOpy

RUN source .setup.sh \
    && echo > .criopy_setup.sh -e \
echo "Configuring environment for cRIOpy" \\n\
source /home/saluser/.setup_salobj.sh \\n\
export PYTHONPATH="/home/saluser/repos/ts_cRIOpy/python:\$PYTHONPATH" \\n\
export OSPL_URI=$(python -c "from lsst.ts import ddsconfig; print( (ddsconfig.get_config_dir() / 'ospl-sp.xml').as_uri())") \\n\
export LSST_DDS_PARTITION_PREFIX="summit" \\n\
export LSST_DDS_DOMAIN_ID=0

COPY startup.sh .

SHELL ["/bin/bash", "-lc"]
ENTRYPOINT ["/home/saluser/startup.sh"]
