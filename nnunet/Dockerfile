FROM nvcr.io/nvidia/cuda:12.8.1-base-ubuntu22.04

LABEL org.opencontainers.image.authors="https://miac.swiss"
LABEL org.opencontainers.image.source="https://github.com/miac-research/MARS-brainstem"
LABEL org.opencontainers.image.url="https://github.com/miac-research/MARS-brainstem"
LABEL org.opencontainers.image.description="Ready-to-use container image for MARS-brainstem using nnU-Net"
LABEL org.opencontainers.image.version="1.0.4"
LABEL version="1.0.4"

# Set environment variables
ENV nnUNet_raw_data_base=/nnunet/raw \
    nnUNet_preprocessed=/nnunet/preprocessed \
    RESULTS_FOLDER=/nnunet/results \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# Install OS dependencies and fix locale
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        locales=2.35* \
        python3=3.10.6* \
        python3-pip=22.0.2* \
        python-is-python3 \
        wget=1.21.2* && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG="en_US.UTF-8" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create folder structure required by nnU-Net
RUN mkdir -p /nnunet/raw/nnUNet_cropped_data \
    /nnunet/raw/nnUNet_raw_data \
    /nnunet/preprocessed \
    /nnunet/results

# Install Python dependencies including torch with CUDA 12.8
RUN python3 -m pip install --no-cache-dir --upgrade \
        pip==23.3.2 && \
    python3 -m pip install --no-cache-dir \
        torch --index-url https://download.pytorch.org/whl/cu128 && \
    python3 -m pip install --no-cache-dir \
        setuptools==69.0.3 \
        wheel==0.42.0 \
        nnunet==1.7.1 && \
    python3 -m pip install --no-cache-dir --no-deps --force-reinstall \
        numpy==1.23.5

# Modify nnunet model_restore.py to revert new default setting in torch==2.6 and newer
RUN sed -i 's/map_location=torch.device('\''cpu'\'')/map_location=torch.device('\''cpu'\''), weights_only=False/g' /usr/local/lib/python3.10/dist-packages/nnunet/training/model_restore.py

# Download nnU-Net model
WORKDIR /nnunet/results/nnUNet/3d_fullres/Task600_Brainstem/
RUN wget -nv -O nnUNet_brainstem.tar.gz "https://zenodo.org/records/13323293/files/nnUNet_brainstem.tar.gz?download=1" && \
    tar xvf nnUNet_brainstem.tar.gz -C ./ && \
    rm nnUNet_brainstem.tar.gz

# Download Python pipeline script
WORKDIR /opt/scripts/
RUN wget -nv -O pipeline_nnunet.py "https://raw.githubusercontent.com/miac-research/MARS-brainstem/main/nnunet/pipeline_nnunet.py" && \
    chmod +x pipeline_nnunet.py

# Add nonroot user and switch to it
RUN adduser --system --no-create-home nonroot
USER nonroot

ENTRYPOINT ["python", "/opt/scripts/pipeline_nnunet.py"]
