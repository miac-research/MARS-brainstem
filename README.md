# Container images for deep learning-based brainstem segmentation

This repository contains the code required to build the container images of two **deep learning-based brainstem segmentation methods**, based on MD-GRU or nnU-net.

The methods are described in detail in the corresponding publication:  
*TO BE ADDED*  
Please make sure to cite this publication when using the method, and please note that the license does not cover any commercial use.

> **IMPORTANT:** These methods are **NOT a medical device** and **for non-commercial, academic research use only!**  
Do NOT use these methods for diagnosis, prognosis, monitoring or any other purposes in clinical use.

## Using the pre-built container images

Ready-to-use, pre-built images for MD-GRU and nnU-Net are available for download from the [Github container registry](https://github.com/miac-research/dl-brainstem/packages). These images have been tested with Docker and Apptainer/Singularity.

### Hardware requirements

While the inference can be run on CPU (>8 cores recommended), an NVIDIA GPU will greatly shorten the calculation time. The pre-built images  use CUDA 12 and can thus support a wide range of NVIDIA GPUs from compute capability 5.0 (Maxwell generation, 2014) to 9.0 (current generation). A minimum of 8 GB GPU memory is required.

### nnU-Net algorithm using Docker

```
# 1. Pull the container image into your local registry
docker pull ghcr.io/miac-research/brainstem-nnunet:latest
docker tag ghcr.io/miac-research/brainstem-nnunet:latest brainstem-nnunet:latest

# 2. Run inference on a T1w image in the current working directory using GPU (flag "--gpus all")
docker run --rm --gpus all -v $(pwd):/data  brainstem-nnunet:latest /data/T1.nii.gz

# For advanced usage, see available command line options:
docker run --rm brainstem-nnunet:latest -h
```

### nnU-Net algorithm using Apptainer

```
# 1. Download the container image and save as sif file   
apptainer build brainstem-nnunet.sif docker://ghcr.io/miac-research/brainstem-nnunet:latest

# 2. Run inference on a T1w image in the current working directory using GPU (flag "--nv")
apptainer run -B $(pwd) --nv brainstem-nnunet.sif T1.nii.gz

# For advanced usage, see available command line options:
apptainer run brainstem-nnunet.sif -h
```

### MD-GRU algorithm using Docker

```
# 1. Pull the container image into your local registry
docker pull ghcr.io/miac-research/brainstem-mdgru:latest
docker tag ghcr.io/miac-research/brainstem-mdgru:latest brainstem-mdgru:latest

# 2. Run inference on a T1w image in the current working directory using GPU (flag "--gpus all")
docker run --rm --gpus all -v $(pwd):/data  brainstem-mdgru:latest /data/T1.nii.gz

# For advanced usage, see available command line options:
docker run --rm brainstem-mdgru:latest -h
```

### MD-GRU algorithm using Apptainer

```
# 1. Download the container image and save as sif file   
apptainer build brainstem-mdgru.sif docker://ghcr.io/miac-research/brainstem-mdgru:latest

# 2. Run inference on a T1w image in the current working directory using GPU (flag "--nv")
apptainer run -B $(pwd) --nv brainstem-mdgru.sif T1.nii.gz

# For advanced usage, see available command line options:
apptainer run brainstem-mdgru.sif -h
```

## Building the container images yourself

If you do not want to use the pre-built images, you can build the images yourself locally using the provided Dockerfiles in the `mdgru` and `nnunet` folders.

1. Download the mdgru or nnunet Dockerfile and place it into a local folder.
2. In this folder, run `docker build -t brainstem-{mdgru/nnunet} .`

> During building, base images are downloaded from the NVIDIA NGC registry, scripts are download from this Github repository, and large model files are downloaded from Zenodo.
