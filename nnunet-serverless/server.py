from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
import shutil
import os
import uuid
import subprocess

app = FastAPI()

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    # Save uploaded file
    input_id = str(uuid.uuid4())
    input_path = f"/tmp/{input_id}.nii.gz"
    output_path = f"/tmp/{input_id}_brainstem.nii.gz"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run inference
    cmd = [
        "python", "/opt/scripts/pipeline_nnunet.py",
        input_path,
        "-o", output_path,
        "-x"  # allow overwrite
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        return {"error": result.stderr.decode()}

    # Return output file
    return FileResponse(output_path, media_type="application/gzip", filename="brainstem.nii.gz")