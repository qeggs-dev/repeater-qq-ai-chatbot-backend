# ==== 标准库 ==== #
import os
import argparse
import asyncio
from uuid import uuid4
from typing import Any
from io import BytesIO
import zipfile
import json

# ==== 第三方库 ==== #
import orjson
from environs import Env
from fastapi import (
    FastAPI,
    Request,
    BackgroundTasks,
    Form,
    Query
)
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse,
    StreamingResponse
)
from fastapi.exceptions import (
    HTTPException
)
from loguru import logger

# ==== 自定义库 ==== #
from core import (
    Core,
    ApiInfo,
    Context
)
from core.CallLog import CallAPILog
from Markdown import markdown_to_image
from Markdown import STYLES as MARKDOWN_STYLES

app = FastAPI(title="RepeaterChatBackend")
env = Env()
parser = argparse.ArgumentParser(description='RepeaterChatBackend')
parser.add_argument(
    '--debug', '-d',
    action='store_const',
    const="./debug.env",  # 如果指定 --debug，则使用 debug.env
    default="./run.env",     # 否则默认 .env
    help='enable debug mode (loads debug.env instead of .env)'
)
args = parser.parse_args()

env.read_env(args.debug)

chat = Core()

# region Web
@app.get("/")
@app.get("/web")
async def root():
    return FileResponse(env.path("WEB_PATH") / "index.html")

@app.get("/web/calllog")
async def root():
    return FileResponse(env.path("WEB_PATH") / "calllog.html")

@app.get("/web/admin")
async def root():
    return FileResponse(env.path("WEB_PATH") / "admin" / "index.html")

@app.get("/web/admin/chat")
async def root():
    return FileResponse(env.path("WEB_PATH") / "admin" / "chat.html")

@app.get("/web/admin/prompt")
async def root():
    return FileResponse(env.path("WEB_PATH") / "admin" / "prompt.html")

@app.get("/web/admin/config")
async def root():
    return FileResponse(env.path("WEB_PATH") / "admin" / "config.html")
# endregion

# region Readme
@app.get("/readme.md")
async def readme():
    readme_path = env.path("README_FILE_PATH", "README.md")
    if not readme_path.exists():
        raise HTTPException(status_code=404, detail="README.md not found")
    return FileResponse(readme_path, media_type="text/markdown")
# endregion

# region static
@app.get("/static/{path:path}")
async def static(path: str):
    """
    Endpoint for serving static files
    """
    if not (env.path("STATIC_DIR") / f"{path}.png").exists():
        raise HTTPException(detail="File not found", status_code=404)
    return FileResponse(env.path("STATIC_DIR") / path)

@app.get("/favicon.ico")
async def favicon():
    """
    Endpoint for serving favicon
    """
    if not (env.path("STATIC_DIR") / "favicon.ico").exists():
        raise HTTPException(detail="File not found", status_code=404)
    return FileResponse(env.path("STATIC_DIR") / "favicon.ico")
# endregion

# region Chat
@app.post("/chat/completion/{user_id}")
async def chat_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: str,
    message: str = Form(""),
    user_name: str = Form(""),
    role: str = Form("user"),
    role_name: str = Form(None),
    model_type: str | None = Form(None),
    load_prompt: bool = Form(True),
    rendering: bool = Form(False),
    save_context: bool = Form(True),
    reference_context_id: str | None = Form(None),
    continue_completion: bool = Form(False)
):
    """
    Endpoint for chat
    """
    if continue_completion and message:
        raise HTTPException(detail="Cannot send message when continuing completion", status_code=400)
    try:
        context = await chat.Chat(
            user_id = user_id,
            message = message,
            user_name = user_name,
            role = role,
            role_name = role_name,
            model_type = model_type,
            print_chunk = True,
            load_prompt = load_prompt,
            save_context = save_context,
            reference_context_id = reference_context_id,
            continue_completion = continue_completion
        )
    except ApiInfo.APIGroupNotFoundError as e:
        raise HTTPException(detail=str(e), status_code=400)
    if rendering:
        text = ""
        if 'reasoning_content' in context and context['reasoning_content']:
            text += ('> ' + context['reasoning_content'].replace('\n', '\n> ')).strip() + '\n\n---\n\n'
        text += context['content']
        fuuid = uuid4()
        filename = f"{fuuid}.png"

        async def _wait_delete(sleep_time: int, filename: str):
            async def _delete(filename: str):
                await asyncio.to_thread(os.remove, env.path("RENDERED_IMAGE_DIR") / filename)
                logger.info(f'Deleted image {filename}', user_id=user_id)
            try:
                await asyncio.sleep(sleep_time)
            finally:
                await _delete(filename)
        
        config:dict = await chat.user_config_manager.load(user_id, default={})
        default_style = env.str("MARKDOWN_TO_IMAGE_STYLE", "light")
        if isinstance(config, dict):
            style = config.get('render_style', default_style)
        else:
            style = default_style
        logger.info(f'Rendering image {filename} for "{style}" style', user_id=user_id)
        await asyncio.to_thread(
            markdown_to_image,
            markdown_text = text,
            output_path = env.path("RENDERED_IMAGE_DIR") / filename,
            style = style
        )
        logger.info(f'Created image {filename}', user_id=user_id)
        background_tasks.add_task(_wait_delete, 60, filename)
        fileurl = request.url_for("render_file", file_uuid=fuuid)
        context['image_url'] = str(fileurl)
        context['file_uuid'] = str(fuuid)
    return JSONResponse(context)
