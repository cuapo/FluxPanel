import request from '@/utils/request'

// 查询物理地址池列表
export function listPool(query) {
  return request({
    url: '/mac/pool/list',
    method: 'get',
    params: query
  })
}

// 查询物理地址池详细
export function getPool(id) {
  return request({
    url: '/mac/pool/getById/' + id,
    method: 'get'
  })
}

// 新增物理地址池
export function addPool(data) {
  return request({
    url: '/mac/pool/add',
    method: 'post',
    data: data
  })
}

// 修改物理地址池
export function updatePool(data) {
  return request({
    url: '/mac/pool/update',
    method: 'put',
    data: data
  })
}

// 删除物理地址池
export function delPool(id) {
  return request({
    url: '/mac/pool/delete/' + id,
    method: 'delete'
  })
}

// 导入物理地址池
export function importPool(data) {
    return request({
      url: '/mac/pool/import',
      method: 'post',
      data: data
    })
}

// 授权
export function encrypt(data) {
  return request({
    url: '/mac/pool/encrypt',
    method: 'post',
    data: data
  })
}