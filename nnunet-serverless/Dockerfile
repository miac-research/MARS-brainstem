FROM ubuntu:noble-20250619

LABEL org.opencontainers.image.authors="https://miac.swiss"
LABEL org.opencontainers.image.source="https://github.com/miac-research/MARS-brainstem"
LABEL org.opencontainers.image.url="https://github.com/miac-research/MARS-brainstem"
LABEL org.opencontainers.image.description="Serverless nnU-Net inference endpoint for MARS-brainstem"
LABEL org.opencontainers.image.version="1.0.5"
LABEL version="1.0.5"

ENV nnUNet_raw_data_base=/nnunet/raw \
    nnUNet_preprocessed=/nnunet/preprocessed \
    RESULTS_FOLDER=/nnunet/results \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# OS dependencies, add non-root user, fix locale
RUN apt-get update -qq && apt-get install -y -q --no-install-recommends \
        adduser=3.137* \
        locales=2.39* \
        python-is-python3=3.11.4* \
        python3=3.12.3* \
        python3-pip=24.0* \
        wget=1.21.4* \
 && adduser --system --no-create-home nonroot \
 && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
 && dpkg-reconfigure --frontend=noninteractive locales \
 && update-locale LANG="en_US.UTF-8" \
 && apt-get purge -y --auto-remove \
        adduser \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Create folder structure required by nnU-Net
RUN mkdir -p /nnunet/raw/nnUNet_cropped_data \
    /nnunet/raw/nnUNet_raw_data \
    /nnunet/preprocessed \
    /nnunet/results

# Python dependencies including torch with CUDA 12.8
RUN python3 -m pip install --break-system-packages --no-cache-dir \
        torch --index-url https://download.pytorch.org/whl/cu128 \
 && python3 -m pip install --break-system-packages --no-cache-dir \
        setuptools==69.0.3 \
        wheel==0.42.0 \
        nnunet==1.7.1  \
        fastapi==0.110.2 \
        uvicorn[standard]==0.29.0 \
        numpy==1.26.4 \
        nibabel \
        SimpleITK \
        python-multipart

# Modify nnunet model_restore.py to revert new default setting in torch==2.6 and newer
RUN sed -i 's/map_location=torch.device('\''cpu'\'')/map_location=torch.device('\''cpu'\''), weights_only=False/g' /usr/local/lib/python3.12/dist-packages/nnunet/training/model_restore.py

#  nnU-Net model
WORKDIR /nnunet/results/nnUNet/3d_fullres/Task600_Brainstem/
RUN wget -nv -O nnUNet_brainstem.tar.gz "https://zenodo.org/records/13323293/files/nnUNet_brainstem.tar.gz?download=1" \
 && tar xvf nnUNet_brainstem.tar.gz -C ./ \
 && rm nnUNet_brainstem.tar.gz

# MARS pipeline script and server
WORKDIR /opt/scripts/
COPY pipeline_nnunet.py .
COPY server.py .

USER nonroot
EXPOSE 8000
ENTRYPOINT ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]