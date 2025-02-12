# Container images for deep learning-based brainstem segmentation

This repository contains the code required to build the container images of two **deep learning-based brainstem segmentation methods**, based on nnU-net or MD-GRU.

The methods are described in detail in the following publication: 
 
> **B. Gesierich, L. Sander, et al. 2025. Extended technical and clinical validation of deep learning-based brainstem segmentation for application in neurodegenerative diseases. Human Brain Mapping. DOI: [10.1002/hbm.70141](https://doi.org/10.1002/hbm.70141).**

Please ensure to cite this publication when using the methods, and please note that the license does not cover any commercial use (defined as use for which any financial return is received). Please also cite the underlying deep learning method (nnU-Net, DOI: [10.1038/s41592-020-01008-z](https://doi.org/10.1038/s41592-020-01008-z) or MD-GRU, DOI: [10.1007/978-3-319-75238-9_3](https://doi.org/10.1007/978-3-319-75238-9_3)).

> [!CAUTION]
> These methods are **NOT medical devices** and **for non-commercial, academic research use only!**  
> Do NOT use these methods for diagnosis, prognosis, monitoring or any other purposes in clinical use.

## Using the pre-built container images

Ready-to-use, pre-built images for nnU-Net and MD-GRU brainstem segmentaion are available for download from the [Github container registry](https://github.com/miac-research/dl-brainstem/packages). The images have been tested with Apptainer and Docker.  

In general, we recommend the nnU-Net algorithm (please see our publication for a detailed comparison between the two algorithms) and using Apptainer (the standard container tool for scientific computing).

### Hardware requirements

While the inference can be run on CPU (>8 cores recommended), an NVIDIA GPU will greatly accelerate the calculation. The pre-built images use CUDA 12 and can thus support a wide range of NVIDIA GPUs from compute capability 5.0 (Maxwell generation, 2014) to 9.0 (H100, RTX 6000 Ada). A minimum of 8 GB GPU memory is required.

### nnU-Net algorithm using Apptainer

```shell
# 1. Pull the container image and save as .sif file   
apptainer build brainstem-nnunet.sif docker://ghcr.io/miac-research/brainstem-nnunet:latest

# 2. Run inference on a T1w image in the current working directory using GPU (flag "--nv")
apptainer run -B $(pwd) --nv brainstem-nnunet.sif T1.nii.gz

# For advanced usage, see available command line options:
apptainer run brainstem-nnunet.sif -h
```

### nnU-Net algorithm using Docker

```shell
# 1. Pull the container image into your local registry
docker pull ghcr.io/miac-research/brainstem-nnunet:latest
docker tag ghcr.io/miac-research/brainstem-nnunet:latest brainstem-nnunet:latest

# 2. Run inference on a T1w image in the current working directory using GPU (flag "--gpus all")
docker run --rm --gpus all -v $(pwd):/data  brainstem-nnunet:latest /data/T1.nii.gz

# For advanced usage, see available command line options:
docker run --rm brainstem-nnunet:latest -h
```

### MD-GRU algorithm using Apptainer

```shell
# 1. Pull the container image and save as .sif file   
apptainer build brainstem-mdgru.sif docker://ghcr.io/miac-research/brainstem-mdgru:latest

# 2. Run inference on a T1w image in the current working directory using GPU (flag "--nv")
apptainer run -B $(pwd) --nv brainstem-mdgru.sif T1.nii.gz

# For advanced usage, see available command line options:
apptainer run brainstem-mdgru.sif -h
```

### MD-GRU algorithm using Docker

```shell
# 1. Pull the container image into your local registry
docker pull ghcr.io/miac-research/brainstem-mdgru:latest
docker tag ghcr.io/miac-research/brainstem-mdgru:latest brainstem-mdgru:latest

# 2. Run inference on a T1w image in the current working directory using GPU (flag "--gpus all")
docker run --rm --gpus all -v $(pwd):/data  brainstem-mdgru:latest /data/T1.nii.gz

# For advanced usage, see available command line options:
docker run --rm brainstem-mdgru:latest -h
```

## Building the container images yourself

If you prefer to build the container images yourself, you can use the provided Dockerfiles in the `mdgru` and `nnunet` folders.

1. Download the mdgru or nnunet Dockerfile and place it into a folder.
2. In this folder, run `docker build -t brainstem-{mdgru/nnunet} .`

> [!NOTE]
> During building, multiple external sources need to be used, e.g., base images are downloaded from the NVIDIA NGC registry, scripts are download from this Github repository, and larger model files are downloaded from Zenodo. Make sure you can access all required external sources in your build environment.

## Licenses of redistributed software

Please note the license terms of software components that we redistribute within our container images:

- [nnU-Net](https://github.com/MIC-DKFZ/nnUNet?tab=Apache-2.0-1-ov-file)
- [MD-GRU](https://github.com/zubata88/mdgru?tab=LGPL-2.1-1-ov-file)