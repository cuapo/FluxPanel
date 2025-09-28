<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="80px">

      <el-form-item label="设备SN" prop="serialSn">
        <el-input
            v-model="queryParams.serialSn"
            placeholder="请输入设备SN"
            clearable
            @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item label="MAC地址" prop="macAddress">
        <el-input
            v-model="queryParams.macAddress"
            placeholder="请输入MAC地址"
            clearable
            @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item label="开始时间" prop="startTime">
        <el-date-picker clearable
                        v-model="queryParams.startTime"
                        type="date"
                        value-format="YYYY-MM-DD"
                        placeholder="请选择开始时间">
        </el-date-picker>
      </el-form-item>

      <el-form-item label="结束时间" prop="endTime">
        <el-date-picker clearable
                        v-model="queryParams.endTime"
                        type="date"
                        value-format="YYYY-MM-DD"
                        placeholder="请选择结束时间">
        </el-date-picker>
      </el-form-item>

      <el-form-item label="生产状态" prop="status">
        <el-select
            v-model="queryParams.status"
            placeholder="请选择生产状态"
            style="width: 180px"
            clearable>
          <el-option
              v-for="dict in produce_status"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-card class="base-table" ref="fullTable">
      <TableSetup
          ref="tSetup"
          @onStripe="onStripe"
          @onRefresh="onRefresh"
          @onChange="onChange"
          @onfullTable="onfullTable"
          @onSearchChange="onSearchChange"
          :columns="columns"
          :isTable="isTable"
      >
        <template v-slot:operate>
          <el-button
              type="primary"
              plain
              icon="Plus"
              @click="handleAdd"
              v-hasPermi="['mac:pool:add']"
          >新增
          </el-button>
          <el-button
              type="success"
              plain
              icon="Edit"
              :disabled="single"
              @click="handleUpdate"
              v-hasPermi="['mac:pool:edit']"
          >修改
          </el-button>
          <el-button
              type="danger"
              plain
              icon="Delete"
              :disabled="multiple"
              @click="handleDelete"
              v-hasPermi="['mac:pool:remove']"
          >删除
          </el-button>
          <el-button
              type="primary"
              plain
              icon="Upload"
              @click="handleImport"
              v-hasPermi="['mac:pool:import']"
          >导入
          </el-button
          >
          <el-button
              type="warning"
              plain
              icon="Download"
              @click="handleExport"
              v-hasPermi="['mac:pool:export']"
          >导出
          </el-button>
        </template>
      </TableSetup>
      <auto-table
          ref="multipleTable"
          class="mytable"
          :tableData="poolList"
          :columns="columns"
          :loading="loading"
          :stripe="stripe"
          :tableHeight="tableHeight"
          @onColumnWidthChange="onColumnWidthChange"
          @onSelectionChange="handleSelectionChange"
      >


        <template #endTime="{ row }">
          <span>{{ parseTime(row.endTime, '{y}-{m}-{d}') }}</span>
        </template>


        <template #startTime="{ row }">
          <span>{{ parseTime(row.startTime, '{y}-{m}-{d}') }}</span>
        </template>

        <template #status="{ row }">
          <dict-tag :options="produce_status" :value="row.status"/>
        </template>

        <template #updateTime="{ row }">
          <span>{{ parseTime(row.updateTime, '{y}-{m}-{d}') }}</span>
        </template>

        <template #used="{ row }">
          <dict-tag :options="use_status" :value="row.used"/>
        </template>
        <template #operate="{ row }">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(row)" v-hasPermi="['mac:pool:edit']">
            修改
          </el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(row)" v-hasPermi="['mac:pool:remove']">
            删除
          </el-button>
          <el-button link type="primary" icon="Key" @click="handleEncrypt(row)" v-hasPermi="['mac:pool:encrypt']">
            授权
          </el-button>
        </template>
      </auto-table>
      <div class="table-pagination">
        <pagination
            v-show="total > 0"
            :total="total"
            v-model:page="queryParams.pageNum"
            v-model:limit="queryParams.pageSize"
            @pagination="getList"
        />
      </div>
    </el-card>

    <!-- 添加或修改物理地址池对话框 -->
    <el-dialog :title="title" v-model="open" width="800px" append-to-body>
      <el-form ref="poolRef" :model="form" :rules="rules" label-width="120px">

        <el-form-item label="序列号" prop="serialSn">
          <el-input v-model="form.serialSn" placeholder="请输入序列号"/>
        </el-form-item>

        <el-form-item label="物理地址" prop="macAddress">
          <el-input v-model="form.macAddress" placeholder="请输入物理地址"/>
        </el-form-item>

        <el-form-item label="开始时间" prop="startTime">
          <el-date-picker clearable
                          v-model="form.startTime"
                          type="date"
                          value-format="YYYY-MM-DD"
                          placeholder="请选择开始时间">
          </el-date-picker>
        </el-form-item>

        <el-form-item label="结束时间" prop="endTime">
          <el-date-picker clearable
                          v-model="form.endTime"
                          type="date"
                          value-format="YYYY-MM-DD"
                          placeholder="请选择结束时间">
          </el-date-picker>
        </el-form-item>

        <el-form-item label="生产状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择生产状态">
            <el-option
                v-for="dict in produce_status"
                :key="dict.value"
                :label="dict.label"
                :value="dict.value"
            ></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="使用状态" prop="used">
          <el-radio-group v-model="form.used">
            <el-radio
                v-for="dict in use_status"
                :key="dict.value"
                :label="dict.value"
            >{{ dict.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>

      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>
    <!-- 导入数据对话框 -->
    <ImportData
        v-if="openImport"
        v-model="openImport"
        tableName="mac_pool"
        @success="handleImportSuccess"
    />
  </div>
</template>

<script setup name="MacPool">
import {addPool, delPool, encrypt, getPool, importPool, listPool, updatePool} from "@/api/mac/pool";
import {listAllTable} from '@/api/system/table'
import TableSetup from '@/components/TableSetup'
import AutoTable from '@/components/AutoTable'
import ImportData from '@/components/ImportData'

const {proxy} = getCurrentInstance();
const {produce_status, use_status} = proxy.useDict('produce_status', 'use_status');

const poolList = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");

const columns = ref([])
const stripe = ref(true)
const isTable = ref(true)
const tableHeight = ref(500)
const fullScreen = ref(false)
const openImport = ref(false)

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    endTime: null,
    macAddress: null,
    serialSn: null,
    startTime: null,
    status: null,
  },
  rules: {
    createBy: [
      {required: true, message: "创建者不能为空", trigger: "blur"}
    ], deptId: [
      {required: true, message: "部门id不能为空", trigger: "blur"}
    ], macAddress: [
      {required: true, message: "MAC地址不能为空", trigger: "blur"}
    ], status: [
      {required: true, message: "生产状态不能为空", trigger: "change"}
    ], used: [
      {required: true, message: "使用状态不能为空", trigger: "change"}
    ]
  }
});

