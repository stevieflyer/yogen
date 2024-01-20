from typing import Generator

from chatbot import format_transcript
from crawler import crawl_youtube_transcript


output_dir: str = 'C:/Users/Steve/Projects/yogen/data/input/'

class TranscriptFormatterService:
    @staticmethod
    def crawl_script(video_id: str) -> dict:
        return crawl_youtube_transcript(video_id=video_id, output_dir=output_dir)

    @staticmethod
    def format_script(src_fp: str, chunk_size: int = 5000, model_name: str = "gpt-3.5-turbo-1106") -> Generator[dict, None, None]:
        return format_transcript(src_fp=src_fp, chunk_size=chunk_size, model_name=model_name)
