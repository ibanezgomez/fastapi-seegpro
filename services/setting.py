from sqlalchemy import select
from typing import Any, Dict
from models.setting import SettingModel
from utils.session import SessionFactory
from services.base import BaseDataManager, BaseService

class SettingServiceLocal():
    def get_settings(self) -> Dict[str, Any]:
        data = SettingDataManager(session=SessionFactory()).get_settings()
        results = {}
        for d in data: results[d.id] = d.convert_setting()
        return results

class SettingService(BaseService):
    def get_setting(self, id: str) -> Any:
        setting = SettingDataManager(session=self.session).get_setting(id=id)
        if setting: return setting.convert_setting()
        else:       return None

class SettingDataManager(BaseDataManager):
    def get_setting(self, **kwargs) -> SettingModel:
        stmt = select(SettingModel).filter_by(**kwargs)
        model = self.get_one(stmt)
        return model
    
    def get_settings(self, **kwargs) -> SettingModel:
        model = self.get_all(select(SettingModel))
        return model
