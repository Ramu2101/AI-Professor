from __future__ import annotations

from typing import Any

import requests
import streamlit as st


class YouTubeServiceError(RuntimeError):
    """Raised when YouTube API lookup fails."""


@st.cache_data(ttl=3600, show_spinner=False)
def search_youtube_video(topic: str, youtube_api_key: str) -> dict[str, Any] | None:
    if not youtube_api_key:
        return None

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{topic} tutorial",
        "type": "video",
        "maxResults": 1,
        "key": youtube_api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        data = response.json()
    except requests.exceptions.Timeout as exc:
        raise YouTubeServiceError("YouTube request timed out.") from exc
    except requests.exceptions.ConnectionError as exc:
        raise YouTubeServiceError("Network error while contacting YouTube API.") from exc
    except requests.exceptions.RequestException as exc:
        raise YouTubeServiceError(f"YouTube API request failed: {exc}") from exc

    if response.status_code != 200:
        error = data.get("error", {})
        message = error.get("message", "YouTube API error")
        reason = ""
        errors = error.get("errors", [])
        if errors:
            reason = errors[0].get("reason", "")

        reason_or_message = (reason or message).lower()
        if "quota" in reason_or_message:
            raise YouTubeServiceError("YouTube API quota exceeded. Try again later.")
        if "keyinvalid" in reason_or_message or "api key" in reason_or_message:
            raise YouTubeServiceError("Invalid YouTube API key.")
        raise YouTubeServiceError(f"YouTube API error: {reason or message}")

    items = data.get("items", [])
    if not items:
        return None

    video_id = items[0].get("id", {}).get("videoId")
    title = items[0].get("snippet", {}).get("title", "")
    if not video_id:
        return None

    return {
        "video_id": video_id,
        "title": title,
        "video_url": f"https://www.youtube.com/watch?v={video_id}",
    }