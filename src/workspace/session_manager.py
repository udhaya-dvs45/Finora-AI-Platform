import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
"""
session_manager.py
------------------
JSON-based research session management for the Multi-Agent Financial Analysis System.

Responsibilities:
- Create named research sessions with unique IDs
- List / retrieve / delete sessions
- Track which documents have been added to each session

Session file format  (sessions/<session_id>.json):
{
    "session_id": "<uuid4>",
    "name": "Q4 Research",
    "created_at": "2024-01-01T12:00:00",
    "documents": [
        {
            "doc_id": "<company>_<year>",
            "company": "AMAZON",
            "year": "2023",
            "filename": "AMAZON_ANNUAL_2023.pdf",
            "processed_at": "2024-01-01T12:05:00"
        }
    ]
}
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional


class SessionManager:
    """
    Manages research sessions using simple JSON files stored in a local directory.

    Each session is stored as a single <session_id>.json file inside
    the `sessions_dir` folder.
    """

    def __init__(self, sessions_dir: str):
        """
        Parameters
        ----------
        sessions_dir : str
            Path to the folder where session JSON files are stored.
            Created automatically if it does not exist.
        """
        self.sessions_dir = sessions_dir
        os.makedirs(sessions_dir, exist_ok=True)
        print(f"[SessionManager] Sessions directory: '{sessions_dir}'")

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _session_path(self, session_id: str) -> str:
        return os.path.join(self.sessions_dir, f"{session_id}.json")

    def _load(self, session_id: str) -> Optional[Dict[str, Any]]:
        path = self._session_path(session_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, session: Dict[str, Any]) -> None:
        path = self._session_path(session["session_id"])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def create_session(self, name: str) -> Dict[str, Any]:
        """
        Create a new named research session.

        Parameters
        ----------
        name : str
            Human-readable session name (e.g. "FAANG 2023 Review").

        Returns
        -------
        The newly created session dict.
        """
        session: Dict[str, Any] = {
            "session_id": str(uuid.uuid4()),
            "name": name,
            "created_at": datetime.now().isoformat(),
            "documents": [],
        }
        self._save(session)
        print(f"[SessionManager] Created session '{name}' (ID: {session['session_id']})")
        return session

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        Return a list of all stored sessions sorted by creation date (newest first).
        """
        sessions = []
        for fname in os.listdir(self.sessions_dir):
            if fname.endswith(".json"):
                session_id = fname[:-5]
                session = self._load(session_id)
                if session:
                    sessions.append(session)

        # Sort newest first
        sessions.sort(key=lambda s: s.get("created_at", ""), reverse=True)
        return sessions

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single session by ID.

        Returns None if the session does not exist.
        """
        session = self._load(session_id)
        if session is None:
            print(f"[SessionManager] Session '{session_id}' not found.")
        return session

    def add_document_to_session(
        self,
        session_id: str,
        company: str,
        year: str,
        filename: str,
    ) -> bool:
        """
        Append a processed document record to an existing session.

        Parameters
        ----------
        session_id : str   -- Target session ID.
        company    : str   -- Company name (e.g. 'AMAZON').
        year       : str   -- Year string (e.g. '2023').
        filename   : str   -- Original PDF filename.

        Returns
        -------
        True on success, False if session not found.
        """
        session = self._load(session_id)
        if session is None:
            print(f"[SessionManager] Cannot add document -- session '{session_id}' not found.")
            return False

        doc_id = f"{company}_{year}"

        # Avoid duplicate entries
        existing_ids = [d["doc_id"] for d in session.get("documents", [])]
        if doc_id in existing_ids:
            print(f"[SessionManager] Document '{doc_id}' already in session.")
            return True

        doc_record = {
            "doc_id": doc_id,
            "company": company,
            "year": year,
            "filename": filename,
            "processed_at": datetime.now().isoformat(),
        }
        session.setdefault("documents", []).append(doc_record)
        self._save(session)
        print(f"[SessionManager] Added '{doc_id}' to session '{session['name']}'.")
        return True

    def remove_document_from_session(self, session_id: str, doc_id: str) -> bool:
        """Remove a document record from the session."""
        session = self._load(session_id)
        if session is None:
            return False

        before = len(session.get("documents", []))
        session["documents"] = [
            d for d in session.get("documents", []) if d["doc_id"] != doc_id
        ]
        if len(session["documents"]) < before:
            self._save(session)
            print(f"[SessionManager] Removed '{doc_id}' from session '{session['name']}'.")
            return True
        print(f"[SessionManager] Document '{doc_id}' not found in session.")
        return False

    def delete_session(self, session_id: str) -> bool:
        """
        Permanently delete a session file.

        Returns True on success, False if session not found.
        """
        path = self._session_path(session_id)
        if os.path.exists(path):
            os.remove(path)
            print(f"[SessionManager] Deleted session '{session_id}'.")
            return True
        print(f"[SessionManager] Session '{session_id}' not found -- nothing deleted.")
        return False

    def print_session_summary(self, session: Dict[str, Any]) -> None:
        """Pretty-print a session summary to stdout."""
        print("\n" + "=" * 60)
        print(f"  Session  : {session['name']}")
        print(f"  ID       : {session['session_id']}")
        print(f"  Created  : {session['created_at']}")
        docs = session.get("documents", [])
        print(f"  Documents: {len(docs)}")
        for doc in docs:
            print(f"    * {doc['doc_id']}  ({doc['filename']})  -- added {doc['processed_at']}")
        print("=" * 60 + "\n")