# endregion

# region PromptVariableExpansion
@app.post("/userdata/variable/expand/{user_id}")
async def expand_variables(user_id: str, username: str = Form(...), text: str = Form(...)):
    """
    Endpoint for expanding variables
    """
    config = await chat.user_config_manager.load(user_id=user_id)
    if not config or not isinstance(config, dict):
        config = {}
    prompt_vp = await chat.get_prompt_vp(
        user_id = user_id,
        user_name = username,
        model_type = "nomodel",
        config = config
    )
    output = prompt_vp.process(text)
    logger.info(f"Prompt Hits Variable: {prompt_vp.hit_var()}/{prompt_vp.discover_var()}({prompt_vp.hit_var() / prompt_vp.discover_var() if prompt_vp.discover_var() != 0 else 0:.2%})", user_id = user_id)
    return PlainTextResponse(output)
# endregion

# region context manage
@app.get("/userdata/context/get/{user_id}")
async def get_context(user_id: str):
    """
    Endpoint for getting context
    """
    context = await chat.context_manager.load(user_id, [])
    return JSONResponse(context)

@app.get("/userdata/context/length/{user_id}")
async def get_context(user_id: str):
    """
    Endpoint for getting context
    """
    context = await chat.context_manager.load(user_id, [])
    context = Context.ContextObject().from_context(context)
    return JSONResponse(
        {
            "total_context_length": context.total_length,
            "context_length": len(context)
        }
    )
@app.get("/userdata/context/userlist")
async def get_context_userlist():
    """
    Endpoint for getting context
    """
    userid_list = await chat.context_manager.get_all_user_id()
    return JSONResponse(userid_list)

@app.post("/userdata/context/withdraw/{user_id}")
async def withdraw_context(user_id: str, index: int = Form(...)):
    """
    Endpoint for withdrawing context
    """
    context = await chat.context_manager.load(user_id, [])
    if 0 <= index < len(context):
        context.pop(index)
        await chat.context_manager.save(user_id, context)
    else:
        raise HTTPException(400, "Index out of range")
    return JSONResponse(context)

@app.post("/userdata/context/rewrite/{user_id}")
async def rewrite_context(user_id: str, index: int = Form(...), content: str = Form(""), reasoning_content: str = Form("")):
    """
    Endpoint for rewriting context
    """
    context = await chat.context_manager.load(user_id, [])
    if 0 <= index < len(context):
        if content:
            context[index]["content"] = content
        if reasoning_content:
            if context[index]["role"] == "assistant":
                context[index]["reasoning_content"] = reasoning_content
            else:
                raise HTTPException(400, "Only assistant can have reasoning_content")
        await chat.context_manager.save(user_id, context)
    else:
        raise HTTPException(400, "Index out of range")
    return JSONResponse(context)

@app.post("/userdata/context/change/{user_id}")
async def change_context(user_id: str, new_context_id: str):
    """
    Endpoint for changing context
    """
    await chat.context_manager.set_default_item(user_id, item = new_context_id)
    return PlainTextResponse("Context deleted successfully")

@app.delete("/userdata/context/delete/{user_id}")
async def delete_context(user_id: str):
    """
    Endpoint for deleting context
    """
    await chat.context_manager.delete(user_id)
    return PlainTextResponse("Context deleted successfully")
# endregion

# region prompt manage
@app.get("/userdata/prompt/get/{user_id}")
async def get_prompt(user_id: str):
    """
    Endpoint for setting prompt
    """
    prompt = await chat.prompt_manager.load(user_id)
    return PlainTextResponse(prompt)

@app.post("/userdata/prompt/set/{user_id}")
async def set_prompt(user_id: str, prompt: str = Form(...)):
    """
    Endpoint for setting prompt
    """
    await chat.prompt_manager.save(user_id, prompt)
    return PlainTextResponse("Prompt set successfully")

@app.get("/userdata/prompt/userlist")
async def get_prompt_userlist():
    """
    Endpoint for getting prompt user list
    """
    userid_list = await chat.prompt_manager.get_all_user_id()
    return JSONResponse(userid_list)

