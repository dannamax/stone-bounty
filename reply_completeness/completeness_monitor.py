#!/usr/bin/env python3
"""
Reply Completeness Monitor - Core monitoring module for OpenClaw
Monitors response generation and ensures complete replies are delivered.
"""

import time
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class ReplyContext:
    """Context for reply generation monitoring"""
    session_id: str
    user_message: str
    start_time: float
    timeout_threshold: float = 15.0  # seconds
    generated_content: str = ""
    is_complete: bool = False
    retry_count: int = 0
    max_retries: int = 3

class CompletenessMonitor:
    """Monitors reply generation and handles timeouts/interruptions"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.timeout_threshold = self.config.get("timeout_threshold_seconds", 15)
        self.max_retries = self.config.get("max_retry_attempts", 3)
        self.active_monitors: Dict[str, ReplyContext] = {}
    
    async def start_monitoring(self, session_id: str, user_message: str) -> ReplyContext:
        """Start monitoring a reply generation process"""
        context = ReplyContext(
            session_id=session_id,
            user_message=user_message,
            start_time=time.time(),
            timeout_threshold=self.timeout_threshold,
            max_retries=self.max_retries
        )
        self.active_monitors[session_id] = context
        return context
    
    async def update_content(self, session_id: str, content: str):
        """Update the generated content for a session"""
        if session_id in self.active_monitors:
            self.active_monitors[session_id].generated_content = content
    
    async def mark_complete(self, session_id: str):
        """Mark a reply as complete"""
        if session_id in self.active_monitors:
            self.active_monitors[session_id].is_complete = True
    
    async def check_timeout(self, session_id: str) -> bool:
        """Check if a session has timed out"""
        if session_id not in self.active_monitors:
            return False
        
        context = self.active_monitors[session_id]
        elapsed = time.time() - context.start_time
        return elapsed > context.timeout_threshold
    
    async def should_retry(self, session_id: str) -> bool:
        """Check if a session should be retried"""
        if session_id not in self.active_monitors:
            return False
        
        context = self.active_monitors[session_id]
        return context.retry_count < context.max_retries
    
    async def increment_retry(self, session_id: str):
        """Increment retry count for a session"""
        if session_id in self.active_monitors:
            self.active_monitors[session_id].retry_count += 1
    
    async def get_fallback_reply(self, session_id: str) -> str:
        """Get fallback reply for a timed out session"""
        if session_id not in self.active_monitors:
            return "正在处理您的请求，请稍等..."
        
        context = self.active_monitors[session_id]
        if context.generated_content:
            # If we have partial content, return it with continuation notice
            return f"{context.generated_content}\n\n🔄 正在补充完整答案，请稍等..."
        else:
            return "🔄 正在生成完整回复，请稍等..."
    
    async def cleanup_session(self, session_id: str):
        """Clean up monitoring context for a session"""
        if session_id in self.active_monitors:
            del self.active_monitors[session_id]
