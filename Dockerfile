ARG DEVELOP_TAG=c0022.001

FROM lsstts/develop-env:$DEVELOP_TAG AS crio-develop

ARG cRIO_PY=develop

WORKDIR /home/saluser

RUN source .setup.sh \
    && conda install -y pyside2 asyncqt \
    && conda install -y -c lsstts ts-salobj ts-idl

RUN cd repos && git clone --branch $cRIO_PY https://github.com/lsst-ts/ts_cRIOpy

RUN source .setup.sh \
    && echo > .criopy_setup.sh -e \
echo "Configuring environment for cRIOpy" \\n\
source /home/saluser/.setup_salobj.sh \\n\
export PYTHONPATH="/home/saluser/repos/ts_cRIOpy/python:\$PYTHONPATH" \\n\
export LSST_DDS_PARTITION_PREFIX="test" \\n

COPY startup.sh .

SHELL ["/bin/bash", "-lc"]
ENTRYPOINT ["/home/saluser/startup.sh"]