@app.post("/userdata/prompt/change/{user_id}")
async def change_prompt(user_id: str, new_prompt_id: str):
    """
    Endpoint for changing prompt
    """
    await chat.prompt_manager.set_default_item(user_id, item = new_prompt_id)
    return PlainTextResponse("Prompt deleted successfully")

@app.delete("/userdata/prompt/delete/{user_id}")
async def delete_prompt(user_id: str):
    """
    Endpoint for deleting prompt
    """
    await chat.prompt_manager.delete(user_id)
    return PlainTextResponse("Prompt deleted successfully")
# endregion

# region config manage
@app.get("/userdata/config/get/{user_id}")
async def change_config(user_id: str):
    """
    Endpoint for changing config
    """
    config = await chat.get_config(user_id = user_id)
    return JSONResponse(config)

@app.put("/userdata/config/set/{user_id}/{value_type}")
async def set_config(user_id: str, value_type: str, key: str = Form(...), value: Any = Form(...)):
    """
    Endpoint for setting config
    """
    TYPES = {
        "int": int,
        "float": float,
        "string": str,
        "bool": bool,
        "dict": dict,
        "list": list,
        "null": None
    }
    if value_type not in TYPES:
        raise HTTPException(400, "Invalid value type")
    if value_type == "null":
        value = None
    else:
        value = TYPES[value_type](value)
    config = await chat.user_config_manager.load(user_id=user_id)
    if config  is None:
        config = {}
    config[key] = value
    await chat.user_config_manager.save(user_id=user_id, data=config)
    return JSONResponse(config)

@app.post("/userdata/config/delkey/{user_id}")
async def delkey_config(user_id: str, key: str = Form(...)):
    """
    Endpoint for delkey config
    """
    config:dict = await chat.user_config_manager.load(user_id=user_id)
    config.pop(key)
    await chat.user_config_manager.save(user_id=user_id, config=config)
    return JSONResponse(config)

@app.get("/userdata/config/userlist")
async def get_config_userlist():
    """
    Endpoint for getting config userlist
    """
    userid_list = await chat.user_config_manager.get_all_user_id()
    return JSONResponse(userid_list)

@app.post("/userdata/config/change/{user_id}")
async def change_config(user_id: str, new_config_id: str):
    """
    Endpoint for changing config
    """
    await chat.user_config_manager.set_default_item(user_id, item = new_config_id)
    return PlainTextResponse("Config deleted successfully")


@app.delete("/userdata/config/delete/{user_id}")
async def delete_config(user_id: str):
    """
    Endpoint for deleting config
    """
    await chat.user_config_manager.delete(user_id)
    return PlainTextResponse("Config deleted successfully")
# endregion

# region userdata_file

@app.get("/userdata/file/{user_id}.zip")
async def get_userdata_file(user_id: str):
    """
    Endpoint for getting userdata file
    """
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zipf:
        zipf.writestr("user_context.json", json.dumps(await chat.context_manager.load(user_id = user_id, default = {}), indent = 4, ensure_ascii=False))
        zipf.writestr("user_config.json", json.dumps(await chat.user_config_manager.load(user_id = user_id, default = []), indent = 4, ensure_ascii=False))
        zipf.writestr("user_prompt.json", json.dumps(await chat.prompt_manager.load(user_id = user_id, default = ""), indent = 4, ensure_ascii=False))
    buffer.seek(0)
    return StreamingResponse(buffer, media_type = "application/zip")

# region get calllog
@app.get("/calllog")
async def get_calllog():
    """
    Endpoint for getting calllog
    """
    calllogs = await chat.calllog.read_call_log()
    calllog_list = [calllog_object.as_dict for calllog_object in calllogs]
    return JSONResponse(calllog_list)

@app.get("/calllog/stream")
async def stream_call_logs():
    async def generate_jsonl():
        generator = chat.calllog.read_stream_call_log()
        async for log_obj in generator:
            # 转换为字典并使用orjson序列化
            json_line = orjson.dumps(
                log_obj.as_dict,
                option=orjson.OPT_APPEND_NEWLINE
            )
            yield json_line

    return StreamingResponse(
        generate_jsonl(),
        media_type="application/x-ndjson",  # 保持JSONL格式
        headers={
            # 关键：不设置Content-Disposition，避免浏览器触发下载
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
# endregion

# region get files
@app.get("/file/render/{file_uuid}.png", name = "render_file")
async def render_file(file_uuid: str):
    """
    Endpoint for rendering file
    """
    if not (env.path("RENDERED_IMAGE_DIR") / f"{file_uuid}.png").exists():
        raise HTTPException(detail="File not found", status_code=404)
    return FileResponse(env.path("RENDERED_IMAGE_DIR") / f"{file_uuid}.png")
# endregion


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app = app,
        host = env.str("HOST", "0.0.0.0"),
        port = env.int("PORT", 8000)
    )