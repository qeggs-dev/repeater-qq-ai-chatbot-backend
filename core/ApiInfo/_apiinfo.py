import asyncio
import aiofiles
import orjson
from pathlib import Path
from typing import Dict, List, Optional, Union

from ._apigroup import ApiGroup
from ._exceptions import *

class ApiInfo:
    def __init__(self, CaseSensitive: bool = False):
        self._api_groups: List[ApiGroup] = []
        self._api_types: Dict[str, List[ApiGroup]] = {}
        self._api_names: Dict[str, List[ApiGroup]] = {}
        self._api_baseGroups: Dict[str, List[ApiGroup]] = {}
        self.CaseSensitive = CaseSensitive

    def _create_api_group(self, api_data: dict, model_data: dict) -> ApiGroup:
        """Create an ApiGroup instance from raw data."""
        metadata:dict = api_data.get('Metadata', {})
        if 'Metadata' in model_data:
            metadata.update(model_data.get('Metadata', {}))
        
        return ApiGroup(
            group_name = api_data.get('Name', ''),
            api_key_envname = model_data.get('ApiKeyEnv', api_data.get('ApiKeyEnv', '')),
            model_name = model_data.get('Name', ''),
            url = model_data.get('URL', api_data.get('URL', '')),
            model_id = model_data.get('Id', ''),
            model_type = model_data.get('Type', ''),
            metadata = metadata,
        )

    def _add_api_group(self, api_group: ApiGroup) -> None:
        """Add an ApiGroup to all relevant indexes."""
        self._api_groups.append(api_group)
            
        # Update type index
        if self.CaseSensitive:
            self._api_types.setdefault(api_group.model_type, []).append(api_group)
            self._api_names.setdefault(api_group.model_name, []).append(api_group)
            self._api_baseGroups.setdefault(api_group.group_name, []).append(api_group)
        else:
            self._api_types.setdefault(api_group.model_type.lower(), []).append(api_group)
            self._api_names.setdefault(api_group.model_name.lower(), []).append(api_group)
            self._api_baseGroups.setdefault(api_group.group_name.lower(), []).append(api_group)

    def _parse_api_groups(self, raw_api_groups: List[dict]) -> None:
        """Parse raw API groups data and populate indexes."""
        if not isinstance(raw_api_groups, list):
            raise ValueError('api_groups must be a list')
            
        for api_data in raw_api_groups:
            if not isinstance(api_data, dict):
                raise ValueError('Each API group must be a dictionary')
                
            models = api_data.get('models', [])
            if not isinstance(models, list):
                raise ValueError('models must be a list')
                
            for model_data in models:
                if not isinstance(model_data, dict):
                    raise ValueError('Each model must be a dictionary')
                    
                api_group = self._create_api_group(api_data, model_data)
                self._add_api_group(api_group)
    
    def load(self, path: Path) -> None:
        """Load and parse API groups from a JSON file."""
        try:
            with open(path, 'rb') as f:
                fdata = f.read()
                raw_api_groups: List[dict] = orjson.loads(fdata)
                self._parse_api_groups(raw_api_groups)
        except orjson.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON format: {e}')
        except OSError as e:
            raise IOError(f'Failed to read file: {e}')

    async def load_async(self, path: Path) -> None:
        """Load and parse API groups from a JSON file."""
        try:
            async with aiofiles.open(path, 'rb') as f:
                fdata = await f.read()
                raw_api_groups: List[dict] = await asyncio.to_thread(orjson.loads(fdata))
                await asyncio.to_thread(self._parse_api_groups(raw_api_groups))
        except orjson.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON format: {e}')
        except OSError as e:
            raise IOError(f'Failed to read file: {e}')

    def find_type(self, model_type: str) -> List[ApiGroup]:
        """Find API groups by model type."""
        if not self.CaseSensitive:
            if model_type.lower() in self._api_types:
                return self._api_types[model_type.lower()].copy()
            else:
                raise APIGroupNotFoundError(f'API group not found for model type: {model_type}')
        else:
            if model_type in self._api_types:
                return self._api_types[model_type].copy()
            else:
                raise APIGroupNotFoundError(f'API group not found for model type: {model_type}')
    def find_name(self, model_name: str) -> List[ApiGroup]:
        """Find API groups by model name."""
        if not self.CaseSensitive:
            if model_name.lower() in self._api_names:
                return self._api_names[model_name.lower()].copy()
            else:
                raise APIGroupNotFoundError(f'API group not found for model name: {model_name}')
        else:
            if model_name in self._api_names:
                return self._api_names[model_name].copy()
            else:
                raise APIGroupNotFoundError(f'API group not found for model name: {model_name}')
    
    def find_baseGroup(self, group_name: str) -> List[ApiGroup]:
        """Find API groups by base group name."""
        if not self.CaseSensitive:
            if group_name.lower() in self._api_baseGroups:
                return self._api_baseGroups[group_name.lower()].copy()
            else:
                raise APIGroupNotFoundError(f'API group not found for base group name: {group_name}')
        else:
            if group_name in self._api_baseGroups:
                return self._api_baseGroups[group_name].copy()
            else:
                raise APIGroupNotFoundError(f'API group not found for base group name: {group_name}')
        