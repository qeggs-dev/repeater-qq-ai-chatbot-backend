from environs import Env
from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    Form,
    Query
)
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse
)

from core import (
    Core
)

app = FastAPI(title="RepeaterChatBackend")
env = Env()
load_dotenv()

chat = Core()

@app.get("/")
async def root():
    return FileResponse(env.path("WEB_PATH") / "index.html")

@app.post("/chat/completions/{user_id}")
async def chat_endpoint(
    user_id: str,
    message: str = Form(...),
    user_name: str = Form(""),
    model_type: str = Form("chat"),
    load_prompt: bool = Query(True)
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
    return JSONResponse(context)


@app.delete("/userdata/context/delete/{user_id}")
async def delete_context(user_id: str):
    """
    Endpoint for deleting context
    """
    await chat.context_manager.delete(user_id)
    return PlainTextResponse("Context deleted successfully")


@app.delete("/userdata/prompt/delete/{user_id}")
async def delete_prompt(user_id: str):
    """
    Endpoint for deleting prompt
    """
    await chat.prompt_manager.delete(user_id)
    return PlainTextResponse("Prompt deleted successfully")


@app.delete("/userdata/config/delete/{user_id}")
async def delete_config(user_id: str):
    """
    Endpoint for deleting config
    """
    await chat.user_config_manager.delete(user_id)
    return PlainTextResponse("Config deleted successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app = app,
        host = env.str("HOST", "0.0.0.0"),
        port = env.int("PORT", 8000)
    )