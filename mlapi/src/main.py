import logging
import os
from pydantic import BaseModel, Extra, validator
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from fastapi_cache.coder import PickleCoder
from redis import Redis
from redis import asyncio as aioredis
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

#Not using huggingface load
#model_path = "winegarj/distilbert-base-uncased-finetuned-sst2"


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(parent_dir, "model")

model = AutoModelForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)
classifier = pipeline(
    task="text-classification",
    model=model,
    tokenizer=tokenizer,
    device=-1,
    return_all_scores=True,
)

logger = logging.getLogger(__name__)
LOCAL_REDIS_URL = "redis://redis:6379"
app = FastAPI()


@app.on_event("startup")
def startup():
    try: 
        logger_startup = logging.getLogger("startup")
        logger_startup.debug("Attempting to connect to Redis...")
        redis = aioredis.from_url(LOCAL_REDIS_URL)

        #redis = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
        logger_startup.debug("Redis connection successful!")
    except Exception as e:
        logger_startup.error("Redis connection failed!")
        raise 
    #redis = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


# for debugging purposes
"""@app.get("/connect")
async def test_redis_connection():
    try:
        redis = await aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
        result = await redis.ping()
        redis.close()
        #await redis.wait_closed()
        return {"message": "Connected to Redis", "result": result}
    except Exception as e:
        return {"error": f"Failed to connect to Redis: {e}"}

"""

class SentimentRequest(BaseModel):
    text: list[str]


class Sentiment(BaseModel):
    label: str
    score: float

class SentimentResponse(BaseModel):
    predictions: list[list[Sentiment]]


@app.post("/predict", response_model=SentimentResponse)
@cache(expire=60)
async def predict(sentiments: SentimentRequest):
    return {"predictions": classifier(sentiments.text)}


@app.get("/health")
async def health():
    return {"status": "healthy"}
