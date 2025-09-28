# -*- coding:utf-8 -*-

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime
from config.database import BaseMixin, Base

class BrandManage(Base, BaseMixin):
    """
    电子名牌管理表
    """
    __tablename__ = "brand_manage"

    code = Column(String(255), nullable=False, comment='项目代码')
    desc = Column(String(255), comment='项目描述')
    eeprom_addr = Column(String(255), comment='EEPROM地址')
    generate_count = Column(Integer, comment='生成数量')
    mac_address = Column(String(255), nullable=False, comment='mac地址')
    mac_count = Column(Integer, comment='mac数量')
    manufacture_date = Column(String(255), nullable=False, comment='制造日期')
    passwd = Column(String(255), comment='口令')
    pcb_version = Column(Integer, comment='pcb版本')
    serial_num = Column(Integer, nullable=False, comment='序号')
    status = Column(String(20), nullable=False, comment='生产状态')
    tag = Column(Integer, comment='标签')


