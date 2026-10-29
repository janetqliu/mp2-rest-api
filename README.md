# MP2: Data Processing REST API

This project is a FastAPI application that exposes the MP1 data-cleaning pipeline over HTTP. Clients upload a CSV with `POST /upload`, which stores the data in memory and returns its metadata (ID, filename, row and column counts, column names). `GET /datasets/{dataset_id}` returns up to `limit` stored rows along with the dataset's total row count. `POST /datasets/{dataset_id}/process` accepts a JSON configuration that validates required and numeric columns, then applies duplicate removal, missing-value handling, and optional outlier removal. It returns a cleaning report and replaces the stored dataset only after validation and processing both succeed. Request-logging middleware attaches an eight-character `X-Request-ID` header to every response and logs each request's method, path, status code, and duration, and a pytests cover the main workflows and error cases. `GET /health` reports the API's status and version.

## Running the API

```bash
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs to try the endpoints.