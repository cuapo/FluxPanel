import request from '@/utils/request'

// 查询电子名牌管理列表
export function listManage(query) {
  return request({
    url: '/brand/manage/list',
    method: 'get',
    params: query
  })
}

// 查询电子名牌管理详细
export function getManage(id) {
  return request({
    url: '/brand/manage/getById/' + id,
    method: 'get'
  })
}

// 新增电子名牌管理
export function addManage(data) {
  return request({
    url: '/brand/manage/add',
    method: 'post',
    data: data
  })
}

// 修改电子名牌管理
export function updateManage(data) {
  return request({
    url: '/brand/manage/update',
    method: 'put',
    data: data
  })
}

// 删除电子名牌管理
export function delManage(id) {
  return request({
    url: '/brand/manage/delete/' + id,
    method: 'delete'
  })
}

// 导入电子名牌管理
export function importManage(data) {
    return request({
      url: '/brand/manage/import',
      method: 'post',
      data: data
    })
}

// 根据生产状态从服务器获取MAC地址
export function getMacByStatus(status) {
    return request({
    url: '/mac/pool/getMacByStatus/' + status,
    method: 'get'
  })
}

// 生成电子铭牌二进制文件
export function generate(data) {
  return request({
    url: '/brand/manage/generate',
    method: 'post',
    data: data
  })
}

//
export function checkStatus(){
  return request({
    url: '/brand/manage/checkStatus',
    method: 'post',
    data: data
  })
}