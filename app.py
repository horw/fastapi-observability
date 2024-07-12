import asyncio
import json
import logging
import os
import time
from datetime import datetime

from fastapi import Request
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs._internal.export import ConsoleLogExporter
from opentelemetry.sdk.trace import TracerProvider, Span, SpanContext
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi import FastAPI
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from starlette.types import Scope, Receive, Send
from fastapi import FastAPI, BackgroundTasks
from opentelemetry.propagate import inject
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

app = FastAPI()
resource = Resource.create(
    {
        "service.name": "my_app",
    }
)
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer("hello fastapi")
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
otlp_tracer = trace.get_tracer_provider().add_span_processor(span_processor)


logger_provider = LoggerProvider(
    resource=Resource.create(
        {
            "service.name": "train-the-telemetfuchry",
            "service.instance.id": os.uname().nodename,
        }
    ),
)
set_logger_provider(logger_provider)
otlp_log_exporter = OTLPLogExporter(endpoint="http://localhost:4317")
logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))
# console_exporter = ConsoleLogExporter()
# logger_provider.add_log_record_processor(BatchLogRecordProcessor(console_exporter))
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logger = logging.getLogger()


LoggingInstrumentor().instrument(set_logging_format=True)

@tracer.start_as_current_span("should_error_func")
async def should_error_func(arg):
    logger.warning("SHOULD ERROR!!!!!")
    return 1


@app.middleware("http")
async def he2llo(request: Request, call_next):
    span = trace.get_current_span()
    span.set_attribute("this", "other")
    resp = await call_next(request)
    span.set_attribute("lol", "wft")
    trace.get_current_span().set_attribute("igor", "name")

    return resp


@app.middleware("http")
async def he2123llo(request: Request, call_next):
    span = trace.get_current_span()
    span.set_attribute("this", "other")
    resp = await call_next(request)
    return resp


@app.middleware("http")
async def he2112323llo(request: Request, call_next):
    span = trace.get_current_span()
    span.set_attribute("this", "other")
    resp = await call_next(request)
    return resp


FastAPIInstrumentor.instrument_app(
    app,
    tracer_provider=otlp_tracer,

)


@app.get("/")
async def index():
    logger.warning("hello")
    return {"foo": "bar"}


@app.post("/some")
async def ii(l: dict, bacground_task: BackgroundTasks):
    logger.warning("allala")
    lala = {}
    inject(lala)
    print("IMG ", lala)
    bacground_task.add_task(should_error_func, 1)
    with tracer.start_span("lol") as span:
        span.set_attribute("1", "123")
    with tracer.start_as_current_span("span-name") as span:
        span.set_attribute("dict", json.dumps(l))

    return {"foo": "bar"}