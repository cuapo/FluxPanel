# -*- coding:utf-8 -*-
import hashlib
import os
import struct
import time
import zlib
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_admin.dao.brand_manage_dao import BrandManageDao
from module_admin.dao.mac_pool_dao import MacPoolDao
from module_admin.entity.vo.brand_manage_vo import BrandManagePageModel, BrandManageModel, GenerateModel
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.mac_pool_vo import MacPoolModel
from module_admin.entity.vo.sys_table_vo import SysTablePageModel
from module_admin.service.sys_table_service import SysTableService
from utils.common_util import CamelCaseUtil, export_list2excel
from utils.nvm_email import NvmEmailUtil
from utils.page_util import PageResponseModel
from utils.string_util import StringUtil


class BrandManageService:
    """
    用户管理模块服务层
    """

    @classmethod
    async def get_brand_manage_list(cls, query_db: AsyncSession, query_object: BrandManagePageModel,
                                    data_scope_sql: str) -> [list | PageResponseModel]:
        brand_manage_list = await BrandManageDao.get_brand_manage_list(query_db, query_object, data_scope_sql,
                                                                       is_page=True)
        return brand_manage_list

    @classmethod
    async def get_brand_manage_by_id(cls, query_db: AsyncSession, brand_manage_id: int) -> BrandManageModel:
        brand_manage = await BrandManageDao.get_by_id(query_db, brand_manage_id)
        brand_manage_model = BrandManageModel(**CamelCaseUtil.transform_result(brand_manage))
        return brand_manage_model

    @classmethod
    async def add_brand_manage(cls, query_db: AsyncSession, query_object: BrandManageModel) -> BrandManageModel:
        brand_manage_model = await BrandManageDao.add_brand_manage(query_db, query_object)
        return brand_manage_model

    @classmethod
    async def update_brand_manage(cls, query_db: AsyncSession, query_object: BrandManageModel) -> BrandManageModel:
        brand_manage = await BrandManageDao.edit_brand_manage(query_db, query_object)
        brand_manage_model = BrandManageModel(**CamelCaseUtil.transform_result(brand_manage))
        return brand_manage_model

    @classmethod
    async def del_brand_manage(cls, query_db: AsyncSession, brand_manage_ids: List[str]):
        await BrandManageDao.del_brand_manage(query_db, brand_manage_ids)

    @classmethod
    async def export_brand_manage_list(cls, query_db: AsyncSession, query_object: BrandManagePageModel,
                                       data_scope_sql) -> bytes:
        brand_manage_list = await BrandManageDao.get_brand_manage_list(query_db, query_object, data_scope_sql,
                                                                       is_page=False)
        filed_list = await SysTableService.get_sys_table_list(query_db, SysTablePageModel(tableName='brand_manage'),
                                                              is_page=False)
        filtered_filed = sorted(filter(lambda x: x["show"] == '1', filed_list), key=lambda x: x["sequence"])
        new_data = []
        for item in brand_manage_list:
            mapping_dict = {}
            for fild in filtered_filed:
                if fild["prop"] in item:
                    mapping_dict[fild["label"]] = item[fild["prop"]]
            new_data.append(mapping_dict)
        binary_data = export_list2excel(new_data)
        return binary_data

    @classmethod
    async def generate_nvm(cls, query_db: AsyncSession, generate_object: GenerateModel):
        brand_manage_id = generate_object.id
        brand_manage = await BrandManageDao.get_by_id(query_db, brand_manage_id)
        brand_manage_model = BrandManageModel(**CamelCaseUtil.transform_result(brand_manage))

        generateCount = int(brand_manage_model.generate_count)
        macCount = brand_manage_model.mac_count
        try:
            file_paths = []
            # 循环生成指定数量的电子铭牌
            for i in range(generateCount):
                # 更新序号
                brand_manage_model.serial_num = brand_manage_model.serial_num + i
                # 获取基础MAC地址
                base_mac_addr = brand_manage_model.mac_address

                # 解析基础MAC地址
                base_mac = [int(part, 16) for part in base_mac_addr.split('-')]
                base_mac_int = base_mac[0] << 40 | base_mac[1] << 32 | base_mac[2] << 24 | base_mac[3] << 16 | base_mac[
                    4] << 8 | base_mac[5]

                current_mac_int = base_mac_int + i * macCount
                # 转换回字符串格式
                new_mac = f"{((current_mac_int >> 40) & 0xff):02X}-{((current_mac_int >> 32) & 0xff):02X}-{((current_mac_int >> 24) & 0xff):02X}-{((current_mac_int >> 16) & 0xff):02X}-{((current_mac_int >> 8) & 0xff):02X}-{current_mac_int & 0xff:02X}"
                brand_manage_model.mac_address = new_mac

                # 调用单个生成方法
                file_path = cls._generate_single_nvm_binary(query_db, brand_manage_model)

                file_paths.append(file_path)

            # 检查是否需要压缩并发送邮件
            email_address = generate_object.email_address
            compress_and_email = StringUtil.is_empty(email_address)
            email_sent = False

            # 如果生成了文件且需要发送邮件，异步发送
            if file_paths and compress_and_email and email_address:
                import threading
                # 获取第一个文件的目录
                first_file_path = file_paths[0]
                file_dir = os.path.dirname(first_file_path)

                # 创建并启动新线程发送邮件
                def send_email_async():
                    try:
                        # 发送邮件
                        email_result = NvmEmailUtil.send_completion_email(file_dir, email_address)
                        # 这里可以记录邮件发送状态到文件或数据库
                        import json
                        status_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tmp',
                                                   'email_status.json')
                        os.makedirs(os.path.dirname(status_file), exist_ok=True)
                        with open(status_file, 'w') as f:
                            json.dump({
                                'email_address': email_address,
                                'status': 'success' if email_result else 'failed',
                                'timestamp': time.time()
                            }, f)
                    except Exception as e:
                        print(f"异步发送邮件失败: {str(e)}")
                        # 记录失败状态
                        status_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tmp',
                                                   'email_status.json')
                        os.makedirs(os.path.dirname(status_file), exist_ok=True)
                        with open(status_file, 'w') as f:
                            json.dump({
                                'email_address': email_address,
                                'status': 'failed',
                                'error': str(e),
                                'timestamp': time.time()
                            }, f)

                # 启动线程
                email_thread = threading.Thread(target=send_email_async)
                email_thread.daemon = True
                email_thread.start()
                # 立即返回，不等待邮件发送完成
                email_sent = True  # 标记为已发送，实际发送结果后续通过轮询获取
            result = dict(is_success=email_sent, message=f"成功生成{generateCount}个电子铭牌二进制文件", result=generateCount)
            return CrudResponseModel(**result)
        except Exception as e:
            print(f"批量生成电子铭牌失败: {str(e)}")
            raise ServiceException(message=f'批量生成电子铭牌失败')

    @classmethod
    def _generate_single_nvm_binary(cls, query_db: AsyncSession, brand_manage_model: BrandManageModel):
        # 解析配置参数
        code = brand_manage_model.code.ljust(32, '\x00')[:32].encode('ascii')
        tag = brand_manage_model.tag
        pcba = brand_manage_model.pcb_version
        addr = int(brand_manage_model.eeprom_addr, 16)
        passwd = brand_manage_model.passwd.ljust(64, '\x00')[:64].encode('ascii')
        mac_address = brand_manage_model.mac_address
        mac_count = int(brand_manage_model.mac_count)
        manufacture_date = brand_manage_model.manufacture_date
        serial_number = int(brand_manage_model.serial_num)
        status = brand_manage_model.status

        # 解析制造日期
        date_parts = manufacture_date.split('-')
        year = int(date_parts[0][2:])  # 取后两位
        month = int(date_parts[1])
        day = int(date_parts[2])

        # 生成序列号: CODEC+年月日+序号(3位)
        serialnum = serial_number & 0xffff  # 限制为16位

        # 创建NVM结构体数据
        nvm_data = bytearray(0x1f0)

        # 填充signature: 'BoardNvm'
        struct.pack_into('8s', nvm_data, 0x00, b'BoardNvm')

        # 填充revision: 0x00010000,v1.0
        struct.pack_into('I', nvm_data, 0x08, 0x00010000)

        # 动态计算size
        size = 0x18f + mac_count * 6
        struct.pack_into('I', nvm_data, 0x10, size)

        # 填充code
        struct.pack_into('32s', nvm_data, 0x14, code)

        # 填充type: 0x0000
        struct.pack_into('H', nvm_data, 0x34, 0x0000)

        # 填充addr
        struct.pack_into('B', nvm_data, 0x36, addr)

        # 填充year, month, day
        struct.pack_into('B', nvm_data, 0x37, year)
        struct.pack_into('B', nvm_data, 0x38, month)
        struct.pack_into('B', nvm_data, 0x39, day)

        # 填充pcba
        struct.pack_into('B', nvm_data, 0x3a, pcba)

        # 填充tag
        struct.pack_into('B', nvm_data, 0x3b, tag)

        # 填充serialnum
        struct.pack_into('H', nvm_data, 0x3c, serialnum)

        # 填充passwd
        passwd_name = passwd.decode('ascii', errors='ignore').strip()
        passwd_name = passwd_name.replace('\x00', '')
        passwd_hash = hashlib.sha256(passwd_name.encode()).hexdigest()
        passwd_hash_str = passwd_hash.ljust(64, '\x00')
        struct.pack_into('64s', nvm_data, 0x3e, passwd_hash_str.encode('ascii'))

        # 填充mac_num
        struct.pack_into('B', nvm_data, 0x18f, mac_count)

        # 生成并填充MAC地址数组
        base_mac = [int(part, 16) for part in mac_address.split('-')]
        current_mac = base_mac[0] << 40 | base_mac[1] << 32 | base_mac[2] << 24 | base_mac[3] << 16 | base_mac[4] << 8 | \
                      base_mac[5]
        sq_current_mac = current_mac

        for i in range(16):
            if i < mac_count:
                mac_offset = 0x190 + i * 6
                for j in range(6):
                    struct.pack_into('B', nvm_data, mac_offset + j, (current_mac >> (40 - j * 8)) & 0xff)
                current_mac += 1
            else:
                mac_offset = 0x190 + i * 6
                for j in range(6):
                    struct.pack_into('B', nvm_data, mac_offset + j, 0x00)

        # 生成文件名
        file_name = f"{mac_count}mac_{mac_address}.bin"

        # 计算并填充checksum
        checksum_data = nvm_data[:size]
        struct.pack_into('I', checksum_data, 0x0c, 0x00000000)
        checksum = zlib.crc32(checksum_data) & 0xFFFFFFFF
        struct.pack_into('I', nvm_data, 0x0c, checksum)

        # 生成文件名和存储路径
        try:
            codec_name = code.decode('ascii', errors='ignore').strip()
            codec_name = codec_name.replace('\x00', '')
            invalid_chars = '<>:"|?*'
            codec_name = ''.join(c for c in codec_name if c not in invalid_chars)
            if not codec_name:
                codec_name = 'DEFAULT'
            date_dir = f"{year:02d}{month:02d}{day:02d}"
            file_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'file',
                                    f"{codec_name}_date_20{date_dir}")
            os.makedirs(file_dir, exist_ok=True)
            file_path = os.path.join(file_dir, file_name)
        except Exception as e:
            print(f"创建目录失败: {str(e)}")
            raise

        # 写入二进制文件
        with open(file_path, 'wb') as f:
            f.write(nvm_data)

        print(f"电子铭牌二进制文件已生成: {file_path}")

        # 更新数据库
        if status != 'ES':
            try:
                # 拼接serial_sn字符串
                serial_sn = f"{codec_name}{date_dir}{serialnum:03d}"
                # 批量更新MAC地址对应的serial_sn
                for i in range(16):
                    if i < mac_count:
                        # 计算当前MAC地址
                        current_mac_int = sq_current_mac + i
                        new_mac = f"{((current_mac_int >> 40) & 0xff):02X}-{((current_mac_int >> 32) & 0xff):02X}-{((current_mac_int >> 24) & 0xff):02X}-{((current_mac_int >> 16) & 0xff):02X}-{((current_mac_int >> 8) & 0xff):02X}-{current_mac_int & 0xff:02X}"
                        mac_pool = MacPoolDao.get_by_status_macAddress(query_db, status, new_mac)
                        if mac_pool:
                            mac_pool_model = MacPoolModel(**CamelCaseUtil.transform_result(mac_pool))
                            mac_pool_model.used = '1'
                            mac_pool_model.serial_sn = serial_sn
                            MacPoolDao.update_mac_pool(query_db, mac_pool_model)
            except Exception as e:
                print(f"更新数据库失败: {str(e)}")

        return file_path
