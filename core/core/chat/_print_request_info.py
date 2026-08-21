# ==== 标准库 ==== #
from urllib.parse import urljoin

# ==== 第三方库 ==== #
from loguru import logger

# ==== 自定义库 ==== #
from ...context import (
    ContentUnit,
)
from ...global_config_manager import ConfigManager
from ...assist_struct import (
    RequestUserInfo,
)
from ...clients.model_info import (
    ModelInfo,
)

def print_request_info(
        user_id: str,
        api: ModelInfo,
        user_input: ContentUnit | None,
        suffix: str | None,
        user_info: RequestUserInfo,
        role_name: str | None = None
    ) -> None:
    logger.info(
        "API URL: {url}",
        user_id = user_id,
        url = urljoin(api.base_url, api.endpoint)
    )
    logger.info(
        "API Model: {parent}/{model_name}",
        user_id = user_id,
        parent = api.parent,
        model_name = api.name
    )

    # 打印上下文信息
    if user_input is not None:
        if user_input.content:
            if isinstance(user_input.content, str):
                logger.info(
                    "Message:\n{message}",
                    message = user_input.content,
                    user_id = user_id
                )
            else:
                logger.info(
                    "Message:\n{message}",
                    message = user_input.content_to_string(
                        ConfigManager.get_configs().context.max_log_length_for_non_text_content
                    ),
                    user_id = user_id
                )
        else:
            logger.warning(
                "Message is empty",
                user_id = user_id
            )
    else:
        logger.warning(
            "No message to send",
            user_id = user_id
        )
    
    if suffix:
        logger.info(
            "Suffix: \n{suffix}",
            user_id = user_id,
            suffix = suffix
        )

    # 如果有设置用户信息，则打印日志
    if user_info.username:
        logger.info(
            "User Name: {username}",
            user_id = user_id,
            username = user_info.username
        )
    if user_info.nickname:
        logger.info(
            "User Nickname: {nickname}",
            user_id = user_id,
            nickname = user_info.nickname
        )
    if user_info.gender:
        logger.info(
            "User Gender: {gender}",
            user_id = user_id,
            gender = user_info.gender
        )
    if user_info.age is not None:
        logger.info(
            "User Age: {age}",
            user_id = user_id,
            age = user_info.age
        )
    if role_name:
        logger.info(
            "Role Name: {role_name}",
            user_id = user_id,
            role_name = role_name
        )