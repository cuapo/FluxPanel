# -*- coding:utf-8 -*-
import os

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from config.enums import BusinessType
from config.get_db import get_db
from exceptions.exception import ServiceException
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.data_scope import GetDataScope
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.brand_manage_vo import BrandManagePageModel, BrandManageModel, GenerateModel, \
    EmailStatusModel
from module_admin.entity.vo.import_vo import ImportModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.brand_manage_service import BrandManageService
from module_admin.service.import_service import ImportService
from module_admin.service.login_service import LoginService
from utils.common_util import bytes2file_response
from utils.response_util import ResponseUtil

brandManageController = APIRouter(prefix='/brand/manage', dependencies=[Depends(LoginService.get_current_user)])


@brandManageController.get('/list', dependencies=[Depends(CheckUserInterfaceAuth('brand:manage:list'))])
async def get_brand_manage_list(
        request: Request,
        query_db: AsyncSession = Depends(get_db),
        page_query: BrandManagePageModel = Depends(BrandManagePageModel.as_query),
        data_scope_sql: str = Depends(GetDataScope('BrandManage'))
):
    brand_manage_result = await BrandManageService.get_brand_manage_list(query_db, page_query, data_scope_sql)

    return ResponseUtil.success(model_content=brand_manage_result)


@brandManageController.get('/getById/{brandManageId}',
                           dependencies=[Depends(CheckUserInterfaceAuth('brand:manage:list'))])
async def get_brand_manage_by_id(
        request: Request,
        brandManageId: int,
        query_db: AsyncSession = Depends(get_db),
        data_scope_sql: str = Depends(GetDataScope('BrandManage'))
):
    brand_manage = await BrandManageService.get_brand_manage_by_id(query_db, brandManageId)
    return ResponseUtil.success(data=brand_manage)


@brandManageController.post('/add', dependencies=[Depends(CheckUserInterfaceAuth('brand:manage:add'))])
@Log(title='brand_manage', business_type=BusinessType.INSERT)
async def add_brand_manage(
        request: Request,
        add_model: BrandManageModel,
        query_db: AsyncSession = Depends(get_db),
        current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_model.create_by = current_user.user.user_id
    add_model.dept_id = current_user.user.dept_id
    add_dict_type_result = await BrandManageService.add_brand_manage(query_db, add_model)
    return ResponseUtil.success(data=add_dict_type_result)


@brandManageController.put('/update', dependencies=[Depends(CheckUserInterfaceAuth('brand:manage:edit'))])
@Log(title='brand_manage', business_type=BusinessType.UPDATE)
async def update_brand_manage(
        request: Request,
        edit_model: BrandManageModel,
        query_db: AsyncSession = Depends(get_db),
        current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_dict_type_result = await BrandManageService.update_brand_manage(query_db, edit_model)
    return ResponseUtil.success(data=add_dict_type_result)


@brandManageController.delete('/delete/{brandManageIds}',
                              dependencies=[Depends(CheckUserInterfaceAuth('brand:manage:del'))])
@Log(title='brand_manage', business_type=BusinessType.DELETE)
async def del_brand_manage(
        request: Request,
        brandManageIds: str,
        query_db: AsyncSession = Depends(get_db),
        current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    ids = brandManageIds.split(',')
    del_result = await BrandManageService.del_brand_manage(query_db, ids)
    return ResponseUtil.success(data=del_result)


@brandManageController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('brand:manage:export'))])
@Log(title='brand_manage', business_type=BusinessType.EXPORT)
async def export_brand_manage(
        request: Request,
        brand_manage_form: BrandManagePageModel = Form(),
        query_db: AsyncSession = Depends(get_db),
        data_scope_sql: str = Depends(GetDataScope('BrandManage')),
):
    # 获取全量数据
    export_result = await BrandManageService.export_brand_manage_list(
        query_db, brand_manage_form, data_scope_sql
    )
    return ResponseUtil.streaming(data=bytes2file_response(export_result))


@brandManageController.post('/import', dependencies=[Depends(CheckUserInterfaceAuth('brand:manage:import'))])
async def import_brand_manage(request: Request,
                              import_model: ImportModel,
                              query_db: AsyncSession = Depends(get_db),
                              current_user: CurrentUserModel = Depends(LoginService.get_current_user)
                              ):
    """
    导入数据
    """
    await ImportService.import_data(query_db, import_model, current_user)
    return ResponseUtil.success()


@brandManageController.post('/generate', dependencies=[Depends(CheckUserInterfaceAuth('brand:manage:generate'))])
async def generate_nvm(
        request: Request,
        generate_model: GenerateModel,
        query_db: AsyncSession = Depends(get_db),
        current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    generate_nvm_result = await BrandManageService.generate_nvm(query_db, generate_model)
    return ResponseUtil.success(msg=generate_nvm_result.message)


# 检查邮件发送状态API路由
@brandManageController.post("/checkStatus")
async def check_email_status(
        request: Request,
        status_model: EmailStatusModel,
):
    try:
        # 获取请求数据
        email_address = status_model.email_address

        if not email_address:
            raise ServiceException(message='邮箱地址是必填项')

        # 读取邮件状态文件
        status_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tmp', 'email_status.json')
        if not os.path.exists(status_file):
            return ResponseUtil.success(data='pending')

        import json
        with open(status_file, 'r') as f:
            status_data = json.load(f)

        # 检查是否是请求的邮箱地址
        if status_data.get('email_address') != email_address:
            return ResponseUtil.success(data='pending')

        return ResponseUtil.success(data=status_data.get('status'), msg=status_data.get('error'))
    except Exception as e:
        print(f"检查邮件状态异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise ServiceException(message=f"检查邮件状态失败: {str(e)}")
