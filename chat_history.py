"""
Chat History Datastore for 30 Days of Voice Agents - Day 10
Simple in-memory datastore for storing conversation history by session_id
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ChatMessage:
    """Represents a single message in the conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

class ChatHistoryStore:
    """In-memory datastore for chat history"""
    
    def __init__(self):
        self._sessions: Dict[str, List[ChatMessage]] = {}
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session"""
        if session_id not in self._sessions:
            return []
        return [msg.to_dict() for msg in self._sessions[session_id]]
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to the session history"""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        self._sessions[session_id].append(message)
    
    def get_session_messages(self, session_id: str) -> List[Dict]:
        """Get messages formatted for LLM API"""
        history = self.get_session_history(session_id)
        return [{"role": msg["role"], "content": msg["content"]} for msg in history]
    
    def clear_session(self, session_id: str) -> None:
        """Clear chat history for a session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def get_all_sessions(self) -> Dict[str, List[Dict]]:
        """Get all sessions (for debugging)"""
        return {
            session_id: [msg.to_dict() for msg in messages]
            for session_id, messages in self._sessions.items()
        }

# Global instance
chat_store = ChatHistoryStore()
