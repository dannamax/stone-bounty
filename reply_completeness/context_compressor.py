#!/usr/bin/env python3
"""
Context Compressor for Reply Completeness Skill
Automatically compresses conversation context to prevent token overflow
"""

import json
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class ContextCompressionConfig:
    """Configuration for context compression"""
    max_context_tokens: int = 4000
    compression_ratio: float = 0.8
    preserve_recent_messages: int = 3
    preserve_system_messages: bool = True
    preserve_tool_calls: bool = True

class ContextCompressor:
    """Compresses conversation context to fit within token limits"""
    
    def __init__(self, config: ContextCompressionConfig = None):
        self.config = config or ContextCompressionConfig()
        self.tokenizer = self._get_tokenizer()
    
    def _get_tokenizer(self):
        """Get tokenizer for token counting"""
        try:
            # Try to use tiktoken if available
            import tiktoken
            return tiktoken.get_encoding("cl100k_base")
        except ImportError:
            # Fallback to simple word-based tokenization
            return self._simple_tokenizer
    
    def _simple_tokenizer(self, text: str) -> List[str]:
        """Simple tokenizer as fallback"""
        if not text:
            return []
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
        return tokens
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if hasattr(self.tokenizer, 'encode'):
            return len(self.tokenizer.encode(text))
        else:
            return len(self.tokenizer(text))
    
    def compress_context(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compress conversation context to fit within token limits
        
        Args:
            messages: List of message dictionaries with 'role', 'content', etc.
            
        Returns:
            Compressed list of messages
        """
        if not messages:
            return messages
        
        # Calculate current token count
        current_tokens = self._count_context_tokens(messages)
        
        # If within limits, return as-is
        if current_tokens <= self.config.max_context_tokens:
            return messages
        
        # Preserve important messages
        preserved_messages = self._preserve_important_messages(messages)
        
        # Calculate remaining budget
        preserved_tokens = self._count_context_tokens(preserved_messages)
        remaining_budget = self.config.max_context_tokens - preserved_tokens
        
        if remaining_budget <= 0:
            # Even preserved messages exceed limit, return only most recent
            return preserved_messages[-self.config.preserve_recent_messages:]
        
        # Compress older messages
        compressed_messages = self._compress_older_messages(
            messages, preserved_messages, remaining_budget
        )
        
        return compressed_messages
    
    def _count_context_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """Count total tokens in message context"""
        total_tokens = 0
        for msg in messages:
            if isinstance(msg.get('content'), str):
                total_tokens += self.count_tokens(msg['content'])
            elif isinstance(msg.get('content'), list):
                # Handle multimodal content
                for item in msg['content']:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        total_tokens += self.count_tokens(item.get('text', ''))
        return total_tokens
    
    def _preserve_important_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Preserve system messages, tool calls, and recent messages"""
        preserved = []
        
        # Add system messages if configured
        if self.config.preserve_system_messages:
            system_msgs = [msg for msg in messages if msg.get('role') == 'system']
            preserved.extend(system_msgs)
        
        # Add tool call messages if configured
        if self.config.preserve_tool_calls:
            tool_msgs = [msg for msg in messages if msg.get('role') == 'tool']
            preserved.extend(tool_msgs)
        
        # Add most recent messages
        recent_msgs = messages[-self.config.preserve_recent_messages:]
        preserved.extend(recent_msgs)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_preserved = []
        for msg in preserved:
            msg_key = (msg.get('role'), str(msg.get('content'))[:100])
            if msg_key not in seen:
                seen.add(msg_key)
                unique_preserved.append(msg)
        
        return unique_preserved
    
    def _compress_older_messages(self, all_messages: List[Dict[str, Any]], 
                                preserved_messages: List[Dict[str, Any]], 
                                budget: int) -> List[Dict[str, Any]]:
        """Compress older messages to fit within budget"""
        # Get messages that are not preserved
        preserved_set = set(id(msg) for msg in preserved_messages)
        older_messages = [msg for msg in all_messages if id(msg) not in preserved_set]
        
        if not older_messages:
            return preserved_messages
        
        # Sort by recency (keep more recent older messages)
        older_messages.sort(key=lambda x: all_messages.index(x), reverse=True)
        
        # Add older messages until budget is exhausted
        result = preserved_messages.copy()
        current_tokens = self._count_context_tokens(result)
        
        for msg in older_messages:
            msg_tokens = self.count_tokens(str(msg.get('content', '')))
            if current_tokens + msg_tokens <= self.config.max_context_tokens:
                result.insert(0, msg)  # Insert at beginning to maintain order
                current_tokens += msg_tokens
            else:
                break
        
        return result
    
    def summarize_old_context(self, messages: List[Dict[str, Any]]) -> str:
        """
        Create a summary of old context to replace compressed messages
        
        Args:
            messages: Messages to summarize
            
        Returns:
            Summary string
        """
        if not messages:
            return ""
        
        # Extract key information from old messages
        user_questions = []
        assistant_responses = []
        
        for msg in messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                if isinstance(content, str):
                    user_questions.append(content)
            elif msg.get('role') == 'assistant':
                content = msg.get('content', '')
                if isinstance(content, str):
                    assistant_responses.append(content)
        
        summary_parts = []
        if user_questions:
            summary_parts.append(f"Previous user questions: {len(user_questions)} messages")
        if assistant_responses:
            summary_parts.append(f"Previous assistant responses: {len(assistant_responses)} messages")
        
        if summary_parts:
            return " ".join(summary_parts) + ". This is a summary of earlier conversation context."
        else:
            return "Earlier conversation context has been compressed to save space."

# Example usage and testing
if __name__ == "__main__":
    # Test the context compressor
    config = ContextCompressionConfig(
        max_context_tokens=100,
        compression_ratio=0.5,
        preserve_recent_messages=2
    )
    
    compressor = ContextCompressor(config)
    
    # Create test messages
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
        {"role": "assistant", "content": "The capital of France is Paris."},
        {"role": "user", "content": "What is the population of Paris?"},
        {"role": "assistant", "content": "Paris has a population of about 2.1 million people."},
        {"role": "user", "content": "Tell me about the Eiffel Tower."},
        {"role": "assistant", "content": "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris."}
    ]
    
    compressed = compressor.compress_context(test_messages)
    print(f"Original messages: {len(test_messages)}")
    print(f"Compressed messages: {len(compressed)}")
    print("Compressed messages:")
    for i, msg in enumerate(compressed):
        print(f"  {i}: {msg['role']}: {msg['content'][:50]}...")