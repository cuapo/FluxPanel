# -*- coding:utf-8 -*-
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from module_admin.annotation.pydantic_annotation import as_query


class BrandManageModel(BaseModel):
    """
    表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    code: Optional[str] = Field(default=None, description='项目代码')
    create_by: Optional[int] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    del_flag: Optional[str] = Field(default=None, description='删除标志')
    dept_id: Optional[int] = Field(default=None, description='部门id')
    desc: Optional[str] = Field(default=None, description='项目描述')
    eeprom_addr: Optional[str] = Field(default='00', description='EEPROM地址')
    generate_count: Optional[int] = Field(default=1, description='生成数量')
    id: Optional[int] = Field(default=None, description='id')
    mac_address: Optional[str] = Field(default='B2-DF-61-00-00-01', description='mac地址')
    mac_count: Optional[int] = Field(default=1, description='mac数量')
    manufacture_date: Optional[str] = Field(default=datetime.now().strftime('%Y-%m-%d'), description='制造日期')
    passwd: Optional[str] = Field(default=None, description='口令')
    pcb_version: Optional[int] = Field(default=0, description='pcb版本')
    serial_num: Optional[int] = Field(default=1, description='序号')
    status: Optional[str] = Field(default='ES', description='生产状态')
    tag: Optional[int] = Field(default=0, description='标签')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')


class GenerateModel(BaseModel):
    """
    表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    id: Optional[int] = Field(default=None, description='id')
    email_address: Optional[str] = Field(default=None, description='邮箱地址')


class EmailStatusModel(BaseModel):
    """
    表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)
    email_address: Optional[str] = Field(default=None, description='邮箱地址')



@as_query
class BrandManagePageModel(BrandManageModel):
    """
    分页查询模型
    """
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


