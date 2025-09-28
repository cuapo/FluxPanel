# -*- coding:utf-8 -*-

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.data_scope import GetDataScope
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.import_vo import ImportModel
from module_admin.entity.vo.mac_pool_vo import MacPoolPageModel, MacPoolModel, EncryptMacPoolModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.import_service import ImportService
from module_admin.service.login_service import LoginService
from module_admin.service.mac_pool_service import MacPoolService
from utils.common_util import bytes2file_response
from utils.response_util import ResponseUtil

macPoolController = APIRouter(prefix='/mac/pool', dependencies=[Depends(LoginService.get_current_user)])


@macPoolController.get('/list', dependencies=[Depends(CheckUserInterfaceAuth('mac:pool:list'))])
async def get_mac_pool_list(
        request: Request,
        query_db: AsyncSession = Depends(get_db),
        page_query: MacPoolPageModel = Depends(MacPoolPageModel.as_query),
        data_scope_sql: str = Depends(GetDataScope('MacPool'))
):
    mac_pool_result = await MacPoolService.get_mac_pool_list(query_db, page_query, data_scope_sql)

    return ResponseUtil.success(model_content=mac_pool_result)


@macPoolController.get('/getById/{macPoolId}', dependencies=[Depends(CheckUserInterfaceAuth('mac:pool:list'))])
async def get_mac_pool_by_id(
        request: Request,
        macPoolId: int,
        query_db: AsyncSession = Depends(get_db),
        data_scope_sql: str = Depends(GetDataScope('MacPool'))
):
    mac_pool = await MacPoolService.get_mac_pool_by_id(query_db, macPoolId)
    return ResponseUtil.success(data=mac_pool)


@macPoolController.get('/getMacByStatus/{status}', dependencies=[Depends(CheckUserInterfaceAuth('mac:pool:list'))])
async def get_mac_pool_by_status(
        request: Request,
        status: str,
        query_db: AsyncSession = Depends(get_db),
        data_scope_sql: str = Depends(GetDataScope('MacPool'))
):
    mac_pool = await MacPoolService.get_mac_pool_by_status(query_db, status)
    return ResponseUtil.success(data=mac_pool)


@macPoolController.post('/add', dependencies=[Depends(CheckUserInterfaceAuth('mac:pool:add'))])
@Log(title='mac_pool', business_type=BusinessType.INSERT)
async def add_mac_pool(
        request: Request,
        add_model: MacPoolModel,
        query_db: AsyncSession = Depends(get_db),
        current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_model.create_by = current_user.user.user_id
    add_model.dept_id = current_user.user.dept_id
    add_dict_type_result = await MacPoolService.add_mac_pool(query_db, add_model)
    return ResponseUtil.success(data=add_dict_type_result)


@macPoolController.put('/update', dependencies=[Depends(CheckUserInterfaceAuth('mac:pool:edit'))])
@Log(title='mac_pool', business_type=BusinessType.UPDATE)
async def update_mac_pool(
        request: Request,
        edit_model: MacPoolModel,
        query_db: AsyncSession = Depends(get_db),
        current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_dict_type_result = await MacPoolService.update_mac_pool(query_db, edit_model)
    return ResponseUtil.success(data=add_dict_type_result)


@macPoolController.delete('/delete/{macPoolIds}', dependencies=[Depends(CheckUserInterfaceAuth('mac:pool:del'))])
@Log(title='mac_pool', business_type=BusinessType.DELETE)
async def del_mac_pool(
        request: Request,
        macPoolIds: str,
        query_db: AsyncSession = Depends(get_db),
        current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    ids = macPoolIds.split(',')
    del_result = await MacPoolService.del_mac_pool(query_db, ids)
    return ResponseUtil.success(data=del_result)


@macPoolController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('mac:pool:export'))])
@Log(title='mac_pool', business_type=BusinessType.EXPORT)
async def export_mac_pool(
        request: Request,
        mac_pool_form: MacPoolPageModel = Form(),
        query_db: AsyncSession = Depends(get_db),
        data_scope_sql: str = Depends(GetDataScope('MacPool')),
):
    # 获取全量数据
    export_result = await MacPoolService.export_mac_pool_list(
        query_db, mac_pool_form, data_scope_sql
    )
    return ResponseUtil.streaming(data=bytes2file_response(export_result))


@macPoolController.post('/import', dependencies=[Depends(CheckUserInterfaceAuth('mac:pool:import'))])
async def import_mac_pool(request: Request,
                          import_model: ImportModel,
                          query_db: AsyncSession = Depends(get_db),
                          current_user: CurrentUserModel = Depends(LoginService.get_current_user)
                          ):
    """
    导入数据
    """
    await ImportService.import_data(query_db, import_model, current_user)
    return ResponseUtil.success()


@macPoolController.post('/encrypt', dependencies=[Depends(CheckUserInterfaceAuth('mac:pool:encrypt'))])
async def encrypt_mac_pool(
        request: Request,
        encrypt_model: EncryptMacPoolModel,
        query_db: AsyncSession = Depends(get_db),
        current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    encrypt_result = await MacPoolService.encrypt_mac_pool(query_db, encrypt_model)
    return ResponseUtil.success(data=encrypt_result)
