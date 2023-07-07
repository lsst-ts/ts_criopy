FROM ts-dockerhub.lsst.org/develop-env:develop

ARG cRIO_PY=develop

RUN source ~/.setup.sh \
    && mamba install -y pyside2 asyncqt numpy pytest

RUN cd repos && git clone --branch $cRIO_PY https://github.com/lsst-ts/ts_criopy

RUN echo > .criopy_setup.sh -e \
echo "Configuring environment for criopy" \\n\
source /home/saluser/.setup_salobj.sh \\n\
export OSPL_URI="file:///home/saluser/repos/ts_ddsconfig/python/lsst/ts/ddsconfig/data/config/ospl-shmem.xml" \\n\
export PYTHONPATH="/home/saluser/repos/ts_criopy/python:\$PYTHONPATH" \\n\
export LSST_DDS_PARTITION_PREFIX="summit" \\n\
setup ts_salobj -t current \\n\
ospl start

RUN source ~/.criopy_setup.sh && python3.10 -m pip install PyOpenSSL --upgrade

COPY startup.sh .

SHELL ["/bin/bash", "-lc"]
ENTRYPOINT ["/home/saluser/startup.sh"]
