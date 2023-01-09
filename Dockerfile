FROM lsstts/develop-env:c0026.010

ARG cRIO_PY=develop

USER root
RUN yum install -y openssh
USER saluser

WORKDIR /home/saluser

RUN source ~/.setup.sh \
    && mamba install -y pyside2 asyncqt numpy pytest \
    && mamba install -y -c lsstts ts-salobj ts-idl

RUN cd repos && git clone --branch $cRIO_PY https://github.com/lsst-ts/ts_cRIOpy \
    && cd ts_xml && git checkout develop && git pull \
    && cd ../ts_sal && git checkout develop && git pull

RUN echo > .criopy_setup.sh -e \
echo "Configuring environment for cRIOpy" \\n\
source /home/saluser/.setup_salobj.sh \\n\
export PYTHONPATH="/home/saluser/repos/ts_cRIOpy/python:/home/saluser/repos/ts_xml/python:/home/saluser/repos/ts_sal/python:\$PYTHONPATH" \\n\
export OSPL_URI=$(python -c "from lsst.ts import ddsconfig; print( (ddsconfig.get_config_dir() / 'ospl-sp.xml').as_uri())") \\n\
export LSST_DDS_PARTITION_PREFIX="summit" \\n\
export LSST_DDS_DOMAIN_ID=0

RUN source ~/.criopy_setup.sh && make_idl_files.py MTM1M3 MTM1M3TS MTVMS MTMount \
    && python3.10 -m pip install PyOpenSSL --upgrade

COPY startup.sh .

SHELL ["/bin/bash", "-lc"]
ENTRYPOINT ["/home/saluser/startup.sh"]
