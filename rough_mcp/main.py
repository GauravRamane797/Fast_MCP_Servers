from fastmcp import FastMCP
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import os
import re
from facebook_client import FacebookClient

# Load .env variables
load_dotenv()

PAGE_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

if not PAGE_TOKEN or not PAGE_ID:
    raise RuntimeError("ERROR: Missing FACEBOOK_PAGE_ACCESS_TOKEN or FACEBOOK_PAGE_ID in .env")

# Init Facebook API wrapper
facebook = FacebookClient(PAGE_TOKEN, PAGE_ID)

# Init MCP server
mcp = FastMCP("FacebookMCP")


def parse_period(period_str: str) -> timedelta:
    """
    Parse natural periods like:
    - 5 minutes
    - 2 hours
    - 3 days
    - 1 week
    - 4 months
    - 2 years
    into timedelta.
    """
    period_str = period_str.lower().strip()
    match = re.match(r"(\d+)\s*(minute|minutes|hour|hours|day|days|week|weeks|month|months|year|years)", period_str)
    
    if not match:
        raise ValueError(f"Invalid period: '{period_str}'. Examples: '4 days', '3 months'.")

    number = int(match.group(1))
    unit = match.group(2)

    if "minute" in unit:
        return timedelta(minutes=number)
    elif "hour" in unit:
        return timedelta(hours=number)
    elif "day" in unit:
        return timedelta(days=number)
    elif "week" in unit:
        return timedelta(weeks=number)
    elif "month" in unit:
        return timedelta(days=number * 30) # Approximate
    elif "year" in unit:
        return timedelta(days=number * 365) # Approximate


# Post/comment tools stay the same
@mcp.tool()
def post_to_facebook(message: str):
    """Post a text message to the Facebook Page."""
    return facebook.post_message(message)


@mcp.tool()
def get_page_posts():
    """Get the latest Facebook Page posts."""
    return facebook.get_posts()


@mcp.tool()
def get_post_comments(post_id: str):
    """Get comments for a specific post."""
    return facebook.get_comments(post_id)


@mcp.tool()
def reply_to_comment(comment_id: str, message: str):
    """Reply to a specific comment."""
    return facebook.reply_comment(comment_id, message)


@mcp.tool()
def delete_post(post_id: str):
    """Delete a Facebook post."""
    return facebook.delete_post(post_id)


@mcp.tool()
def delete_comment(comment_id: str):
    """Delete a specific comment."""
    return facebook.delete_comment(comment_id)


# Inbox messaging tools
@mcp.tool()
def get_messages_from_period(period: str = "7 days"):
    """
    Get Messenger inbox messages from the Page within a given period.

    Example input: "4 days", "3 months", "2 years"
    """
    delta = parse_period(period)
    cutoff = datetime.now(timezone.utc) - delta
    return facebook.get_messages_since(cutoff)


@mcp.tool()
def reply_to_message(sender_id: str, text: str):
    """Reply to a user message from the inbox by PSID."""
    return facebook.send_message_to_user(sender_id, text)


def run_server():
    mcp.run()


if __name__ == "__main__":
    run_server()
