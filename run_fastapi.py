# region imports
# ==== 标准库 ==== #
import os
import sys
import asyncio
from uuid import uuid4
from typing import Any
from io import BytesIO
import zipfile
import json
import time
from pathlib import Path

# ==== 第三方库 ==== #
import orjson
from environs import Env
env = Env()
env.read_env()
from fastapi import (
    FastAPI,
    Request,
    BackgroundTasks,
    Form,
    Query,
    Header
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
from ConfigManager import ConfigLoader
# 一定要提前加载，否则其他模块会无法获取配置内容
configs = ConfigLoader(
    config_file_path = env.path("CONFIG_FILE_PATH", "./configs/project_config.json")
)
from core import (
    Core,
    ApiInfo,
    Context
)
from core.CallLog import CallAPILog
from Markdown import markdown_to_image, STYLES as MARKDOWN_STYLES
from admin_apikey_manager import AdminKeyManager
# endregion

# region Global Objects
app = FastAPI(title="RepeaterChatBackend")
chat = Core()

# 生成或读取API Key
admin_api_key = AdminKeyManager()
# endregion

# region Tool: validate_path
def validate_path(base_path: str | Path, user_path: str | Path) -> bool:
    """
    验证路径是否合法
    """
    # 转换为Path对象以便于操作
    base_path = Path(base_path)
    user_path = Path(user_path)

    # 获取基础路径的绝对路径
    requested_path = (base_path.resolve() / user_path).resolve()
    
    # 检查路径是否在base_path的子目录内
    return requested_path.is_relative_to(base_path)
# endregion

# region Readme
@app.get("/readme.md")
async def readme():
    readme_path = configs.get_config("readme_path", "./README.md").get_value(Path)
    if not readme_path.exists():
        raise HTTPException(status_code=404, detail="README.md not found")
    return FileResponse(readme_path, media_type="text/markdown")
# endregion

@app.get("/static/{path:path}")
async def static(path: str):
    """
    Endpoint for serving static files
    """
    static_dir = configs.get_config("static_dir", "./static").get_value(Path)
    if not (static_dir / f"{path}.png").exists():
        raise HTTPException(detail="File not found", status_code=404)
    return FileResponse(static_dir / path)

@app.get("/favicon.ico")
async def favicon():
    """
    Endpoint for serving favicon
    """
    static_dir = configs.get_config("static_dir", "./static").get_value(Path)
    if not (static_dir / "favicon.ico").exists():
        raise HTTPException(detail="File not found", status_code=404)
    return FileResponse(static_dir / "favicon.ico")

# region Chat
@app.post("/chat/completion/{user_id}")
async def chat_endpoint(
    user_id: str,
    message: str = Form(""),
    user_name: str = Form(""),
    role: str = Form("user"),
    role_name: str = Form(None),
    model_type: str | None = Form(None),
    load_prompt: bool = Form(True),
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
    return JSONResponse(context)
# endregion

# region Render
@app.post("/render/{user_id}")
async def render(
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: str,
    text: str = Form(...),
    style: str | None = Form(None),
    timeout: int | None = Form(None),
):
    """
    Endpoint for rendering markdown text to image
    """
    # 生成图片ID
    fuuid = uuid4()
    filename = f"{fuuid}.png"
    rendered_image_dir = configs.get_config("rendered_image_dir", "./temp/render").get_value(Path)

    # 延迟删除函数
    async def _wait_delete(sleep_time: int, filename: str):
        """
        等待一段时间后删除图片
        """
        async def _delete(filename: str):
            """
            删除图片
            """
            await asyncio.to_thread(os.remove, rendered_image_dir / filename)
            logger.info(f'Deleted image {filename}', user_id = user_id)
        
        try:
            await asyncio.sleep(sleep_time)
            await _delete(filename)
        except asyncio.CancelledError:
            logger.info("Image delete task cancelled", user_id = user_id)
            await _delete(filename)
        
    if style:
        if style not in MARKDOWN_STYLES:
            raise HTTPException(status_code=400, detail="Invalid style")
    else:
        # 获取用户配置
        config = await chat.user_config_manager.load(user_id)
        # 获取环境变量中的图片渲染风格
        default_style = configs.get_config("markdown_to_image_style", "light").get_value(str)
        # 获取图片渲染风格
        style = config.get('render_style', default_style)
    
    if not timeout:
        timeout = configs.get_config("rendered_default_image_timeout", 60.0).get_value(float)
    
    # 日志打印文件名和渲染风格
    logger.info(f'Rendering image {filename} for "{style}" style', user_id=user_id)

    # 调用markdown_to_image函数生成图片
    await asyncio.to_thread(
        markdown_to_image,
        markdown_text = text,
        output_path = rendered_image_dir / filename,
        style = style
    )
    create_ms = time.time_ns() // 10**6
    create = create_ms // 1000
    logger.info(f'Created image {filename}', user_id = user_id)

    # 添加一个后台任务，时间到后删除图片
    background_tasks.add_task(_wait_delete, timeout, filename)

    # 生成图片的URL
    fileurl = request.url_for("render_file", file_uuid=fuuid)

    return JSONResponse(
        {
            "image_url": str(fileurl),
            "file_uuid": str(fuuid),
            "style": style,
            "timeout": timeout,
            "text": text,
            "create": create,
            "create_ms": create_ms
        }
    )
# endregion

# region PromptVariableExpansion
@app.post("/userdata/variable/expand/{user_id}")
async def expand_variables(user_id: str, username: str = Form(...), text: str = Form(...)):
    """
    Endpoint for expanding variables
    """
    # 获取用户配置
    config = await chat.user_config_manager.load(user_id=user_id)
    if not config or not isinstance(config, dict):
        config = {}
    
    # 调用PromptVP类处理文本
    prompt_vp = await chat.get_prompt_vp(
        user_id = user_id,
        user_name = username,
        model_type = "nomodel",
        config = config
    )
    output = prompt_vp.process(text)

    # 日志输出命中信息
    logger.info(f"Prompt Hits Variable: {prompt_vp.hit_var()}/{prompt_vp.discover_var()}({prompt_vp.hit_var() / prompt_vp.discover_var() if prompt_vp.discover_var() != 0 else 0:.2%})", user_id = user_id)

    # 返回结果
    return PlainTextResponse(output)
# endregion

# region context manage
@app.get("/userdata/context/get/{user_id}")
async def get_context(user_id: str):
    """
    Endpoint for getting context
    """
    # 从chat.context_manager中加载用户ID为user_id的上下文
    context = await chat.context_manager.load(user_id, [])
    # 返回JSON格式的上下文
    return JSONResponse(context)

@app.get("/userdata/context/length/{user_id}")
async def get_context(user_id: str):
    """
    Endpoint for getting context
    """
    # 从chat.context_manager中加载用户ID为user_id的上下文
    context = await chat.context_manager.load(user_id, [])
    # 将上下文转换为Context.ContextObject对象
    context = Context.ContextObject().from_context(context)
    # 返回JSONResponse，包含上下文的总长度和上下文的长度
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
    # 从chat.context_manager中获取所有用户ID
    userid_list = await chat.context_manager.get_all_user_id()

    # 返回JSONResponse，包含所有用户ID
    return JSONResponse(userid_list)

@app.post("/userdata/context/withdraw/{user_id}")
async def withdraw_context(user_id: str, index: int = Form(...)):
    """
    Endpoint for withdrawing context
    """
    # 从chat.context_manager中加载用户ID为user_id的上下文
    context = await chat.context_manager.load(user_id, [])

    # 检查索引是否在上下文范围内
    if 0 <= index < len(context):
        context.pop(index)
        await chat.context_manager.save(user_id, context)
    else:
        raise HTTPException(400, "Index out of range")
    
    # 返回JSONResponse，新的上下文内容
    return JSONResponse(context)

@app.post("/userdata/context/rewrite/{user_id}")
async def rewrite_context(user_id: str, index: int = Form(...), content: str = Form(""), reasoning_content: str = Form("")):
    """
    Endpoint for rewriting context
    """
    # 从chat.context_manager中加载用户ID为user_id的上下文
    context = await chat.context_manager.load(user_id, [])

    # 检查索引是否在上下文范围内
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
    
    # 返回JSONResponse，新的上下文内容
    return JSONResponse(context)

@app.get("/userdata/context/branch/{user_id}")
async def get_context_branch_id(user_id: str):
    """
    Endpoint for getting context branch id list
    """
    # 获取用户ID为user_id的上下文分支ID
    branchs = await chat.context_manager.get_all_item_id(user_id)

    # 返回上下文分支ID
    return JSONResponse(branchs)

@app.get("/userdata/context/now_branch/{user_id}")
async def get_context_now_branch_id(user_id: str):
    """
    Endpoint for getting context branch id
    """
    # 获取用户ID为user_id的上下文分支ID
    branch_id = await chat.context_manager.get_default_item_id(user_id)

    # 返回上下文分支ID
    return PlainTextResponse(branch_id)

@app.post("/userdata/context/change/{user_id}")
async def change_context(user_id: str, new_branch_id: str):
    """
    Endpoint for changing context
    """

    # 设置用户ID为user_id的上下文为new_context_id
    await chat.context_manager.set_default_item_id(user_id, item = new_branch_id)

    # 返回成功文本
    return PlainTextResponse("Context changed successfully")

@app.delete("/userdata/context/delete/{user_id}")
async def delete_context(user_id: str):
    """
    Endpoint for deleting context
    """
    # 删除用户ID为user_id的上下文
    await chat.context_manager.delete(user_id)

    # 返回成功文本
    return PlainTextResponse("Context deleted successfully")
# endregion

# region prompt manage
@app.get("/userdata/prompt/get/{user_id}")
async def get_prompt(user_id: str):
    """
    Endpoint for setting prompt
    """
    # 获取用户ID为user_id的提示词
    prompt = await chat.prompt_manager.load(user_id)

    # 返回提示词内容
    return PlainTextResponse(prompt)

@app.post("/userdata/prompt/set/{user_id}")
async def set_prompt(user_id: str, prompt: str = Form(...)):
    """
    Endpoint for setting prompt
    """
    # 设置用户ID为user_id的提示词为prompt
    await chat.prompt_manager.save(user_id, prompt)

    # 返回成功文本
    return PlainTextResponse("Prompt set successfully")

@app.get("/userdata/prompt/userlist")
async def get_prompt_userlist():
    """
    Endpoint for getting prompt user list
    """
    # 获取所有用户ID
    userid_list = await chat.prompt_manager.get_all_user_id()

    # 返回用户ID列表
    return JSONResponse(userid_list)

@app.get("/userdata/prompt/branch/{user_id}")
async def get_prompt_branch_id(user_id: str):
    """
    Endpoint for getting prompt branch ID
    """
    # 获取用户ID为user_id的提示词分支ID
    branchs = await chat.prompt_manager.get_all_item_id(user_id)

    # 返回分支ID
    return JSONResponse(branchs)

@app.get("/userdata/prompt/now_branch/{user_id}")
async def get_prompt_now_branch_id(user_id: str):
    """
    Endpoint for getting prompt branch ID
    """
    # 获取用户ID为user_id的提示词分支ID
    branch_id = await chat.prompt_manager.get_default_item_id(user_id)

    # 返回分支ID
    return PlainTextResponse(branch_id)

@app.post("/userdata/prompt/change/{user_id}")
async def change_prompt(user_id: str, new_branch_id: str):
    """
    Endpoint for changing prompt
    """
    # 设置用户ID为user_id的提示词为new_prompt_id
    await chat.prompt_manager.set_default_item_id(user_id, item = new_branch_id)

    # 返回成功文本
    return PlainTextResponse("Prompt changed successfully")

@app.delete("/userdata/prompt/delete/{user_id}")
async def delete_prompt(user_id: str):
    """
    Endpoint for deleting prompt
    """
    # 删除用户ID为user_id的提示词
    await chat.prompt_manager.delete(user_id)

    # 返回成功文本
    return PlainTextResponse("Prompt deleted successfully")
# endregion

# region config manage
@app.get("/userdata/config/get/{user_id}")
async def change_config(user_id: str):
    """
    Endpoint for changing config
    """
    # 获取用户ID为user_id的配置
    config = await chat.get_config(user_id = user_id)

    # 返回配置
    return JSONResponse(config)

@app.put("/userdata/config/set/{user_id}/{value_type}")
async def set_config(user_id: str, value_type: str, key: str = Form(...), value: Any = Form(...)):
    """
    Endpoint for setting config
    """
    # 允许的值类型
    TYPES = {
        "int": int,
        "float": float,
        "string": str,
        "bool": bool,
        "dict": dict,
        "list": list,
        "null": None
    }
    # 检查值类型是否有效
    if value_type not in TYPES:
        raise HTTPException(400, "Invalid value type")
    if value_type == "null":
        value = None
    else:
        # 将值转换为指定类型
        value = TYPES[value_type](value)
    
    # 读取配置
    config = await chat.user_config_manager.load(user_id=user_id)
    
    # 更新配置
    config[key] = value

    # 保存配置
    await chat.user_config_manager.force_write(user_id=user_id, configs=config)

    # 返回新配置内容
    return JSONResponse(config.configs)

@app.post("/userdata/config/delkey/{user_id}")
async def delkey_config(user_id: str, key: str = Form(...)):
    """
    Endpoint for delkey config
    """

    # 读取配置
    config = await chat.user_config_manager.load(user_id=user_id)
    
    # 如果项不存在，则抛出错误
    if key not in config:
        raise HTTPException(400, "Key not found")

    # 删除项
    del config[key]

    # 保存配置
    await chat.user_config_manager.force_write(user_id=user_id, configs=config)

    # 返回新配置内容
    return JSONResponse(config)

@app.get("/userdata/config/userlist")
async def get_config_userlist():
    """
    Endpoint for getting config userlist
    """

    # 获取所有用户ID
    userid_list = await chat.user_config_manager.get_all_user_id()

    # 返回用户ID列表
    return JSONResponse(userid_list)

@app.get("/userdata/config/branch/{user_id}")
async def get_config_branch_id(user_id: str):
    """
    Endpoint for get config branch id
    """

    # 设置平行配置路由
    branchs = await chat.user_config_manager.get_all_item_id(user_id)

    # 返回分支ID
    return JSONResponse(branchs)

@app.get("/userdata/config/now_branch/{user_id}")
async def get_config_now_branch_id(user_id: str):
    """
    Endpoint for get config branch id
    """

    # 设置平行配置路由
    branch_id = await chat.user_config_manager.get_default_item(user_id)

    # 返回分支ID
    return PlainTextResponse(branch_id)

@app.post("/userdata/config/change/{user_id}")
async def change_config(user_id: str, new_branch_id: str = Form(...)):
    """
    Endpoint for changing config
    """

    # 设置平行配置路由
    await chat.user_config_manager.set_default_item(user_id, item = new_branch_id)

    # 返回成功文本
    return PlainTextResponse("Config changed successfully")


@app.delete("/userdata/config/delete/{user_id}")
async def delete_config(user_id: str):
    """
    Endpoint for deleting config
    """
    # 删除配置
    await chat.user_config_manager.delete(user_id)

    # 返回成功文本
    return PlainTextResponse("Config deleted successfully")
# endregion

# region userdata_file

@app.get("/userdata/file/{user_id}.zip")
async def get_userdata_file(user_id: str):
    """
    Endpoint for getting userdata file
    """
    # 创建虚拟文件缓冲区
    buffer = BytesIO()

    # 创建zip文件并写入
    with zipfile.ZipFile(buffer, "w") as zipf:
        zipf.writestr("user_context.json", json.dumps(await chat.context_manager.load(user_id = user_id, default = {}), indent = 4, ensure_ascii=False))
        zipf.writestr("user_config.json", json.dumps(await chat.user_config_manager.load(user_id = user_id, default = []), indent = 4, ensure_ascii=False))
        zipf.writestr("user_prompt.json", json.dumps(await chat.prompt_manager.load(user_id = user_id, default = ""), indent = 4, ensure_ascii=False))
    buffer.seek(0)

    # 返回zip文件
    return StreamingResponse(buffer, media_type = "application/zip")

# region get calllog
@app.get("/calllog")
async def get_calllog():
    """
    Endpoint for getting calllog
    """

    # 获取calllog
    calllogs = await chat.calllog.read_call_log()

    # 将calllog转换为字典列表
    calllog_list = [calllog_object.as_dict for calllog_object in calllogs]

    # 返回JSON响应
    return JSONResponse(calllog_list)

@app.get("/calllog/stream")
async def stream_call_logs():
    async def generate_jsonl():
        """
        将日志流转换为JSONL流格式
        """
        # 获取日志生成器
        generator = chat.calllog.read_stream_call_log()

        # 将每个日志对象转换为字典并使用orjson序列化
        async for log_obj in generator:
            # 转换为字典并使用orjson序列化
            json_line = orjson.dumps(
                log_obj.as_dict,
                option=orjson.OPT_APPEND_NEWLINE
            )

            # 生成JSONL行
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
    rendered_image_dir = configs.get_config("rendered_image_dir", "./temp/render").get_value(Path)
    # 检查文件是否存在
    if not (rendered_image_dir / f"{file_uuid}.png").exists():
        raise HTTPException(detail="File not found", status_code=404)
    
    # 返回文件
    return FileResponse(rendered_image_dir / f"{file_uuid}.png")
# endregion

# region Admin API
@app.post("/admin/reload/apiinfo")
async def reload_apiinfo(api_key: str = Header(..., alias="X-Admin-API-Key")):
    """
    Endpoint for reloading apiinfo
    """
    if not admin_api_key.validate_key(api_key):
        raise HTTPException(detail="Invalid API key", status_code=401)
    logger.info("Reloading apiinfo", user_id="[Admin API]")
    await chat.reload_apiinfo()
    return JSONResponse({"detail": "Apiinfo reloaded"})


@app.post("/admin/regenerate/admin_key")
async def regenerate_admin_key(api_key: str = Header(..., alias="X-Admin-API-Key")):
    """
    Endpoint for regenerating admin key
    """
    if not admin_api_key.validate_key(api_key):
        raise HTTPException(detail="Invalid API key", status_code=401)
    logger.info("Regenerating admin key", user_id="[Admin API]")
    admin_api_key.generate()
# endregion

def main():
    import uvicorn
    host = "0.0.0.0" # 默认监听所有地址
    port = 8000 # 默认监听8000端口

    host = env.str("HOST", host)
    port = env.int("PORT", port)

    host = configs.get_config("server.host", host).get_value(str)
    port = configs.get_config("server.port", port).get_value(int)

    uvicorn.run(
        app = app,
        host = host,
        port = port
    )

if __name__ == "__main__":
    main()