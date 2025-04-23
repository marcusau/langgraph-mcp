import re
from mcp.server.fastmcp import FastMCP
from youtube_transcript_api import YouTubeTranscriptApi
import json
import os

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
with open(path+"/setting.json", "r") as f:
    setting = json.load(f)
host = setting["host"]
port = setting["port"]["youtube_transcript"]
mcp_transport = setting["transport"]
server_name = setting["server_name"]["youtube_transcript"]

mcp = FastMCP(server_name, host=host , port=port )

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
    mcp.run(transport=mcp_transport)