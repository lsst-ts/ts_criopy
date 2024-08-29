FROM lsstts/develop-env:develop

ARG cRIO_PY=develop

RUN source ~/.setup.sh \
    && mamba install -y pyside6 qasync numpy pytest

RUN cd repos/ts_criopy && git checkout $cRIO_PY

RUN echo > .criopy_setup.sh -e \
echo "Configuring environment for criopy" \\n\
source /home/saluser/.setup_salobj.sh \\n\
export OSPL_URI="file:///home/saluser/repos/ts_ddsconfig/python/lsst/ts/ddsconfig/data/config/ospl-shmem.xml" \\n\
export PYTHONPATH="/home/saluser/repos/ts_criopy/python:\$PYTHONPATH" \\n\
export LSST_DDS_PARTITION_PREFIX="summit" \\n\
export QT_API="pyside6" \\n\
setup ts_salobj -t current \\n

RUN source ~/.criopy_setup.sh && cd repos/ts_criopy && pip install .

COPY startup.sh /home/saluser/

SHELL ["/bin/bash", "-lc"]
ENTRYPOINT ["/home/saluser/startup.sh"]
