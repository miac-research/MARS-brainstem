FROM nvcr.io/nvidia/tensorflow:23.03-tf1-py3

LABEL org.opencontainers.image.authors="https://miac.swiss"
LABEL org.opencontainers.image.source="https://github.com/miac-research/MARS-brainstem"
LABEL org.opencontainers.image.url="https://github.com/miac-research/MARS-brainstem"
LABEL org.opencontainers.image.description="Ready-to-use container image for MARS-brainstem using MD-GRU"
LABEL org.opencontainers.image.version="1.0.5"
LABEL version="1.0.5"

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# Python dependencies
RUN python3 -m pip install --no-cache-dir \
        nibabel==3.2.1 \
        pydicom==2.2.2 \
        pynrrd==0.4.2 \
        scikit-image==0.19.1 \
        setproctitle==1.2.2 \
        visdom==0.1.8.9 \
 && python3 -m pip install --no-cache-dir --no-deps git+https://github.com/spezold/mvloader.git@4244ba3 \
 && python3 -m pip install --no-cache-dir --no-deps --force-reinstall \
        future==0.18.2 \
        SimpleITK==2.0.1

# Clone MD-GRU
WORKDIR /opt
RUN git clone https://github.com/miac-research/mdgru.git \
 && cd mdgru \
 && git reset --hard 791ee4f

# MD-GRU model
WORKDIR /model
RUN wget -nv -O brainstem_140000.data-00000-of-00001 "https://zenodo.org/records/12578294/files/brainstem_140000.data-00000-of-00001?download=1" \
 && wget -nv -O brainstem_140000.index "https://zenodo.org/records/12578294/files/brainstem_140000.index?download=1" \
 && wget -nv -O brainstem_140000.meta "https://zenodo.org/records/12578294/files/brainstem_140000.meta?download=1"

# MARS pipeline script
WORKDIR /opt/scripts/
COPY pipeline_mdgru.py .

RUN adduser --system --no-create-home nonroot
USER nonroot
ENTRYPOINT ["python", "/opt/scripts/pipeline_mdgru.py"]
