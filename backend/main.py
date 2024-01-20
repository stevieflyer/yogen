from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import transcript

app = FastAPI()


# 加载 plugins
@app.on_event("startup")
async def startup_event():
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass


# 加载 middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # 允许来自任意端口的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 绑定路由
app.include_router(transcript.router, prefix="/transcript", tags=["transcript"])
# To run: uvicorn backend.main:app --reload
