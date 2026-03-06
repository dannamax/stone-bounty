#!/usr/bin/env python3
"""
Fallback Handler for Reply Completeness Skill
Handles temporary fallback replies and async completion
"""

import json
import time
from typing import Dict, Any, Optional
from pathlib import Path

class FallbackHandler:
    """Handles fallback replies and async completion"""
    
    def __init__(self, workspace_dir: str = "/home/admin/.openclaw/workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.fallback_cache_dir = self.workspace_dir / "skills" / "reply-completeness" / "fallback_cache"
        self.fallback_cache_dir.mkdir(parents=True, exist_ok=True)
        
    def should_send_fallback(self, response: str, context: Dict[str, Any]) -> bool:
        """
        Determine if a fallback reply should be sent
        
        Args:
            response: The incomplete response from the model
            context: Context information including timeout status
            
        Returns:
            bool: True if fallback should be sent
        """
        # Check if response is empty or very short
        if not response or len(response.strip()) < 10:
            return True
            
        # Check if response ends abruptly (no proper ending)
        response_lower = response.lower().strip()
        if response_lower and not any(
            response_lower.endswith(ending) 
            for ending in ['.', '!', '?', '。', '！', '？', '"', "'", ')', '}', ']', '\n']
        ):
            # Check if it's a complete sentence despite no ending punctuation
            if not self._is_complete_sentence(response):
                return True
                
        # Check if context indicates timeout
        if context.get('timeout_occurred', False):
            return True
            
        return False
        
    def _is_complete_sentence(self, text: str) -> bool:
        """Check if text appears to be a complete sentence"""
        # Simple heuristic: check for common sentence patterns
        text = text.strip()
        if not text:
            return False
            
        # Check if it contains a verb-like pattern (very basic)
        verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'would', 
                'can', 'could', 'should', 'may', 'might', 'must', 'do', 'does', 'did']
        words = text.lower().split()
        if any(word in verbs for word in words):
            return True
            
        # Check for question patterns
        if text.endswith('?') or any(q in text.lower() for q in ['what', 'how', 'why', 'when', 'where', 'who']):
            return True
            
        # If it's longer than 20 characters, assume it might be complete
        if len(text) > 20:
            return True
            
        return False
        
    def generate_fallback_reply(self, original_query: str, incomplete_response: str = "") -> str:
        """
        Generate a temporary fallback reply
        
        Args:
            original_query: The user's original query
            incomplete_response: The incomplete response (if any)
            
        Returns:
            str: Fallback reply message
        """
        if incomplete_response:
            # If we have partial response, acknowledge it and promise completion
            return (
                f"{incomplete_response}\n\n"
                f"⏳ **正在补充完整答案，请稍等...**\n"
                f"您的问题已收到，我正在完善详细回复。"
            )
        else:
            # No partial response, just acknowledge receipt
            return (
                "⏳ **正在处理您的请求...**\n"
                "您的问题比较复杂，我需要一点时间来提供完整准确的答案。\n"
                "请稍等片刻，完整回复即将发送。"
            )
            
    def cache_incomplete_response(self, session_id: str, context: Dict[str, Any]) -> str:
        """
        Cache incomplete response for async completion
        
        Args:
            session_id: Session identifier
            context: Full context including query and partial response
            
        Returns:
            str: Cache file path
        """
        cache_file = self.fallback_cache_dir / f"{session_id}_{int(time.time())}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(context, f, ensure_ascii=False, indent=2)
        return str(cache_file)
        
    def load_cached_context(self, cache_file: str) -> Optional[Dict[str, Any]]:
        """
        Load cached context for async completion
        
        Args:
            cache_file: Path to cache file
            
        Returns:
            Optional[Dict]: Cached context or None if not found
        """
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
            
    def cleanup_old_cache(self, max_age_hours: int = 24):
        """
        Clean up old cache files
        
        Args:
            max_age_hours: Maximum age of cache files in hours
        """
        import os
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for cache_file in self.fallback_cache_dir.glob("*.json"):
            file_time = datetime.fromtimestamp(os.path.getctime(cache_file))
            if file_time < cutoff_time:
                cache_file.unlink()
                
    def get_async_completion_prompt(self, cached_context: Dict[str, Any]) -> str:
        """
        Generate prompt for async completion
        
        Args:
            cached_context: Cached context from incomplete response
            
        Returns:
            str: Prompt for completing the response
        """
        original_query = cached_context.get('original_query', '')
        partial_response = cached_context.get('partial_response', '')
        conversation_history = cached_context.get('conversation_history', [])
        
        if partial_response:
            return (
                f"继续完成以下回答，确保回答完整且准确：\n\n"
                f"用户问题：{original_query}\n\n"
                f"已有回答：{partial_response}\n\n"
                f"请接着上面的内容继续，不要重复已有的内容，直接完成剩余部分。"
            )
        else:
            return (
                f"请完整回答以下问题：\n\n"
                f"{original_query}\n\n"
                f"要求：回答要详细、准确、完整，包含所有必要的信息。"
            )

# Example usage
if __name__ == "__main__":
    handler = FallbackHandler()
    
    # Test fallback detection
    test_cases = [
        ("", {"timeout_occurred": True}),
        ("This is a complete sentence.", {}),
        ("This is incomplete", {}),
        ("How do I fix this error?", {}),
        ("The solution involves multiple steps:", {}),
    ]
    
    for response, context in test_cases:
        should_fallback = handler.should_send_fallback(response, context)
        fallback_msg = handler.generate_fallback_reply("test query", response)
        print(f"Response: '{response}'")
        print(f"Should fallback: {should_fallback}")
        print(f"Fallback message: {fallback_msg[:100]}...")
        print("-" * 50)