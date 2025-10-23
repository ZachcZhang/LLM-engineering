"""
AI聊天相关的Pydantic schemas
"""
from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# OpenAI标准消息格式
class ChatMessage(BaseModel):
    role: Literal['system', 'user', 'assistant', 'function', 'tool'] = Field(..., description="消息角色")
    content: Optional[str] = Field(None, description="消息内容")
    name: Optional[str] = Field(None, description="消息发送者名称")
    function_call: Optional[Dict[str, Any]] = Field(None, description="函数调用信息")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="工具调用信息")
    tool_call_id: Optional[str] = Field(None, description="工具调用ID")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "请帮我分析这个患者的病情"
            }
        }


# 工具定义
class Tool(BaseModel):
    type: Literal['function'] = Field(default='function', description="工具类型")
    function: Dict[str, Any] = Field(..., description="函数定义")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "function",
                "function": {
                    "name": "medical_search",
                    "description": "搜索医学知识库",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "搜索查询"}
                        },
                        "required": ["query"]
                    }
                }
            }
        }
        
        
# Agent配置
class AgentConfig(BaseModel):
    agent_type: Literal['medical', 'general', 'specialist'] = Field(..., description="Agent类型")
    specialization: Optional[str] = Field(None, description="专业领域")
    personality: Optional[str] = Field(None, description="性格特征")
    guidelines: Optional[List[str]] = Field(None, description="指导原则")
    tools_enabled: Optional[List[str]] = Field(None, description="启用的工具")
    max_iterations: Optional[int] = Field(3, description="最大迭代次数")
    reasoning_mode: Optional[Literal['chain_of_thought', 'tree_of_thought', 'reflection']] = Field(
        'chain_of_thought', description="推理模式"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "medical",
                "specialization": "gastrointestinal_stromal_tumor",
                "personality": "professional, empathetic",
                "guidelines": ["基于循证医学", "强调专业诊断"],
                "tools_enabled": ["medical_search", "drug_interaction"],
                "max_iterations": 3,
                "reasoning_mode": "chain_of_thought"
            }
        }


# Agent配置
class AgentConfig(BaseModel):
    agent_type: Literal['medical', 'general', 'specialist'] = Field(..., description="Agent类型")
    specialization: Optional[str] = Field(None, description="专业领域")
    personality: Optional[str] = Field(None, description="性格特征")
    guidelines: Optional[List[str]] = Field(None, description="指导原则")
    tools_enabled: Optional[List[str]] = Field(None, description="启用的工具")
    max_iterations: Optional[int] = Field(3, description="最大迭代次数")
    reasoning_mode: Optional[Literal['chain_of_thought', 'tree_of_thought', 'reflection']] = Field(
        'chain_of_thought', description="推理模式"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "medical",
                "specialization": "gastrointestinal_stromal_tumor",
                "personality": "professional, empathetic",
                "guidelines": ["基于循证医学", "强调专业诊断"],
                "tools_enabled": ["medical_search", "drug_interaction"],
                "max_iterations": 3,
                "reasoning_mode": "chain_of_thought"
            }
        }


# 记忆配置
class MemoryConfig(BaseModel):
    memory_type: Literal['conversation', 'episodic', 'semantic', 'working'] = Field(..., description="记忆类型")
    retention_policy: Optional[Literal['session', 'persistent', 'temporary']] = Field(
        'session', description="保留策略"
    )
    max_memory_size: Optional[int] = Field(100, description="最大记忆数量")
    compression_enabled: Optional[bool] = Field(True, description="是否启用压缩")
    retrieval_strategy: Optional[Literal['recent', 'relevant', 'hybrid']] = Field(
        'hybrid', description="检索策略"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "memory_type": "conversation",
                "retention_policy": "session",
                "max_memory_size": 50,
                "compression_enabled": True,
                "retrieval_strategy": "hybrid"
            }
        }


# MCP配置
class MCPConfig(BaseModel):
    context_window_size: int = Field(4096, description="上下文窗口大小")
    context_compression: bool = Field(True, description="上下文压缩")
    relevance_threshold: float = Field(0.7, description="相关性阈值")
    context_sources: List[str] = Field(default_factory=list, description="上下文来源")
    dynamic_context: bool = Field(True, description="动态上下文")


# 聊天完成请求
class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="模型名称")
    messages: List[ChatMessage] = Field(..., description="消息列表")
    max_tokens: Optional[int] = Field(1000, description="最大token数")
    temperature: Optional[float] = Field(0.7, description="温度参数")
    top_p: Optional[float] = Field(1.0, description="核采样参数")
    n: Optional[int] = Field(1, description="生成数量")
    stream: Optional[bool] = Field(False, description="是否流式输出")
    stop: Optional[Union[str, List[str]]] = Field(None, description="停止词")
    presence_penalty: Optional[float] = Field(0.0, description="存在惩罚")
    frequency_penalty: Optional[float] = Field(0.0, description="频率惩罚")
    logit_bias: Optional[Dict[str, float]] = Field(None, description="logit偏置")
    user: Optional[str] = Field(None, description="用户标识")
    tools: Optional[List[Tool]] = Field(None, description="可用工具")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(None, description="工具选择策略")
    # 扩展字段
    agent_config: Optional[AgentConfig] = Field(None, description="Agent配置")
    memory_config: Optional[MemoryConfig] = Field(None, description="记忆配置")
    mcp_config: Optional[MCPConfig] = Field(None, description="MCP配置")
    context_id: Optional[str] = Field(None, description="上下文ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    
    # 新增：患者上下文字段
    patient_id: Optional[int] = Field(None, description="患者ID，用于获取患者信息作为上下文")
    include_patient_context: Optional[bool] = Field(False, description="是否包含患者上下文信息")
    
    # 工具调用元数据
    metadata: Optional[Dict[str, Any]] = Field(None, description="工具调用元数据，如case_type等")

    class Config:
        json_schema_extra = {
            "example": {
                "model": "gpt-4",
                "messages": [
                    {"role": "user", "content": "请分析GIST的治疗方案"}
                ],
                "max_tokens": 1000,
                "temperature": 0.7,
                "session_id": "session_123"
            }
        }


# 聊天完成响应
class ChatCompletionResponse(BaseModel):
    id: str = Field(..., description="响应ID")
    object: Literal['chat.completion', 'chat.completion.chunk'] = Field(..., description="对象类型")
    created: int = Field(..., description="创建时间戳")
    model: str = Field(..., description="模型名称")
    choices: List[Dict[str, Any]] = Field(..., description="选择列表")
    usage: Optional[Dict[str, int]] = Field(None, description="使用统计")
    # 扩展字段
    agent_info: Optional[Dict[str, Any]] = Field(None, description="Agent信息")
    memory_info: Optional[Dict[str, Any]] = Field(None, description="记忆信息")
    tool_execution_info: Optional[Dict[str, Any]] = Field(None, description="工具执行信息")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677652288,
                "model": "gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "根据您的描述，GIST的治疗方案主要包括..."
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 100,
                    "total_tokens": 110
                }
            }
        }