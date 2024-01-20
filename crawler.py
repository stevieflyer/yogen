import pathlib

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter, TextFormatter

def crawl_youtube_transcript(video_id: str, output_dir: str) -> dict:
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    json_fp = output_dir / f"{video_id}_cap.json"
    text_fp = output_dir / f"{video_id}_cap.txt"

    transcript = YouTubeTranscriptApi.get_transcript(video_id=video_id)
    json_formatter = JSONFormatter()
    text_formatter = TextFormatter()

    with json_fp.open("w", encoding="utf-8") as f:
        f.write(json_formatter.format_transcript(transcript))

    with text_fp.open("w", encoding="utf-8") as f:
        f.write(text_formatter.format_transcript(transcript))

    return {
        'json_fp': str(json_fp),
        'text_fp': str(text_fp),
    }


__all__ = [
    'crawl_youtube_transcript',
]
