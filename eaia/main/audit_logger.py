"""Audit logging system for executive assistant actions."""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class AuditLogger:
    """Centralized audit logging for all EA actions."""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or "eaia_audit.log"
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up dedicated audit logger."""
        logger = logging.getLogger("eaia_audit")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter(
                '%(asctime)s - AUDIT - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def log_email_received(self, email_data: Dict[str, Any]):
        """Log when an email is received and processed."""
        audit_data = {
            "action": "email_received",
            "email_id": email_data.get("id"),
            "from_email": email_data.get("from_email"),
            "subject": email_data.get("subject"),
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(json.dumps(audit_data))
    
    def log_triage_decision(self, email_id: str, decision: str, priority_score: int):
        """Log triage decisions."""
        audit_data = {
            "action": "triage_decision",
            "email_id": email_id,
            "decision": decision,
            "priority_score": priority_score,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(json.dumps(audit_data))
    
    def log_email_drafted(self, email_id: str, draft_type: str, recipient_count: int):
        """Log when an email draft is created."""
        audit_data = {
            "action": "email_drafted",
            "email_id": email_id,
            "draft_type": draft_type,
            "recipient_count": recipient_count,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(json.dumps(audit_data))
    
    def log_email_sent(self, email_id: str, recipients: list, subject: str):
        """Log when an email is actually sent."""
        audit_data = {
            "action": "email_sent",
            "original_email_id": email_id,
            "recipients": recipients,
            "subject": subject,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(json.dumps(audit_data))
    
    def log_calendar_invite_sent(self, email_id: str, attendees: list, meeting_title: str):
        """Log calendar invitations."""
        audit_data = {
            "action": "calendar_invite_sent",
            "email_id": email_id,
            "attendees": attendees,
            "meeting_title": meeting_title,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(json.dumps(audit_data))
    
    def log_human_intervention(self, email_id: str, intervention_type: str, reason: str):
        """Log when human intervention is required."""
        audit_data = {
            "action": "human_intervention",
            "email_id": email_id,
            "intervention_type": intervention_type,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(json.dumps(audit_data))
    
    def log_error(self, email_id: str, error_type: str, error_message: str):
        """Log errors for debugging and compliance."""
        audit_data = {
            "action": "error",
            "email_id": email_id,
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.error(json.dumps(audit_data))
    
    def get_audit_summary(self, days: int = 7) -> Dict[str, Any]:
        """Generate audit summary for the last N days."""
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
            
            summary = {
                "emails_processed": 0,
                "emails_sent": 0,
                "triage_decisions": {"no": 0, "email": 0, "notify": 0},
                "errors": 0,
                "human_interventions": 0,
                "calendar_invites": 0
            }
            
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for line in lines:
                try:
                    if " - AUDIT - " in line:
                        json_part = line.split(" - AUDIT - ", 1)[1]
                        data = json.loads(json_part)
                        
                        log_time = datetime.fromisoformat(data.get("timestamp", "")).timestamp()
                        if log_time < cutoff_date:
                            continue
                        
                        action = data.get("action")
                        if action == "email_received":
                            summary["emails_processed"] += 1
                        elif action == "email_sent":
                            summary["emails_sent"] += 1
                        elif action == "triage_decision":
                            decision = data.get("decision", "unknown")
                            if decision in summary["triage_decisions"]:
                                summary["triage_decisions"][decision] += 1
                        elif action == "error":
                            summary["errors"] += 1
                        elif action == "human_intervention":
                            summary["human_interventions"] += 1
                        elif action == "calendar_invite_sent":
                            summary["calendar_invites"] += 1
                            
                except (json.JSONDecodeError, ValueError):
                    continue
            
            return summary
            
        except FileNotFoundError:
            return {"error": "Audit log file not found"}


audit_logger = AuditLogger()
