import requests
from datetime import datetime


class FacebookClient:
    def __init__(self, token, page_id):
        self.token = token
        self.page_id = page_id
        self.base = "https://graph.facebook.com/v19.0"

    def _post(self, endpoint, data=None):
        if not data:
            data = {}
        data["access_token"] = self.token
        return requests.post(f"{self.base}/{endpoint}", data=data).json()

    def _get(self, endpoint):
        return requests.get(f"{self.base}/{endpoint}?access_token={self.token}").json()

    def post_message(self, message: str):
        return self._post(f"{self.page_id}/feed", {"message": message})

    def get_posts(self):
        return self._get(f"{self.page_id}/posts")

    def get_comments(self, post_id: str):
        return self._get(f"{post_id}/comments")

    def reply_comment(self, comment_id: str, message: str):
        return self._post(f"{comment_id}/comments", {"message": message})

    def delete_post(self, post_id: str):
        return self._post(f"{post_id}", {"method": "delete"})

    def delete_comment(self, comment_id: str):
        return self._post(f"{comment_id}", {"method": "delete"})

    # Inbox helpers
    def get_inbox_messages(self):
        """Fetch all messages from Messenger."""
        endpoint = f"{self.page_id}/conversations?fields=messages{{id,message,from,created_time}}"
        return self._get(endpoint)

    def get_messages_since(self, cutoff_time):
        """Filter messages based on cutoff time."""
        raw = self.get_inbox_messages()
        messages = []

        for conv in raw.get("data", []):
            for msg in conv.get("messages", {}).get("data", []):
                msg_time = datetime.strptime(msg["created_time"], "%Y-%m-%dT%H:%M:%S%z")
                if msg_time >= cutoff_time:
                    messages.append({
                        "message_id": msg["id"],
                        "sender_id": msg.get("from", {}).get("id"),
                        "sender_name": msg.get("from", {}).get("name"),
                        "message": msg.get("message", ""),
                        "created_time": msg["created_time"],
                    })

        return messages

    def send_message_to_user(self, psid: str, text: str):
        """Send a message to a Messenger user by their Page-Scoped ID (PSID)."""
        payload = {
            "recipient": {"id": psid},
            "message": {"text": text},
        }
        url = f"{self.base}/me/messages"
        return requests.post(url, params={"access_token": self.token}, json=payload).json()
