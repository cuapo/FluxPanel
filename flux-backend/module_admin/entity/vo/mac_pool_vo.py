# -*- coding:utf-8 -*-
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing import List, Literal, Optional, Union
from module_admin.annotation.pydantic_annotation import as_query


class MacPoolModel(BaseModel):
    """
    表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    aes: Optional[str] = Field(default=None, description='加密密钥')
    create_by: Optional[int] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    del_flag: Optional[str] = Field(default=None, description='删除标志')
    dept_id: Optional[int] = Field(default=None, description='部门id')
    end_time: Optional[str] = Field(default=None, description='结束时间')
    id: Optional[int] = Field(default=None, description='id')
    mac_address: Optional[str] = Field(default=None, description='MAC地址')
    serial_sn: Optional[str] = Field(default=None, description='设备SN')
    start_time: Optional[str] = Field(default=None, description='开始时间')
    status: Optional[str] = Field(default=None, description='生产状态')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    used: Optional[str] = Field(default=None, description='使用状态')


class EncryptMacPoolModel(BaseModel):
    """
    表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    id: Optional[int] = Field(default=None, description='id')
    start_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


@as_query
class MacPoolPageModel(MacPoolModel):
    """
    分页查询模型
    """
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
