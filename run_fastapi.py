import os
import asyncio
from uuid import uuid4

from environs import Env
from dotenv import load_dotenv
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
    PlainTextResponse
)
from fastapi.exceptions import (
    HTTPException
)
from loguru import logger

from core import (
    Core
)
from Markdown import markdown_to_image

app = FastAPI(title="RepeaterChatBackend")
env = Env()
load_dotenv()

chat = Core()

@app.get("/")
async def root():
    return FileResponse(env.path("WEB_PATH") / "index.html")

# region Chat
@app.post("/chat/completion/{user_id}")
async def chat_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: str,
    message: str = Form(...),
    user_name: str = Form(""),
    model_type: str = Form("chat"),
    load_prompt: bool = Form(True),
    rendering: bool = Form(False),
):
    """
    Endpoint for chat
    """
    context = await chat.Chat(
        user_id = user_id,
        message = message,
        user_name = user_name,
        model_type = model_type,
        print_chunk = True,
        load_prompt = load_prompt
    )
    if rendering:
        text = ""
        if 'rendering_content' in context:
            text += ('> ' + context['reasoning_content'].replace('\n', '\n> ')).strip() + '\n\n---\n\n'
        text += context['content']
        fuuid = uuid4()

        async def _wait_delete(sleep_time: int):
            await asyncio.sleep(sleep_time)
            await asyncio.to_thread(os.remove, env.path("RENDERED_IMAGE_DIR") / f"{fuuid}.png")
            logger.info(f'Deleted image {fuuid}.png', user_id=user_id)
        
        await asyncio.to_thread(markdown_to_image, text, env.path("RENDERED_IMAGE_DIR") / f"{fuuid}.png")
        logger.info(f'Created image {fuuid}.png', user_id=user_id)
        background_tasks.add_task(_wait_delete, 60)
        fileurl = request.url_for("render_file", file_uuid=fuuid)
        context['image_url'] = str(fileurl)
        context['file_uuid'] = str(fuuid)
    return JSONResponse(context)
# endregion

# region context manage
@app.post("/userdata/context/change/{user_id}")
async def change_context(user_id: str, new_context_id: str):
    """
    Endpoint for deleting context
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
@app.post("/userdata/prompt/set/{user_id}")
async def set_prompt(user_id: str, prompt: str = Form(...)):
    """
    Endpoint for setting prompt
    """
    await chat.prompt_manager.save(user_id, prompt)
    return PlainTextResponse("Prompt set successfully")

@app.post("/userdata/prompt/change/{user_id}")
async def change_prompt(user_id: str, new_prompt_id: str):
    """
    Endpoint for deleting prompt
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
@app.post("/userdata/config/change/{user_id}")
async def change_config(user_id: str, new_config_id: str):
    """
    Endpoint for deleting config
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

# region get files
@app.get("/file/render/{file_uuid}.png", name = "render_file")
async def render_file(file_uuid: str):
    """
    Endpoint for rendering file
    """
    if not (env.path("RENDERED_IMAGE_DIR") / f"{file_uuid}.png").exists():
        return HTTPException(detail="File not found", status_code=404)
    return FileResponse(env.path("RENDERED_IMAGE_DIR") / f"{file_uuid}.png")
# endregion

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app = app,
        host = env.str("HOST", "0.0.0.0"),
        port = env.int("PORT", 8000)
    )