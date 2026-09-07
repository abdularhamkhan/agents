import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import uvicorn

from gemini_client import GeminiClient

# 1. Setup Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gemini_api")


# 2. Application Lifespan (Resource Management)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize external client
    logger.info("Initializing Gemini Client...")
    app.state.gemini_client = GeminiClient()
    yield
    # Shutdown: Clean up resources
    logger.info("Shutting down Gemini Client...")


app = FastAPI(
    title="Gemini AI Chat Service",
    version="1.0.0",
    lifespan=lifespan,
)

# 3. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 4. Dependency Injection for Gemini Client
def get_gemini_client() -> GeminiClient:
    return app.state.gemini_client


# 5. Strict Pydantic v2 Schemas
class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        max_length=4000,
        description="The user query or prompt for the AI.",
        json_schema_extra={"example": "Explain quantum computing in simple terms."},
    )

    @field_validator("message")
    @classmethod
    def validate_and_strip_message(cls, value: str) -> str:
        """Strips whitespace and ensures the message isn't blank."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Message cannot be empty or contain only whitespace.")
        return cleaned


class ChatResponse(BaseModel):
    response: str = Field(..., description="The generated AI text response.")


# 6. API Route Handlers
@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI Response",
    tags=["Chat"],
)
@app.post(
    "/api/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,  # Route alias for compatibility
)
async def chat(
    request_data: ChatRequest,
    client: Annotated[GeminiClient, Depends(get_gemini_client)],
):
    """
    Accepts a user message and returns an AI-generated response from Gemini.
    """
    try:
        # Offload synchronous Gemini/DuckDuckGo API calls to a threadpool
        response_text = await run_in_threadpool(
            client.generate_response, request_data.message
        )

        return ChatResponse(response=response_text)

    except Exception as exc:
        logger.error(f"Gemini API execution failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the response. Please try again later.",
        )


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    # Fix: Changed "main:app" -> "app:app" to match filename app.py
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)






















# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from gemini_client import GeminiClient
# import uvicorn

# app = FastAPI()
# client = GeminiClient()


# @app.post('/api/chat')
# async def chat(request: Request):
# 	payload = await request.json()
# 	user_message = (
# 		payload.get('message', '').strip()
# 		if isinstance(payload, dict)
# 		else ''
# 	)
# 	if not user_message:
# 		return JSONResponse({'error': 'No message provided'}, status_code=400)

# 	try:
# 		response_text = client.generate_response(user_message)
# 		return {'response': response_text}
# 	except Exception:
# 		return JSONResponse({'error': 'Error generating response'}, status_code=500)


# if __name__ == '__main__':
# 	uvicorn.run(app, host='127.0.0.1', port=8000)