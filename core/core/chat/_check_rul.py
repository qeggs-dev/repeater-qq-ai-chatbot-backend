from ...user_config_manager import UserConfigs
from ...global_config_manager import GlobalConfigs

def check_rul(
    fim_mode: bool,
    configs: UserConfigs,
    global_configs: GlobalConfigs,
    save_context: bool | None = None,
) -> bool:
    
    if fim_mode:
        return False
    
    if save_context is None:
        enable_rul = configs.save_context
        if enable_rul is None:
            enable_rul = global_configs.context.save_context
    else:
        enable_rul = save_context
    
    return enable_rul