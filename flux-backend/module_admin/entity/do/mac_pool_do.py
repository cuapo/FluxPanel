# -*- coding:utf-8 -*-

from sqlalchemy import Column, ForeignKey, String, Integer, DateTime
from config.database import BaseMixin, Base

class MacPool(Base, BaseMixin):
    """
    物理地址池表
    """
    __tablename__ = "mac_pool"

    aes = Column(String(255), comment='加密密钥')
    end_time = Column(String(255), comment='结束时间')
    mac_address = Column(String(255), nullable=False, comment='MAC地址')
    serial_sn = Column(String(255), nullable=False, comment='设备SN')
    start_time = Column(String(255), comment='开始时间')
    status = Column(String(20), nullable=False, comment='生产状态')
    used = Column(String(1), nullable=False, comment='使用状态')


