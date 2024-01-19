import json
from sqlalchemy.orm import Mapped, mapped_column
from models.base import SQLModel
from utils.enums import SettingType

class SettingModel(SQLModel):
    __tablename__ = 'settings'
    id:         Mapped[str] = mapped_column("id", primary_key=True)
    value:      Mapped[str] = mapped_column("value", nullable=True)
    value_type: Mapped[SettingType] = mapped_column("value_type", nullable=True)

    def __init__(self, id, value):
        self.id = id
        if   type(value) == str:  
            self.value = value
            self.value_type = SettingType.STR
        elif type(value) == int:  
            self.value = str(value)
            self.value_type = SettingType.INT
        elif type(value) == bool: 
            self.value = str(value)
            self.value_type = SettingType.BOOL
        elif type(value) == list: 
            self.value = json.dumps(value)
            self.value_type = SettingType.LIST
        elif type(value) == dict: 
            self.value = json.dumps(value)
            self.value_type = SettingType.DICT
        else:
            self.value = value
            self.value_type = SettingType.STR

    def convert_setting(self):
        if   self.value_type == SettingType.STR:
            return self.value
        elif self.value_type == SettingType.INT:
            return int(self.value)
        elif self.value_type == SettingType.BOOL:
            return eval(self.value)
        elif self.value_type == SettingType.LIST:
            return json.loads(self.value)
        elif self.value_type == SettingType.DICT: 
            return json.loads(self.value)
        else:
            return None