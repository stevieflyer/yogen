<script lang="ts">
  import ProgressBar from "@okrad/svelte-progressbar";
  import { Circle3 } from "svelte-loading-spinners";

  let videoId = "";
  let model_name = "";
  let chunk_size = 500;
  let processedTexts: string[] = [];
  let crawl_text: string = "";
  let progress = 0;
  let totalChunks = 0;
  let formatting = false;
  let crawling = false;

  let already_crawled = false;
  let crawled_text_video_id = "";

  // default value
  let default_model_name = "gpt-3.5-turbo-1106";
  let default_videoId = "NrO0CJCbYLA";

  $: enable_format =
    !formatting &&
    already_crawled &&
    videoId !== "" &&
    crawled_text_video_id === videoId;

  async function crawlScript() {
    // 如果已经爬取过了，就不再爬取
    if (already_crawled && crawled_text_video_id === videoId) {
      return;
    }
    crawling = true;
    if (videoId === "") {
      videoId = default_videoId;
    }

    try {
      // 向后端发送 POST 请求，调用 /crawl 端点
      const response = await fetch(
        `http://localhost:8000/transcript/crawl?video_id=${videoId}`,
        {
          method: "POST",
        }
      );

      if (response.status === 200) {
        // 爬取成功，将已经爬取过的标志设置为 true
        already_crawled = true;
        crawled_text_video_id = videoId;
        crawl_text = await readCrawled(videoId);
      } else {
        console.error("Failed to crawl script");
      }
    } catch (error) {
      console.error("Error while crawling:", error);
    }
    crawling = false;
  }

  async function readCrawled(video_id: string) {
    const response = await fetch(
      `http://localhost:8000/transcript/crawl?video_id=${video_id}`,
      {
        method: "GET",
      }
    );
    let response_text = await response.text();
    let final_text = JSON.parse(response_text); // 去除引号
    final_text = final_text.replace(/\n/g, "<br>"); // 正确显示换行
    console.log("final_text:", final_text);
    return final_text;
  }

  async function formatScript() {
    if (videoId === "") {
      videoId = default_videoId;
    }
    if (model_name === "") {
      model_name = default_model_name;
    }
    formatting = true;
    processedTexts = [];
    console.log("formatScript");
    const response = await fetch(
      `http://localhost:8000/transcript/format?video_id=${videoId}&chunk_size=${chunk_size}&model_name=${model_name}`,
      {
        method: "POST",
      }
    );

    if (!response.body) {
      console.error("No response body");
      return;
    }

    const reader = response.body.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // 将接收到的 Uint8Array 转换为字符串
      const chunkStr = new TextDecoder().decode(value);
      const chunk = JSON.parse(chunkStr);

      processedTexts = [...processedTexts, chunk.processed_text];
      totalChunks = chunk.total;
      progress = chunk.index;
    }
    formatting = false;
  }
</script>

<div class="h-screen">
  <div class=" h-12 text-center p-2">
    <h1 class= "text-lg" >Transform YouTube To Article with Two Clicks!</h1>
  </div>
  <div class="flex mx-1">
    <div
      class="control-panel flex flex-1 flex-col p-4 border-r justify-between"
    >
      <div class="input-groupflex-col">
        <div class="video-id-input my-4 flex items-center">
          <span class="control-label">Video ID</span>
          <input
            type="text"
            class="border-2 border-gray-200 flex-grow rounded p-1 ms-2"
            placeholder="NrO0CJCbYLA"
            bind:value={videoId}
          />
        </div>
        <div class="model-name-input my-4 flex items-center">
          <span class="control-label">Model Name</span>
          <input
            type="text"
            class="border-2 border-gray-200 flex-grow rounded p-1 ms-2"
            placeholder="gpt-3.5-turbo-1106"
            bind:value={model_name}
          />
        </div>
        <div class="chunk-size-input flex justify-between my-4">
          <span class="control-label"> Chunk Size</span>
          <input
            class="flex-grow mx-2"
            type="range"
            step="100"
            min="500"
            max="8000"
            bind:value={chunk_size}
          />
          <span>{chunk_size}</span>
        </div>
      </div>
      <div class="button-group flex justify-between">
        <button class="btn mb-2 rounded" on:click={crawlScript}>Crawl</button>
        <button
          class="btn mb-2 rounded"
          on:click={formatScript}
          disabled={!enable_format}>Format</button
        >
      </div>
    </div>
    <div class="result-panel flex flex-col p-3 justify-between">
      <div class="text-areas">
        <div class="crawl-text-area text-center">
          <div class="title flex align-middle justify-center">
            <span class="me-2">Crawled Raw Subtitle</span>
            {#if crawling}
              <Circle3 size="32" unit="px" />
            {/if}
            {#if already_crawled}
              <span class="ms-2 text-green-500"
                >(character count: {crawl_text.length})</span
              >
            {/if}
          </div>
          <div class=" mb-4 h-48 overflow-auto bg-sky-100 rounded p-2">
            <div class="text-start">{@html crawl_text}</div>
          </div>
        </div>
        <!-- hline -->
        <hr class="my-2" />
        <div class="format-text-area">
          <div class="title text-center flex items-center justify-center">
            Formatted Subtitle
            {#if formatting}
              <Circle3 size="32" unit="px" />
            {/if}
          </div>
          <div class="mb-4 h-48 overflow-auto bg-sky-100 roudned p-2">
            {#each processedTexts as text}
              <span class="text-container">{text}</span>
            {/each}
          </div>
        </div>
      </div>
      <div class="my-2 flex py-2 progression-area items-center">
        {#if formatting || progress > 0}
          <ProgressBar
            series={[
              totalChunks != 0
                ? Math.round((100 * (progress + 1)) / totalChunks)
                : 0,
            ]}
          />
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .control-panel {
    width: 40%;
    flex: 1;
  }
  .result-panel {
    flex: 2;
  }
  .text-container {
    white-space: pre-wrap;
  }
  .btn {
    background-color: skyblue;
    color: white;
    padding: 8px 16px;
    border: none;
    cursor: pointer;
  }
  .btn:hover {
    background-color: blue;
  }
  .btn:disabled {
    background-color: gray;
    cursor: not-allowed;
  }

  .control-label {
    width: 110px;
  }

  .title {
    height: 32px;
  }
</style>
