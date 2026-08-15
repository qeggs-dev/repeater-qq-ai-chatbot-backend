from ...clients.model_info import ModelsClient, ModelInfo
from ...global_config_manager import GlobalConfigs
from ...user_config_manager import UserConfigs

async def get_model(
        model_id: str | list[str] | None,
        model_client: ModelsClient,
        user_configs: UserConfigs,
        global_configs: GlobalConfigs
    ) -> tuple[str | list[str], ModelInfo]:
    model_id = model_id
    if model_id is None:
        model_id = user_configs.image_model_id
    if model_id is None:
        model_id = global_configs.model_api.default_image_model_id
    
    model = await model_client.get_random_model(
        model_id
    )

    return model_id, model