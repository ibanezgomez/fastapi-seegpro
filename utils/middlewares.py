from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from utils.logger import log
from starlette.middleware.base import BaseHTTPMiddleware
from utils.config import config
from datetime import datetime
from http import HTTPStatus

class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = datetime.utcnow()
        response = await call_next(request)
        duration = datetime.utcnow() - start_time
        remote_addr = request.client.host
        http_protocol = f"{request.scope['scheme'].upper()}/{request.scope['http_version']}"
        request_line = f"{request.method} {request.url.path}"
        status = response.status_code
        status_text = HTTPStatus(response.status_code).phrase
        log_message = f"{http_protocol} {status} {status_text}"

        try: 
            client = remote_addr+'-'+request.state.client.id
        except: 
            client = remote_addr+'-unknown'
        log.info(log_message, action=request_line, client=client)
        return response