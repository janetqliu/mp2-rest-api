# main.py

import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import DatasetInfo, DatasetStorage, HealthResponse, setup_logging
from data_pipeline import create_cleaning_report, process_data, validate_dataframe

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return {"status": "ok", "version": "1.0.0"}


@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""

    filename = Path(file.filename)
    if filename.suffix.lower() != ".csv":
        logger.warning(f"File extension {filename.suffix} not accepted")
        raise HTTPException(status_code=400, detail="Must be CSV file")

    contents = await file.read()
    
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except (pd.errors.EmptyDataError,pd.errors.ParserError,UnicodeDecodeError) as error:
        logger.warning(f"Cannot read CSV: {error}")
        raise HTTPException(status_code=400, detail="Cannot read the uploaded CSV")

    dataset_id = storage.save(df, filename.name)
    logger.info(f"Saved dataset {dataset_id}: {filename.name}, {df.shape[0]} rows")

    return DatasetInfo(
        id=dataset_id,
        filename=filename.name,
        rows=df.shape[0],
        columns=df.shape[1],
        column_names=df.columns.tolist()
    )



@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""
    df = storage.get(dataset_id)
    if df is None:
        logger.warning(f"Dataset ID {dataset_id} not found")
        raise HTTPException(status_code=404, detail="Dataset not found")

    records = json.loads(df.head(limit).to_json(orient="records"))

    logger.info(f"Returned {len(records)} rows from dataset {dataset_id}") 
    
    return {"id": dataset_id,
            "data": records,
            "total_rows": len(df)}