# -*- coding: utf-8 -*-
"""
API routes for Entertwine Chatbot
"""

import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .chat_service import QueryRequest, process_query
from botbuilder.schema import Activity
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from .config import ChatbotConfig

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Teams bot adapter (optional)
app_id = ChatbotConfig.get_teams_app_id()
app_password = ChatbotConfig.get_teams_app_password()
tenant_id = ChatbotConfig.get_teams_tenant_id()

if app_id and app_password:
    logger.info("Initializing Teams bot adapter")
    adapter_settings = BotFrameworkAdapterSettings(app_id, app_password, tenant_id)
else:
    logger.info("Teams bot credentials not configured, allowing emulator mode")
    adapter_settings = BotFrameworkAdapterSettings(None, None)

adapter = BotFrameworkAdapter(adapter_settings)
adapter.use_websocket = True
adapter.settings.trust_service_url = "https://webchat.botframework.com/"


class HealthResponse(BaseModel):
    status: str
    message: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="ok", message="Entertwine Chatbot API is running")


@router.post("/query")
async def query_endpoint(request: QueryRequest):
    """
    Process a chat query.
    
    Args:
        request: QueryRequest with session_id and query text
        
    Returns:
        Response text
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        response = await process_query(request)
        return JSONResponse({"response": response})
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/api/messages")
async def teams_messages(req: Request):
    """
    Handle incoming Microsoft Teams messages.
    
    Args:
        req: FastAPI Request object
        
    Returns:
        Response for Teams bot framework
    """
    try:
        body = await req.json()
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        
        logger.debug(f"Received Teams activity: {activity.type}")
        
        async def turn_handler(turn_context: TurnContext):
            user_text = activity.text or ""
            user_id = activity.from_property.id if activity.from_property else "unknown_user"
            
            if not user_text:
                logger.debug("No text in activity")
                return
            
            if "test" in user_text.lower():
                logger.debug("Test message received")
                await turn_context.send_activity("Test successful! I see your message.")
                return
            
            try:
                query_request = QueryRequest(session_id=user_id, query=user_text)
                response = await process_query(query_request)
                await turn_context.send_activity(str(response))
            except Exception as e:
                logger.error(f"Error processing Teams message: {e}")
                await turn_context.send_activity("Sorry, I encountered an error processing your message.")
        
        return await adapter.process_activity(activity, auth_header, turn_handler)
        
    except Exception as e:
        logger.error(f"Error in Teams message handler: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
