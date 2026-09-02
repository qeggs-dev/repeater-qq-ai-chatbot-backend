from ......repeater_main import RepeaterMain
from ......global_config_manager import ConfigManager
from ......assist_struct import RequestUserInfo
from .._router import prompt_router
from fastapi.responses import (
    PlainTextResponse
)
from fastapi import Query
from loguru import logger

@prompt_router.get("/render/{user_id}")
@prompt_router.get("/render/{user_id}.md")
async def render_prompt(
    user_id: str,
    model_id: str | list[str] | None = Query(None),
    username: str | None = Query(None),
    nickname: str | None = Query(None),
    age: int | float | None = Query(None),
    gender: str | None = Query(None)
):
    """
    Render prompt

    Args:
        user_id (str): User ID
    
    Returns:
        PlainTextResponse: Rendered prompt
    """
    server = RepeaterMain.get_now_server()
    runtime = server.runtime
    context_loader = server.core.get_context_loader()
    user_config = await runtime.user_config_manager.load(user_id)
    global_config = ConfigManager.get_configs()
    if model_id is None:
        model_id = user_config.model_id
    if model_id is None:
        model_id = global_config.model_api.default_model_id
    model = await runtime.model_info_client.get_random_model(model_id)
    prompt = await context_loader.load_prompt(
        user_id = user_id,
        static_resources_client = runtime.static_resources_client,
        template_parser = await server.core.get_template_parser(
            user_config = user_config,
            global_config = global_config,
            model = model,
            user_info = RequestUserInfo(
                username = username,
                nickname = nickname,
                age = age,
                gender = gender
            )
        )
    )

    logger.info("Get prompt", user_id=user_id)

    # 返回提示词内容
    return PlainTextResponse(prompt.content)