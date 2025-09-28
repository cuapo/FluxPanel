# -*- coding:utf-8 -*-

import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.dao.mac_pool_dao import MacPoolDao
from module_admin.entity.vo.mac_pool_vo import MacPoolPageModel, MacPoolModel, EncryptMacPoolModel
from module_admin.entity.vo.sys_table_vo import SysTablePageModel
from module_admin.service.sys_table_service import SysTableService
from utils.auth_util import AuthUtil
from utils.common_util import CamelCaseUtil, export_list2excel
from utils.page_util import PageResponseModel
from utils.string_util import StringUtil


class MacPoolService:
    """
    用户管理模块服务层
    """

    @classmethod
    async def get_mac_pool_list(cls, query_db: AsyncSession, query_object: MacPoolPageModel, data_scope_sql: str) -> [
        list | PageResponseModel]:
        mac_pool_list = await MacPoolDao.get_mac_pool_list(query_db, query_object, data_scope_sql, is_page=True)
        return mac_pool_list

    @classmethod
    async def get_mac_pool_by_id(cls, query_db: AsyncSession, mac_pool_id: int) -> MacPoolModel:
        mac_pool = await MacPoolDao.get_by_id(query_db, mac_pool_id)
        mac_pool_model = MacPoolModel(**CamelCaseUtil.transform_result(mac_pool))
        return mac_pool_model

    @classmethod
    async def get_mac_pool_by_status(cls, query_db: AsyncSession, status: str) -> MacPoolModel:
        mac_pool = await MacPoolDao.get_by_status(query_db, status)
        if mac_pool:
            mac_pool_model = MacPoolModel(**CamelCaseUtil.transform_result(mac_pool))
        else:
            mac_pool_model = MacPoolModel(**dict())
        return mac_pool_model

    @classmethod
    async def add_mac_pool(cls, query_db: AsyncSession, query_object: MacPoolModel) -> MacPoolModel:
        mac_pool_model = await MacPoolDao.add_mac_pool(query_db, query_object)
        return mac_pool_model

    @classmethod
    async def update_mac_pool(cls, query_db: AsyncSession, query_object: MacPoolModel) -> MacPoolModel:
        mac_pool = await MacPoolDao.edit_mac_pool(query_db, query_object)
        mac_pool_model = MacPoolModel(**CamelCaseUtil.transform_result(mac_pool))
        return mac_pool_model

    @classmethod
    async def del_mac_pool(cls, query_db: AsyncSession, mac_pool_ids: List[str]):
        await MacPoolDao.del_mac_pool(query_db, mac_pool_ids)

    @classmethod
    async def export_mac_pool_list(cls, query_db: AsyncSession, query_object: MacPoolPageModel,
                                   data_scope_sql) -> bytes:
        mac_pool_list = await MacPoolDao.get_mac_pool_list(query_db, query_object, data_scope_sql, is_page=False)
        filed_list = await SysTableService.get_sys_table_list(query_db, SysTablePageModel(tableName='mac_pool'),
                                                              is_page=False)
        filtered_filed = sorted(filter(lambda x: x["show"] == '1', filed_list), key=lambda x: x["sequence"])
        new_data = []
        for item in mac_pool_list:
            mapping_dict = {}
            for fild in filtered_filed:
                if fild["prop"] in item:
                    mapping_dict[fild["label"]] = item[fild["prop"]]
            new_data.append(mapping_dict)
        binary_data = export_list2excel(new_data)
        return binary_data

    @classmethod
    async def encrypt_mac_pool(cls, query_db: AsyncSession, encrypt_object: EncryptMacPoolModel) -> MacPoolModel:
        mac_pool = await MacPoolDao.get_by_id(query_db, encrypt_object.id)
        mac_pool_model = MacPoolModel(**CamelCaseUtil.transform_result(mac_pool))
        serial_sn = mac_pool_model.serial_sn
        # 解析开始日期
        start_time = datetime.datetime.strptime(encrypt_object.start_time, '%Y-%m-%d')
        if StringUtil.is_empty(encrypt_object.end_time):
            expiry_date_str = 'ffffffff'
            expiry_days = 36500
            expiry_datetime = start_time + datetime.timedelta(days=expiry_days)
        else:
            today = datetime.date.today()
            end = datetime.datetime.strptime(encrypt_object.end_time, "%Y-%m-%d").date()
            time_diff = end - today
            expiry_days = time_diff.days
            expiry_datetime = start_time + datetime.timedelta(days=expiry_days)
            expiry_date_str = expiry_datetime.strftime('%Y%m%d')

        # 格式化起始日期（年月日格式）
        start_date_str = start_time.strftime('%Y%m%d')
        # 生成许可证内容（指定格式）
        license_content = f"{start_date_str};{expiry_date_str};{serial_sn}"
        print(f"加密的明文内容: {license_content}")

        # 数据库中的截止日期
        if StringUtil.is_empty(encrypt_object.end_time):
            db_expiry_date = 'ffffffff'
        else:
            db_expiry_date = expiry_datetime.strftime('%Y-%m-%d')
        # 加密许可证内容
        license_key = AuthUtil.encrypt(license_content)
        mac_pool_model.end_time = db_expiry_date
        mac_pool_model.aes = license_key

        mac_pool = await MacPoolDao.edit_mac_pool(query_db, mac_pool_model)
        return mac_pool
