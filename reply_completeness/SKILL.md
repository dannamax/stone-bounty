# Reply Completeness Assurance Skill

## Overview
This skill ensures complete and reliable responses by monitoring generation timeouts, validating content completeness, and providing fallback mechanisms.

## Core Capabilities

### 1. Generation Timeout Monitoring
- Real-time monitoring of LLM/Agent response duration
- Configurable timeout threshold (default: 15 seconds)
- Automatic fallback trigger on timeout

### 2. Content Completeness Validation  
- Grammar/semantic completeness checking
- Sentence ending validation (periods, conclusions)
- Question-answer completeness verification

### 3. Fallback Response Handling
- Immediate temporary response on interruption
- Asynchronous completion with full answer delivery
- Seamless user experience maintenance

### 4. Context Management
- Intelligent context compression to prevent overflow
- Token usage optimization for long conversations
- State preservation for continuation requests

## Configuration
All settings are configurable via `reply_completeness_config.json`:

```json
{
  "timeout_threshold_seconds": 15,
  "enable_completeness_check": true,
  "enable_fallback_reply": true,
  "context_compression_enabled": true,
  "max_retry_attempts": 3,
  "fallback_message": "正在补充完整答案，请稍等..."
}
```

## Integration
This skill integrates with OpenClaw's existing session management and can be enabled globally or per-session.