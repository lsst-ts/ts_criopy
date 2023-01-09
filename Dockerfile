FROM lsstts/develop-env:c0026.010

ARG cRIO_PY=develop

RUN source ~/.setup.sh \
    && mamba install -y pyside2 asyncqt numpy pytest

RUN cd repos && git clone --branch $cRIO_PY https://github.com/lsst-ts/ts_cRIOpy

RUN echo > .criopy_setup.sh -e \
echo "Configuring environment for cRIOpy" \\n\
source /home/saluser/.setup_salobj.sh \\n\
export PYTHONPATH="/home/saluser/repos/ts_cRIOpy/python:\$PYTHONPATH" \\n\
export LSST_DDS_PARTITION_PREFIX="summit" \\n \
setup ts_salobj -t current

RUN source ~/.criopy_setup.sh && python3.10 -m pip install PyOpenSSL --upgrade

COPY startup.sh .

SHELL ["/bin/bash", "-lc"]
ENTRYPOINT ["/home/saluser/startup.sh"]
