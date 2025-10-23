
"""
AI聊天API端点
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import asyncio
import random

from app.api.deps import get_db, get_current_doctor
from app.models.doctor import Doctor
from app.service.ai_chat_service import ai_chat_service
from app.service.clinical_tools import ClinicalToolManager
from app.schemas.chat import (
    ChatCompletionRequest, ChatCompletionResponse,
)


from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/colposcopy", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """
    接受传入的文件，基于算法流程进行报告解读;
    """
    try:
        # 日志记录患者上下文信息
        if request.patient_id:
            logger.info(f"聊天请求包含患者上下文 - 患者ID: {request.patient_id}, 启用上下文: {request.include_patient_context}")
        else:
            logger.info(f"聊天请求不包含患者上下文")
        
        # 如果是流式请求，返回流式响应
        logger.info(f"流式请求: {request}")
        if request.stream:
            async def generate():
                async for event in ai_chat_service.chat_completion_stream(db, request):
                    # 直接输出OpenAI标准chunk格式，不包装在ChatStreamEvent中
                    if event.type == "message" and event.data:
                        yield f"data: {json.dumps(event.data)}\n\n"
                    elif event.type == "done":
                        yield "data: [DONE]\n\n"
                        break
            
            return StreamingResponse(
                generate(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache", 
                    "Connection": "keep-alive",
                    "Content-Type": "text/plain; charset=utf-8"
                }
            )
        
        # 常规完成
        response = await ai_chat_service.chat_completion(db, request)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.post("/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    db: Session = Depends(get_db),
):
    """
    聊天完成接口 - 兼容OpenAI格式
    """
    try:
        # 日志记录患者上下文信息
        if request.patient_id:
            logger.info(f"聊天请求包含患者上下文 - 患者ID: {request.patient_id}, 启用上下文: {request.include_patient_context}")
        else:
            logger.info(f"聊天请求不包含患者上下文")
        
        # 如果是流式请求，返回流式响应
        logger.info(f"流式请求: {request}")
        if request.stream:
            async def generate():
                async for event in ai_chat_service.chat_completion_stream(db, request):
                    # 直接输出OpenAI标准chunk格式，不包装在ChatStreamEvent中
                    if event.type == "message" and event.data:
                        yield f"data: {json.dumps(event.data)}\n\n"
                    elif event.type == "done":
                        yield "data: [DONE]\n\n"
                        break
            
            return StreamingResponse(
                generate(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache", 
                    "Connection": "keep-alive",
                    "Content-Type": "text/plain; charset=utf-8"
                }
            )
        
        # 常规完成
        response = await ai_chat_service.chat_completion(db, request)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))