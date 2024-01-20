import json
import time
import traceback
from typing import Generator

from langchain_openai.chat_models import ChatOpenAI
from stevools.util_classes import OpenAIModelManager
from stevools.string_utils import generate_random_id
from langchain_community.document_loaders import TextLoader
from langchain_community.callbacks import get_openai_callback
from langchain.text_splitter import RecursiveCharacterTextSplitter

from models import TranscriptFormatterRecord
from storage import TranscriptFormatterRecordStorage

prompt = """Please act as my YouTube subtitle text processing assistant, and help me add appropriate punctuation and correct potential typos in YouTube subtitle texts. The subtitle text is very long, so I have split it into chunks, and I will give you one chunk to process at a time.

[Example]
<Input>:
```json
{{
    "current_chunk": "i'm going to be showing you how to\\n\\ncreate this to-do list vs code extension\\n\\nwhich may look simple\\n\\nbut this code base is the foundation\\n\\nthat i use to create vs code tinder\\n\\nand it has basically all the important\\ntopics that you need to know to build\\nsomething out like that\\n\\nso starting off i'm going to be showing\\n\\nyou how to use web views in vs code this\\n\\nentire thing is a web view\\n\\nthis allows you to \\n\\nstick pretty much",
    "next_chunk_head": "anything that you want to inside of vs\\n\\ncode and\\n\\nactually build out the web views i\\n\\nlike to use a front-end framework"
}}
```
<Output>:
```json
{{
    "processed_text": "I'm going to be showing you how to create this to-do list VS Code extension, which may look simple. But this code base is the foundation that I use to create VS Code Tinder. And it has basically all the important topics that you need to know to build something out like that.\\n\\nSo, starting off, I'm going to be showing you how to use web views in VS Code. This entire thing is a web view. This allows you to stick pretty much"
}}
```
[End of Example]

As shown by the example, you should follow the guidelines:

[Guidelines]
- Your task is to add appropriate punctuation to `current_chunk` while maintaining the original meaning of the text, and correct any obvious spelling errors. Pay special attention to sentence coherence and completeness. Use `next_chunk_head` to help determine whether the end of `current_chunk` is a complete sentence.
- ONLY process `current_chunk`! `next_chunk_head` ONLY acts as reference to help you understand the end of `current_chunk`.
- Carefully paragraph the text for fluency using \\n\\n seperator. Try to Keep sentences short.
- Try to use add periods and commas, and periods are preferred, NEVER leave a long sentence without any punctuation.
- AVOID using ellipsis(...) at the end of a paragraph.

Now, it's your turn. I want to remind you again to return the results in clean JSON format, otherwise your results will not be correctly assessed. Good luck!
<Input>:
{{
    "current_chunk": {current_chunk},
    "next_chunk_head": {next_chunk_head}
}}
<Output>:
"""
storage = TranscriptFormatterRecordStorage()

