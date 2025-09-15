# Stage 1
FROM ubuntu:noble-20250619 AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

RUN apt-get update -qq && apt-get install -y -q --no-install-recommends \
    python-is-python3=3.11.4* \
    python3=3.12.3* \
    python3.12-venv=3.12.3* \
    python3-pip=24.0* \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

RUN python -m venv /venv \
 && /venv/bin/pip install --upgrade pip \
 && /venv/bin/pip install --no-cache-dir --prefer-binary \
        torch --index-url https://download.pytorch.org/whl/cu128 \
 && /venv/bin/pip install --no-cache-dir --prefer-binary \
        setuptools==69.0.3 \
        wheel==0.42.0 \
        nnunet==1.7.1

# Modify nnunet model_restore.py to revert new default setting in torch==2.6 and newer
RUN sed -i 's/map_location=torch.device('\''cpu'\'')/map_location=torch.device('\''cpu'\''), weights_only=False/g' /venv/lib/python3.12/site-packages/nnunet/training/model_restore.py

# venv finalization and clean-up
RUN /venv/bin/pip install --no-cache-dir --prefer-binary --force-reinstall \
        numpy==1.26.4 \
 && find /venv -type d -name '__pycache__' -exec rm -rf {} + \
 && find /venv -type f -name '*.pyc' -delete


# Stage 2 
FROM ubuntu:noble-20250619 AS final

LABEL org.opencontainers.image.authors="https://miac.swiss"
LABEL org.opencontainers.image.source="https://github.com/miac-research/MARS-brainstem"
LABEL org.opencontainers.image.url="https://github.com/miac-research/MARS-brainstem"
LABEL org.opencontainers.image.description="Ready-to-use container image for MARS-brainstem using nnU-Net"
LABEL org.opencontainers.image.version="1.0.5"
LABEL version="1.0.5"

ENV nnUNet_raw_data_base=/nnunet/raw \
    nnUNet_preprocessed=/nnunet/preprocessed \
    RESULTS_FOLDER=/nnunet/results \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/venv \
    PATH="/venv/bin:$PATH"

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

#  nnU-Net model
WORKDIR /nnunet/results/nnUNet/3d_fullres/Task600_Brainstem/
RUN wget -nv -O nnUNet_brainstem.tar.gz "https://zenodo.org/records/13323293/files/nnUNet_brainstem.tar.gz?download=1" \
 && tar xvf nnUNet_brainstem.tar.gz -C ./ \
 && rm nnUNet_brainstem.tar.gz

# Copy venv from builder stage
COPY --from=builder /venv /venv 

# MARS script
WORKDIR /opt/scripts/
COPY pipeline_nnunet.py .

USER nonroot
ENTRYPOINT ["python", "/opt/scripts/pipeline_nnunet.py"]
