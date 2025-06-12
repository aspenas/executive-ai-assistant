"""Enhanced priority scoring system for email triage."""

import re
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from eaia.schemas import State


class EmailPriorityScorer:
    """Scores emails based on various priority indicators."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.vip_contacts = config.get("settings", {}).get("vip_contacts", [])
        self.urgent_keywords = [
            "urgent", "asap", "emergency", "critical", "immediate",
            "deadline", "time-sensitive", "priority", "rush"
        ]
        self.meeting_keywords = [
            "meeting", "call", "schedule", "calendar", "appointment",
            "zoom", "teams", "conference", "discussion"
        ]
        
    def score_email(self, email: Dict) -> Tuple[int, Dict[str, int]]:
        """
        Score an email's priority from 0-100.
        Returns (total_score, breakdown_dict)
        """
        breakdown = {}
        total_score = 0
        
        vip_score = self._score_vip_sender(email.get("from_email", ""))
        breakdown["vip_sender"] = vip_score
        total_score += vip_score
        
        subject_score = self._score_subject_urgency(email.get("subject", ""))
        breakdown["subject_urgency"] = subject_score
        total_score += subject_score
        
        content_score = self._score_content_urgency(email.get("page_content", ""))
        breakdown["content_urgency"] = content_score
        total_score += content_score
        
        time_score = self._score_time_sensitivity(email.get("page_content", ""))
        breakdown["time_sensitivity"] = time_score
        total_score += time_score
        
        meeting_score = self._score_meeting_request(email.get("page_content", ""))
        breakdown["meeting_request"] = meeting_score
        total_score += meeting_score
        
        action_score = self._score_action_required(email.get("page_content", ""))
        breakdown["action_required"] = action_score
        total_score += action_score
        
        thread_score = self._score_thread_length(email.get("page_content", ""))
        breakdown["thread_importance"] = thread_score
        total_score += thread_score
        
        return min(total_score, 100), breakdown
    
    def _score_vip_sender(self, from_email: str) -> int:
        """Score based on VIP sender status."""
        if from_email.lower() in [vip.lower() for vip in self.vip_contacts]:
            return 30
        return 0
    
    def _score_subject_urgency(self, subject: str) -> int:
        """Score based on urgent keywords in subject."""
        subject_lower = subject.lower()
        urgent_count = sum(1 for keyword in self.urgent_keywords if keyword in subject_lower)
        
        if "urgent" in subject_lower or "asap" in subject_lower:
            return 25
        elif urgent_count >= 2:
            return 20
        elif urgent_count == 1:
            return 10
        return 0
    
    def _score_content_urgency(self, content: str) -> int:
        """Score based on urgent language in content."""
        content_lower = content.lower()
        urgent_count = sum(1 for keyword in self.urgent_keywords if keyword in content_lower)
        
        if urgent_count >= 3:
            return 15
        elif urgent_count == 2:
            return 10
        elif urgent_count == 1:
            return 5
        return 0
    
    def _score_time_sensitivity(self, content: str) -> int:
        """Score based on time-sensitive language."""
        content_lower = content.lower()
        
        time_patterns = [
            r"by (?:today|tomorrow|end of (?:day|week))",
            r"within \d+ (?:hours?|days?)",
            r"deadline.*(?:today|tomorrow|this week)",
            r"need.*(?:today|tomorrow|asap|immediately)"
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, content_lower):
                return 15
        
        if any(phrase in content_lower for phrase in ["time sensitive", "deadline", "due date"]):
            return 10
            
        return 0
    
    def _score_meeting_request(self, content: str) -> int:
        """Score based on meeting/scheduling requests."""
        content_lower = content.lower()
        meeting_count = sum(1 for keyword in self.meeting_keywords if keyword in content_lower)
        
        scheduling_patterns = [
            r"when (?:are you|would you be) (?:available|free)",
            r"schedule.*(?:meeting|call|time)",
            r"let's (?:meet|schedule|set up)",
            r"available for.*(?:call|meeting|discussion)"
        ]
        
        has_scheduling = any(re.search(pattern, content_lower) for pattern in scheduling_patterns)
        
        if has_scheduling and meeting_count >= 2:
            return 15
        elif has_scheduling or meeting_count >= 3:
            return 10
        elif meeting_count >= 1:
            return 5
        return 0
    
    def _score_action_required(self, content: str) -> int:
        """Score based on direct questions and action items."""
        content_lower = content.lower()
        
        question_count = content.count("?")
        
        action_patterns = [
            r"can you (?:please )?(?:help|assist|provide|send|review)",
            r"could you (?:please )?(?:help|assist|provide|send|review)",
            r"would you (?:please )?(?:help|assist|provide|send|review)",
            r"please (?:help|assist|provide|send|review|confirm|let me know)",
            r"need you to",
            r"requesting.*(?:help|assistance|information)"
        ]
        
        action_requests = sum(1 for pattern in action_patterns if re.search(pattern, content_lower))
        
        score = 0
        if question_count >= 3:
            score += 10
        elif question_count >= 1:
            score += 5
            
        if action_requests >= 2:
            score += 10
        elif action_requests == 1:
            score += 5
            
        return score
    
    def _score_thread_length(self, content: str) -> int:
        """Score based on email thread length (more replies = potentially more important)."""
        from_count = content.lower().count("from:")
        
        if from_count >= 5:
            return 10
        elif from_count >= 3:
            return 5
        elif from_count >= 2:
            return 2
        return 0
    
    def get_priority_category(self, score: int) -> str:
        """Convert numeric score to priority category."""
        if score >= 70:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 30:
            return "medium"
        elif score >= 10:
            return "low"
        else:
            return "minimal"
