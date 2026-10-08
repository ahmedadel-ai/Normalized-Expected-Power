# TAYF Expected Power API (FastAPI)

Predicts the normalized AC expected power (AC power / rated capacity, about 0..1) for PVDAQ System 10 (NREL CIS-1, Golden CO).

## Run
1. `artifacts/` must contain `model_a.json` + `config.json` (saved by the notebook).
2. `pip install -r requirements.txt`  (xgboost is pinned to the training version)
3. `uvicorn app.main:app --reload`  -> docs at http://127.0.0.1:8000/docs
4. Docker: `docker build -t pv-api . && docker run -p 8000:8000 pv-api`
5. Tests: `pytest`

## Endpoints
- `GET /` health check (model loaded, features, timezone)
- `POST /predict`

Request:
```json
{"timestamp": "10/11/2010 9:18:00 AM", "poa_irradiance": 800, "module_temp": 35, "ambient_temp": 15}
```
Response:
```json
{"timestamp": "2010-10-11T09:18:00-06:00", "expected_power_norm": 0.585, "daytime": true}
```

## Notes
- `timestamp`: ISO 8601 or text like `10/11/2010 9:18:00 AM` (slash dates are MONTH-first).
  No timezone = site local time (America/Denver). With `Z` or an offset = that timezone.
- `poa_irradiance` in W/m2 (small negative night values are clipped to 0), temperatures in °C.
- `daytime` = POA >= 50 W/m2. When false, `expected_power_norm` is 0 (the model was trained on daytime data only).
- To get watts: `expected_power_norm * 1120` (AC rating of System 10).
