#!/usr/bin/env python3
"""
Content Validator for Reply Completeness Skill
Validates the completeness and quality of generated responses
"""

import re
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Validation result structure"""
    is_complete: bool
    completeness_score: float
    issues: List[str]
    suggestions: List[str]

class ContentValidator:
    """Validates response completeness and quality"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.timeout_threshold = self.config.get("timeout_threshold_seconds", 15)
        self.enable_completeness_check = self.config.get("enable_completeness_check", True)
        
        # Validation patterns
        self.sentence_endings = r'[.!?。！？]$'
        self.incomplete_patterns = [
            r'\.\.\.$',  # trailing ellipsis
            r'[\w\s]+,$',  # ending with comma
            r'^\s*$',  # empty or whitespace only
            r'in progress',  # incomplete indicators
            r'to be continued',  # incomplete indicators
        ]
        
        # Question-answer validation
        self.question_indicators = ['?', '？', 'what', 'how', 'why', 'when', 'where', 'who']
        self.answer_indicators = ['answer', 'response', 'solution', 'result', 'conclusion']
    
    def validate_response(self, response: str, original_query: str = "", 
                         generation_time: float = 0.0) -> ValidationResult:
        """
        Validate response completeness
        
        Args:
            response: Generated response text
            original_query: Original user query
            generation_time: Time taken to generate response
            
        Returns:
            ValidationResult with completeness assessment
        """
        if not response or not response.strip():
            return ValidationResult(
                is_complete=False,
                completeness_score=0.0,
                issues=["Empty response"],
                suggestions=["Regenerate response with proper content"]
            )
        
        issues = []
        suggestions = []
        completeness_score = 1.0
        
        # Check for timeout issues
        if generation_time > self.timeout_threshold:
            issues.append(f"Generation time ({generation_time:.1f}s) exceeds threshold ({self.timeout_threshold}s)")
            completeness_score *= 0.7
            suggestions.append("Consider increasing timeout threshold or optimizing response")
        
        # Check sentence completeness
        sentence_complete = self._check_sentence_completeness(response)
        if not sentence_complete:
            issues.append("Response doesn't end with proper sentence ending")
            completeness_score *= 0.8
            suggestions.append("Ensure response ends with proper punctuation (.!?)")
        
        # Check for incomplete patterns
        incomplete_patterns = self._check_incomplete_patterns(response)
        if incomplete_patterns:
            issues.extend(incomplete_patterns)
            completeness_score *= 0.6
            suggestions.append("Remove incomplete indicators like trailing ellipsis")
        
        # Check question-answer completeness (if original query was a question)
        if original_query and self._is_question(original_query):
            answer_complete = self._check_answer_completeness(response, original_query)
            if not answer_complete:
                issues.append("Question not fully answered")
                completeness_score *= 0.7
                suggestions.append("Ensure all aspects of the question are addressed")
        
        # Check minimum length
        min_length = self.config.get("min_response_length", 10)
        if len(response.strip()) < min_length:
            issues.append(f"Response too short ({len(response)} chars, min {min_length})")
            completeness_score *= 0.5
            suggestions.append(f"Increase response length to at least {min_length} characters")
        
        # Final completeness determination
        is_complete = completeness_score >= 0.8 and len(issues) == 0
        
        return ValidationResult(
            is_complete=is_complete,
            completeness_score=completeness_score,
            issues=issues,
            suggestions=suggestions
        )
    
    def _check_sentence_completeness(self, response: str) -> bool:
        """Check if response ends with proper sentence ending"""
        response = response.strip()
        if not response:
            return False
        
        # Check if ends with sentence ending punctuation
        return bool(re.search(self.sentence_endings, response))
    
    def _check_incomplete_patterns(self, response: str) -> List[str]:
        """Check for patterns indicating incomplete response"""
        issues = []
        response_lower = response.lower()
        
        for pattern in self.incomplete_patterns:
            if re.search(pattern, response_lower):
                issues.append(f"Found incomplete pattern: {pattern}")
        
        return issues
    
    def _is_question(self, query: str) -> bool:
        """Check if query is a question"""
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in self.question_indicators)
    
    def _check_answer_completeness(self, response: str, query: str) -> bool:
        """Check if question has been adequately answered"""
        response_lower = response.lower()
        query_lower = query.lower()
        
        # Basic check: response should be longer than query
        if len(response) <= len(query):
            return False
        
        # Check for answer indicators
        has_answer_indicators = any(indicator in response_lower for indicator in self.answer_indicators)
        
        # If it's a specific question, response should contain relevant content
        if "how" in query_lower or "what" in query_lower:
            return len(response.split()) >= 10 or has_answer_indicators
        
        return True
    
    def get_validation_config(self) -> Dict[str, Any]:
        """Get current validation configuration"""
        return {
            "timeout_threshold_seconds": self.timeout_threshold,
            "enable_completeness_check": self.enable_completeness_check,
            "sentence_endings_pattern": self.sentence_endings,
            "min_response_length": self.config.get("min_response_length", 10)
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the validator
    validator = ContentValidator({
        "timeout_threshold_seconds": 15,
        "min_response_length": 20
    })
    
    # Test cases
    test_cases = [
        ("This is a complete sentence.", "Simple complete response", 2.0),
        ("This is incomplete", "Incomplete response", 1.5),
        ("Answer to your question...", "Trailing ellipsis", 3.0),
        ("", "Empty response", 1.0),
        ("How do I implement this feature? This is a detailed explanation of the implementation process with multiple steps and examples.", "Question with detailed answer", 5.0)
    ]
    
    for response, description, time_taken in test_cases:
        result = validator.validate_response(response, "How do I do this?", time_taken)
        print(f"\n{description}:")
        print(f"  Complete: {result.is_complete}")
        print(f"  Score: {result.completeness_score:.2f}")
        print(f"  Issues: {result.issues}")