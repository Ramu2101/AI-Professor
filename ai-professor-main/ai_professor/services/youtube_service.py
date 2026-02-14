from __future__ import annotations

from typing import Any

import requests
import streamlit as st


class YouTubeServiceError(RuntimeError):
    """Raised when YouTube API search fails."""


@st.cache_data(ttl=3600, show_spinner=False)
def search_youtube_video(topic: str, youtube_api_key: str) -> dict[str, Any] | None:
    if not youtube_api_key:
        return None

    params = {
        "part": "snippet",
        "q": f"{topic} tutorial",
        "type": "video",
        "maxResults": 1,
        "key": youtube_api_key,
    }

    try:
        response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params, timeout=20)
        data = response.json()
    except requests.exceptions.Timeout as exc:
        raise YouTubeServiceError("YouTube request timed out.") from exc
    except requests.exceptions.ConnectionError as exc:
        raise YouTubeServiceError("Network error while contacting YouTube API.") from exc
    except requests.exceptions.RequestException as exc:
        raise YouTubeServiceError(f"YouTube request failed: {exc}") from exc

    if response.status_code != 200:
        error = data.get("error", {})
        message = error.get("message", "YouTube API error")
        reason = ""
        errors = error.get("errors", [])
        if errors:
            reason = errors[0].get("reason", "")

        normalized = (reason or message).lower()
        if "quota" in normalized:
            raise YouTubeServiceError("YouTube API quota exceeded. Please try later.")
        if "keyinvalid" in normalized or "api key" in normalized:
            raise YouTubeServiceError("Invalid YouTube API key.")
        raise YouTubeServiceError(f"YouTube API error: {reason or message}")

    items = data.get("items", [])
    if not items:
        return None

    first = items[0]
    video_id = first.get("id", {}).get("videoId")
    title = first.get("snippet", {}).get("title", "")

    if not video_id:
        return None

    return {
        "video_id": video_id,
        "title": title,
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }