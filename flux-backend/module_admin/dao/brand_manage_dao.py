# -*- coding:utf-8 -*-

from typing import List

from sqlalchemy import delete, desc, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.brand_manage_do import BrandManage
from module_admin.entity.vo.brand_manage_vo import BrandManagePageModel, BrandManageModel
from module_gen.constants.gen_constants import GenConstants
from utils.common_util import CamelCaseUtil
from utils.page_util import PageUtil, PageResponseModel


class BrandManageDao:

    @classmethod
    async def get_by_id(cls, db: AsyncSession, brand_manage_id: int) -> BrandManage:
        """根据主键获取单条记录"""
        brand_manage = (((await db.execute(
            select(BrandManage)
            .where(BrandManage.id == brand_manage_id)))
                         .scalars())
                        .first())
        return brand_manage

    """
    查询
    """

    @classmethod
    async def get_brand_manage_list(cls, db: AsyncSession,
                                    query_object: BrandManagePageModel,
                                    data_scope_sql: str = None,
                                    is_page: bool = False) -> [list | PageResponseModel]:

        query = (
            select(BrandManage)
            .where(
                BrandManage.code == query_object.code if query_object.code else True,
                BrandManage.desc == query_object.desc if query_object.desc else True,
                BrandManage.manufacture_date == query_object.manufacture_date if query_object.manufacture_date else True,
                BrandManage.del_flag == '0',
                eval(data_scope_sql) if data_scope_sql else True,
            )
            .order_by(desc(BrandManage.create_time))
            .distinct()
        )
        brand_manage_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)
        return brand_manage_list

    @classmethod
    async def add_brand_manage(cls, db: AsyncSession, add_model: BrandManageModel,
                               auto_commit: bool = True) -> BrandManageModel:
        """
        增加
        """
        brand_manage = BrandManage(**add_model.model_dump(exclude_unset=True, ))
        db.add(brand_manage)
        await db.flush()
        brand_manage_model = BrandManageModel(**CamelCaseUtil.transform_result(brand_manage))
        if auto_commit:
            await db.commit()
        return brand_manage_model

    @classmethod
    async def edit_brand_manage(cls, db: AsyncSession, edit_model: BrandManageModel,
                                auto_commit: bool = True) -> BrandManage:
        """
        修改
        """
        edit_dict_data = edit_model.model_dump(exclude_unset=True, exclude={*GenConstants.DAO_COLUMN_NOT_EDIT})
        await db.execute(update(BrandManage), [edit_dict_data])
        await db.flush()
        if auto_commit:
            await db.commit()
        return await cls.get_by_id(db, edit_model.id)

    @classmethod
    async def del_brand_manage(cls, db: AsyncSession, brand_manage_ids: List[str], soft_del: bool = True,
                               auto_commit: bool = True):
        """
        删除
        """
        if soft_del:
            await db.execute(update(BrandManage).where(BrandManage.id.in_(brand_manage_ids)).values(del_flag='2'))
        else:
            await db.execute(delete(BrandManage).where(BrandManage.id.in_(brand_manage_ids)))
        await db.flush()
        if auto_commit:
            await db.commit()
