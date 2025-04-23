import re
from mcp.server.fastmcp import FastMCP
from youtube_transcript_api import YouTubeTranscriptApi

mcp = FastMCP("youtube_transcript", host="127.0.0.1", port=8080)

@mcp.tool()
def get_youtube_transcript(url: str) -> dict:
    """Fetches transcript from a given YouTube URL.

    Args:
        url: YouTube video URL to fetch transcript from

    Returns:
        dict: Dictionary containing either transcript text or error message
            - transcript: String containing the video transcript if successful
            - error: Error message if request failed
    """
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if not video_id_match:
        return {"error": "Invalid YouTube URL"}

    video_id = video_id_match.group(1)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = "\n".join([entry["text"] for entry in transcript])
        return {"transcript": transcript_text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="sse")