
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from .model import ExpectedPowerModel
from .schemas import Prediction, Reading

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["model"] = ExpectedPowerModel()   # load once at startup
    yield
    state.clear()


app = FastAPI(title="TAYF Expected Power API", version="1.0.0",
              description="Normalized AC expected power for PVDAQ System 10 (NREL CIS-1), ML-A model (POA, module temp, ambient temp, time).",
              lifespan=lifespan)


def _run(readings: list[Reading]) -> list[Prediction]:
    m: ExpectedPowerModel = state["model"]
    preds = m.predict(
        [r.timestamp for r in readings],
        [r.poa_irradiance for r in readings],
        [r.module_temp for r in readings],
        [r.ambient_temp for r in readings],
    )
    return [Prediction(**p) for p in preds]


@app.get("/")
def health():
    m = state.get("model")
    if m is None:
        raise HTTPException(503, "model not loaded")
    return {"status": "ok", "features": m.features, "timezone": m.tz}


@app.post("/predict", response_model=Prediction)
def predict(reading: Reading):
    return _run([reading])[0]

