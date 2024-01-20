import json
import pathlib
import traceback

from typing import Optional, Generator, AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..services import TranscriptFormatterService

router = APIRouter()
crawl_output_dir = pathlib.Path('C:/Users/Steve/Projects/yogen/data/input/')
format_output_dir = pathlib.Path('C:/Users/Steve/Projects/yogen/data/output/')

@router.post("/crawl")
async def crawl(video_id: str):
    try:
        result = TranscriptFormatterService.crawl_script(video_id=video_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/crawl")
async def read_crawl(video_id: str):
    crawl_fp = crawl_output_dir / f"{video_id}_cap.txt"
    if not crawl_fp.exists():
        raise HTTPException(status_code=404, detail="Crawl result not found")
    with crawl_fp.open("r", encoding="utf-8") as f:
        return f.read()

@router.post("/format")
async def format_transcript_endpoint(video_id: str, chunk_size: Optional[int] = 5000, model_name: Optional[str] = "gpt-3.5-turbo-1106"):
    src_fp = str(crawl_output_dir / f"{video_id}_cap.txt")

    async def generator_wrapper(sync_generator: Generator[dict, None, None]) -> AsyncGenerator[dict, None]:
        for item in sync_generator:
            yield item

    async def generator():
        try:
            formatted_texts = []
            async_gen = generator_wrapper(TranscriptFormatterService.format_script(src_fp=src_fp, chunk_size=chunk_size, model_name=model_name))
            async for chunk_response in async_gen:
                formatted_texts.append(chunk_response['processed_text'])
                yield json.dumps(chunk_response)
            
            # save to output file
            output_fp = format_output_dir / f"{video_id}_cap.txt"
            with output_fp.open("w", encoding="utf-8") as f:
                f.write('\n\n'.join(formatted_texts))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # return StreamingResponse(generator(), media_type="text/plain")
    return StreamingResponse(generator(), media_type="application/json")    


@router.post("/crawl_and_format")
async def crawl_and_format(video_id: str):
    try:
        crawl_result = await crawl(video_id)
        src_fp = crawl_result['text_fp']
        async for text_chunk in TranscriptFormatterService.format_script(src_fp=src_fp):
            yield {"text_chunk": text_chunk}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