class TranscriptFormatter(OpenAIModelManager):
    def __init__(self, chunk_size: int = 5000, model_name: str = "gpt-3.5-turbo-1106"):
        super().__init__(model_name=model_name)
        self._chat_model = ChatOpenAI(
            model=self.model_name
        )
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_overlap=0,
            chunk_size = chunk_size,
            separators=['\n\n', '\n', ' ']
        )

    def format_transcript(self, src_fp: str) -> Generator[dict, None, None]:
        """Format the transcript file.
        
        Args:
            src_fp (str): source file path

        Returns:
            Generator[dict, None, None]: a generator that yields the formatted text
        """
        # 1. Load and split the subtitle file
        task_id = generate_random_id(prefix="ft")
        text_chunks = TextLoader(src_fp).load_and_split(self._text_splitter)
        print(f"Load and split the subtitle file: {src_fp} into \n{len(text_chunks)} documents, task_id: {task_id}")

        # 2. Process each chunk
        last_chunk_remains = ""
        for i, chunk in enumerate(text_chunks):
            success = False
            while not success:
                try:
                    current_chunk = last_chunk_remains + str(chunk.page_content)
                    next_chunk_head = self._get_chunk_head(text_chunks[i+1].page_content) if i < len(text_chunks) - 1 else ""
                    final_prompt = prompt.format(current_chunk=json.dumps(current_chunk), next_chunk_head=json.dumps(next_chunk_head))
                    print(f"---- i = {i} / {len(text_chunks)}, length of prompt: {len(final_prompt)}, length of input chunk: {len(current_chunk)}----")
                    print(f"-------- ai thinking...")
                    before_thinking = time.time()
                    with get_openai_callback() as cb:
                        response_message = self._chat_model.invoke(final_prompt)
                    response_json = json.loads(response_message.content)
                    consumed_time = time.time() - before_thinking
                    print(f"-------- ai response in {consumed_time} seconds, response length: {len(response_message.content)}(this should be no less than the input chunk length: {len(current_chunk)})")
                    record = TranscriptFormatterRecord(
                        task_id=task_id,
                        llm_model_name=self.model_name,
                        is_success=True,
                        src_fp=src_fp,
                        prompt=final_prompt,
                        prompt_length=len(final_prompt),
                        prompt_tokens=cb.prompt_tokens,
                        raw_text_length=len(current_chunk),
                        response=response_message.content,
                        response_length=len(response_message.content),
                        completion_tokens=cb.completion_tokens,
                        consumed_time=consumed_time,
                        consumed_dollars=cb.total_cost
                    )
                    if len(response_message.content) < int(len(current_chunk) * 0.95):
                        print(f"-------- ai response is too short, retrying... the response ending is: {json.dumps(response_message.content[-50:])}, the input chunk ending is: {json.dumps(current_chunk[-50:])}")
                        record.is_success = False
                    else:
                        post_process_result = self._post_process_json(response_json)
                        yield {
                            "index": i,
                            "total": len(text_chunks),
                            "processed_text": post_process_result["processed_text"],
                        }
                        # processed_text_list.append(post_process_result["processed_text"])
                        last_chunk_remains = post_process_result["unprocessed_text"].strip('"')
                        record.is_success = True
                        success = True
                except Exception as e:
                    print(f"------------ ai response failed, retrying... the response length: {len(response_message.content)}, the response ending is: {json.dumps(response_message.content[-50:])}, the input chunk ending is: {json.dumps(current_chunk[-50:])}")
                    print(f"------------ error: {e}")
                    record.is_success = False
                    traceback.print_exc()
                finally:
                    with storage:
                        storage.insert(record)                    

    def _get_chunk_head(self, chunk: str):
        lines = chunk.split('\n')
        lines_head = [line for line in lines[:20] if len(line.strip()) > 0]
        return '\n\n'.join(lines_head[:3])

    def _post_process_json(self, response_json: dict[str, str]):
        if not isinstance(response_json, dict):
            print(f"response_json is not a dict, but {type(response_json)}")
            print(f"response_json: {response_json}")
        separator = ". "
        response_text = response_json["processed_text"].strip("```json").strip('```')
        lines = response_text.split(sep=separator)
        if not lines[-1].endswith("...") and lines[-1].endswith("."):
            unprocessed_text = ""
        else:
            unprocessed_text = lines[-1]
        processed_text = separator.join(lines[:-1]) + "."
        return {
            "processed_text": processed_text,
            "unprocessed_text": unprocessed_text
        }


def format_transcript(src_fp: str, chunk_size: int = 5000, model_name: str = "gpt-3.5-turbo-1106") -> Generator[str, None, None]:
    """Format the transcript file.

    Args:
        src_fp (str): source file path
        out_fp (str): output file path
        chunk_size (int, optional): the maximum size of a chunk. Defaults to 5000.
        model_name (str, optional): the underlying openai model. Defaults to "gpt-3.5-turbo-1106".
    
    Returns:
        Generator[str, None, None]: a generator that yields the formatted text
    """
    return TranscriptFormatter(chunk_size=chunk_size, model_name=model_name).format_transcript(src_fp=src_fp)


__all__ = [
    'TranscriptFormatter',
    'format_transcript',
]