const {queryParams, form, rules} = toRefs(data);

/** 查询物理地址池列表 */
function getList() {
  loading.value = true;
  listPool(queryParams.value).then(response => {
    poolList.value = response.rows;
    total.value = response.total;
    loading.value = false;
  });
}

function getColumns() {
  listAllTable({tableName: 'mac_pool'})
      .then((response) => {
        columns.value = response.data
      })
      .then(() => {
        getList()
      })
}

// 取消按钮
function cancel() {
  open.value = false;
  reset();
}

// 表单重置
function reset() {
  form.value = {
    aes: null,
    createBy: null,
    createTime: null,
    delFlag: null,
    deptId: null,
    endTime: null,
    id: null,
    macAddress: null,
    serialSn: null,
    startTime: null,
    status: null,
    updateTime: null,
    used: '0'
  };
  proxy.resetForm("poolRef");
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm("queryRef");
  handleQuery();
}

// 多选框选中数据
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.id);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加物理地址池";
}

/** 新增按钮操作 */
function handleImport() {
  openImport.value = true
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const macPoolId = row.id || ids.value
  getPool(macPoolId).then(response => {
    form.value = response.data;
    open.value = true;
    title.value = "修改物理地址池";
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["poolRef"].validate(valid => {
    if (valid) {
      if (form.value.id != null) {
        updatePool(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addPool(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const _ids = row.id || ids.value;
  proxy.$modal.confirm('是否确认删除物理地址池编号为"' + _ids + '"的数据项？').then(function () {
    return delPool(_ids);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {
  });
}

/** 导出按钮操作 */
function handleExport() {
  proxy.download('mac/pool/export', {
    ...queryParams.value
  }, `pool_${new Date().getTime()}.xlsx`)
}

/** 授权按钮操作 */
function handleEncrypt(row) {
  const _id = row.id;
  const serialSn = row.serialSn;
  const startTime = row.startTime;
  let endTime = row.endTime;

  if (serialSn === null || serialSn === undefined || serialSn === '') {
    proxy.$modal.msgError('序列号不能为空')
    return;
  }

  if (startTime === null || startTime === undefined || startTime === '') {
    proxy.$modal.msgError('开始时间不能为空')
    return;
  }

  if (endTime === null || endTime === undefined || endTime === '') {
    let data = {
      id: _id,
      startTime: startTime,
      endTime: null
    }
    proxy.$modal.confirm('是否确认授权物理地址池编号为"' + serialSn + '"为永久生效？').then(function () {
      return encrypt(data);
    }).then(() => {
      getList();
      proxy.$modal.msgSuccess("授权成功");
    }).catch(() => {
    });
  } else {
    // 验证截止日期必须晚于起始日期
    if (new Date(endTime) <= new Date(startTime)) {
      proxy.$modal.msgError('结束时间必须晚于开始时间');
      return;
    }
    let data = {
      id: _id,
      startTime: startTime,
      endTime: endTime
    }
    encrypt(data).then(() => {
      getList();
      proxy.$modal.msgSuccess("授权成功");
    }).catch(() => {
    });
  }
}

//表格全屏
function onfullTable() {
  proxy.$refs.tSetup.onFull(proxy.$refs.fullTable.$el)
  fullScreen.value = !fullScreen.value
  updateTableHeight()
}

//表格刷新
function onRefresh() {
  getList()
}

//搜索框显示隐藏
function onSearchChange() {
  showSearch.value = !showSearch.value
}

function onStripe(val) {
  stripe.value = val
}

//改变表头数据
function onChange(val) {
  columns.value = val
}

//改变表格宽度
function onColumnWidthChange(column) {
  proxy.$refs.tSetup.tableWidth(column)
}

//更新表格高度
function updateTableHeight() {
  if (
      proxy.$refs.tSetup &&
      proxy.$refs.queryRef &&
      document.querySelector('.table-pagination')
  ) {
    if (fullScreen.value) {
      tableHeight.value = window.innerHeight - 145
    } else {
      tableHeight.value =
          window.innerHeight -
          proxy.$refs.tSetup.$el.clientHeight -
          proxy.$refs.queryRef.$el.clientHeight -
          document.querySelector('.table-pagination').clientHeight -
          220
    }
  }
}

//导入成功
function handleImportSuccess(sheetName, filedInfo, fileName) {
  let data = {
    tableName: 'mac_pool',
    filedInfo: filedInfo,
    fileName: fileName,
    sheetName: sheetName
  }
  importPool(data).then(() => {
    proxy.$modal.msgSuccess('导入成功')
    openImport.value = false
    getList()
  })
  getList()
}

onMounted(() => {
  updateTableHeight() // 初始化计算高度
  window.addEventListener('resize', updateTableHeight) // 监听窗口大小变化
})

onUnmounted(() => {
  window.removeEventListener('resize', updateTableHeight) // 销毁监听
})

getColumns()

</script>