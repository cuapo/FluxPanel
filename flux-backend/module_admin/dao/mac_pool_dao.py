# -*- coding:utf-8 -*-

from typing import List

from sqlalchemy import delete, desc, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.mac_pool_do import MacPool
from module_admin.entity.vo.mac_pool_vo import MacPoolPageModel, MacPoolModel
from module_gen.constants.gen_constants import GenConstants
from utils.common_util import CamelCaseUtil
from utils.page_util import PageUtil, PageResponseModel


class MacPoolDao:

    @classmethod
    async def get_by_id(cls, db: AsyncSession, mac_pool_id: int) -> MacPool:
        """根据主键获取单条记录"""
        mac_pool = (((await db.execute(
            select(MacPool)
            .where(MacPool.id == mac_pool_id)))
                     .scalars())
                    .first())
        return mac_pool

    @classmethod
    async def get_by_status(cls, db: AsyncSession, status: str) -> MacPool:
        """根据生产状态获取单条记录"""
        mac_pool = (((await db.execute(
            select(MacPool)
            .where(MacPool.used == '0', MacPool.status == status)))
                     .scalars())
                    .first())
        return mac_pool

    @classmethod
    async def get_by_status_macAddress(cls, db: AsyncSession, status: str, macAddress: str) -> MacPool:
        """根据生产状态和mac地址获取单条记录"""
        mac_pool = (((await db.execute(
            select(MacPool)
            .where(MacPool.used == '0', MacPool.status == status, MacPool.mac_address == macAddress)))
                     .scalars())
                    .first())
        return mac_pool

    """
    查询
    """

    @classmethod
    async def get_mac_pool_list(cls, db: AsyncSession,
                                query_object: MacPoolPageModel,
                                data_scope_sql: str = None,
                                is_page: bool = False) -> [list | PageResponseModel]:

        query = (
            select(MacPool)
            .where(
                MacPool.end_time <= query_object.end_time if query_object.end_time else True,
                MacPool.mac_address == query_object.mac_address if query_object.mac_address else True,
                MacPool.serial_sn == query_object.serial_sn if query_object.serial_sn else True,
                MacPool.start_time >= query_object.start_time if query_object.start_time else True,
                MacPool.status == query_object.status if query_object.status else True,
                MacPool.del_flag == '0',
                eval(data_scope_sql) if data_scope_sql else True,
            )
            .order_by(desc(MacPool.create_time))
            .distinct()
        )
        mac_pool_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)
        return mac_pool_list

    @classmethod
    async def add_mac_pool(cls, db: AsyncSession, add_model: MacPoolModel, auto_commit: bool = True) -> MacPoolModel:
        """
        增加
        """
        mac_pool = MacPool(**add_model.model_dump(exclude_unset=True, ))
        db.add(mac_pool)
        await db.flush()
        mac_pool_model = MacPoolModel(**CamelCaseUtil.transform_result(mac_pool))
        if auto_commit:
            await db.commit()
        return mac_pool_model

    @classmethod
    async def edit_mac_pool(cls, db: AsyncSession, edit_model: MacPoolModel, auto_commit: bool = True) -> MacPool:
        """
        修改
        """
        edit_dict_data = edit_model.model_dump(exclude_unset=True, exclude={*GenConstants.DAO_COLUMN_NOT_EDIT})
        await db.execute(update(MacPool), [edit_dict_data])
        await db.flush()
        if auto_commit:
            await db.commit()
        return await cls.get_by_id(db, edit_model.id)

    @classmethod
    async def del_mac_pool(cls, db: AsyncSession, mac_pool_ids: List[str], soft_del: bool = True,
                           auto_commit: bool = True):
        """
        删除
        """
        if soft_del:
            await db.execute(update(MacPool).where(MacPool.id.in_(mac_pool_ids)).values(del_flag='2'))
        else:
            await db.execute(delete(MacPool).where(MacPool.id.in_(mac_pool_ids)))
        await db.flush()
        if auto_commit:
            await db.commit()

    @classmethod
    async def update_mac_pool(cls, db: AsyncSession, edit_model: MacPoolModel,
                              auto_commit: bool = True) -> None:
        """
            根据特定字段修改品牌管理数据（不返回更新后记录）
        """
        # 排除不需要更新的字段
        edit_dict_data = edit_model.model_dump(
            exclude_unset=True,
            exclude={*GenConstants.DAO_COLUMN_NOT_EDIT}
        )

        # 获取用于用于条件判断的字段值
        condition_status = edit_model.status
        condition_mac_address = edit_model.mac_address

        # 构建更新语句，指定更新条件
        update_stmt = update(MacPool).where(
            MacPool.used == '0', MacPool.status == condition_status,
            MacPool.mac_address == condition_mac_address
        ).values(**edit_dict_data)

        await db.execute(update_stmt)
        await db.flush()

        if auto_commit:
            await db.commit()
