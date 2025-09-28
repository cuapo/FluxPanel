<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">

      <el-form-item label="项目代码" prop="code">
        <el-input
            v-model="queryParams.code"
            placeholder="请输入项目代码"
            clearable
            @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item label="项目描述" prop="desc">
        <el-input
            v-model="queryParams.desc"
            placeholder="请输入项目描述"
            clearable
            @keyup.enter="handleQuery"
        />
      </el-form-item>

      <el-form-item label="制造日期" prop="manufactureDate">
        <el-date-picker clearable
                        v-model="queryParams.manufactureDate"
                        type="date"
                        value-format="YYYY-MM-DD"
                        placeholder="请选择制造日期">
        </el-date-picker>
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
              v-hasPermi="['brand:manage:add']"
          >新增
          </el-button>
          <el-button
              type="success"
              plain
              icon="Edit"
              :disabled="single"
              @click="handleUpdate"
              v-hasPermi="['brand:manage:edit']"
          >修改
          </el-button>
          <el-button
              type="danger"
              plain
              icon="Delete"
              :disabled="multiple"
              @click="handleDelete"
              v-hasPermi="['brand:manage:remove']"
          >删除
          </el-button>
          <el-button
              type="primary"
              plain
              icon="Upload"
              @click="handleImport"
              v-hasPermi="['brand:manage:import']"
          >导入
          </el-button
          >
          <el-button
              type="warning"
              plain
              icon="Download"
              @click="handleExport"
              v-hasPermi="['brand:manage:export']"
          >导出
          </el-button>
        </template>
      </TableSetup>
      <auto-table
          ref="multipleTable"
          class="mytable"
          :tableData="manageList"
          :columns="columns"
          :loading="loading"
          :stripe="stripe"
          :tableHeight="tableHeight"
          @onColumnWidthChange="onColumnWidthChange"
          @onSelectionChange="handleSelectionChange"
      >


        <template #manufactureDate="{ row }">
          <span>{{ parseTime(row.manufactureDate, '{y}-{m}-{d}') }}</span>
        </template>


        <template #status="{ row }">
          <dict-tag :options="produce_status" :value="row.status"/>
        </template>


        <template #updateTime="{ row }">
          <span>{{ parseTime(row.updateTime, '{y}-{m}-{d}') }}</span>
        </template>
        <template #operate="{ row }">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(row)" v-hasPermi="['brand:manage:edit']">
            修改
          </el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(row)" v-hasPermi="['brand:manage:remove']">
            删除
          </el-button>
          <el-button link type="primary" icon="Document" @click="handleGenerate(row)" v-hasPermi="['brand:manage:generate']">
            生成
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

    <!-- 添加或修改电子名牌管理对话框 -->
    <el-dialog :title="title" v-model="open" width="1200px" append-to-body>
      <el-form ref="manageRef" :model="form" :rules="rules" label-width="120px">
        <el-row>
          <el-col :span="12">
            <el-form-item label="项目代码" prop="code">
              <el-input v-model="form.code" placeholder="请输入项目代码"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目描述" prop="desc">
              <el-input v-model="form.desc" placeholder="请输入项目描述"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="6">
            <el-form-item label="标签" prop="tag">
              <el-input v-model="form.tag" type="number" :min="0" placeholder="请输入标签"/>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="pcb版本" prop="pcbVersion">
              <el-input v-model="form.pcbVersion" type="number" :min="1" placeholder="请输入pcb版本"/>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="EEPROM地址" prop="eepromAddr">
              <el-input v-model="form.eepromAddr" placeholder="请输入EEPROM地址"/>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="口令" prop="passwd">
              <el-input
                  v-model="form.passwd"
                  :type="data.showPassword ? 'text' : 'password'"
                  @focus="data.showPassword = true"
                  @blur="data.showPassword = false"
                  placeholder="请输入口令"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="6">
            <el-form-item label="MAC数量" prop="macCount">
              <el-input v-model="form.macCount" readonly placeholder="请输入MAC数量"/>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="制造日期" prop="manufactureDate">
              <el-date-picker clearable
                              v-model="form.manufactureDate"
                              type="date"
                              value-format="YYYY-MM-DD"
                              placeholder="请选择制造日期">
              </el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="序号" prop="serialNum">
              <el-input v-model="form.serialNum" type="number" :min="1" placeholder="请输入序号"/>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="生成数量" prop="generateCount">
              <el-input v-model="form.generateCount" type="number" :min="1" :max="999" placeholder="请输入生成数量"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="12">
            <el-form-item label="MAC地址" prop="macAddress">
              <el-input v-model="form.macAddress" :disabled="data.isMacReadonly" placeholder="请输入MAC地址"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生产状态" prop="status">
              <el-select v-model="form.status" @change="handleStatusChange" placeholder="请选择生产状态">
                <el-option
                    v-for="dict in produce_status"
                    :key="dict.value"
                    :label="dict.label"
                    :value="dict.value"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="MAC地址列表">
          <el-checkbox
              v-model="isAllSelected"
              @change="handleSelectAll"
          >全选
          </el-checkbox>
          <el-checkbox-group v-model="selectedOptions" @change="handleOptionChange">
            <el-row>
              <el-col :span="colSpan"
                      v-for="option in options"
                      :key="option.value"
              >
                <el-checkbox :label="option.value">
                  {{ option.label }}
                </el-checkbox>
              </el-col>
            </el-row>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 添加或修改电子名牌管理对话框 -->
    <el-dialog :title="generateTitle" v-model="generateOpen" width="500px" append-to-body>
      <el-form ref="generateRef" :model="form" label-width="120px">
        <el-tooltip content="输入有效的邮箱地址，将用于接收电子铭牌文件（可不填写）" placement="bottom">
          <el-form-item label="电子邮箱" prop="emailAddress">
            <el-input v-model="form.emailAddress" placeholder="请输入邮箱地址"/>
          </el-form-item>
        </el-tooltip>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="generateForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 导入数据对话框 -->
    <ImportData
        v-if="openImport"
        v-model="openImport"
        tableName="brand_manage"
        @success="handleImportSuccess"
    />
  </div>
</template>

<script setup name="BrandManage">
import {
  addManage,
  checkStatus,
  delManage,
  generate,
  getMacByStatus,
  getManage,
  importManage,
  listManage,
  updateManage
} from "@/api/brand/manage";
import {listAllTable} from '@/api/system/table'
import TableSetup from '@/components/TableSetup'
import AutoTable from '@/components/AutoTable'
import ImportData from '@/components/ImportData'

const {proxy} = getCurrentInstance();
const {produce_status} = proxy.useDict('produce_status');

const manageList = ref([]);
const open = ref(false);
const generateOpen = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");
const generateTitle = ref("");

const columns = ref([])
const stripe = ref(true)
const isTable = ref(true)
const tableHeight = ref(500)
const fullScreen = ref(false)
const openImport = ref(false)
const produceStatus = ref("ES")
// 全选状态
const isAllSelected = ref(false);
const selectedOptions = ref([]);

/** MAC地址校验 */
const validateMacAddress = (rule, value, callback) => {
  if (produceStatus.value === 'MP' || produceStatus.value === 'WS') {
    return callback();
  }
  const macRegex = /^([0-9A-F]{2}-){5}([0-9A-F]{2})$/;
  // 自动格式化输入
  // 移除所有非十六进制字符
  let cleanValue = value.replace(/[^0-9A-Fa-f]/g, '');

  // 转换为大写
  cleanValue = cleanValue.toUpperCase();
  // 限制长度为12个字符
  cleanValue = cleanValue.substring(0, 12);

  // 格式化MAC地址，每2个字符加一个'-'
  let formattedValue = '';
  for (let i = 0; i < cleanValue.length; i++) {
    formattedValue += cleanValue[i];
    if (i % 2 === 1 && i < cleanValue.length - 1) {
      formattedValue += '-';
    }
  }

  if (formattedValue.length > 0 && !macRegex.test(formattedValue)) {
    return callback(new Error('MAC地址格式无效，请使用XX-XX-XX-XX-XX-XX格式'));
  }

  callback();
};

const data = reactive({
  form: {},
  formEmail: {},
  showPassword: false,
  isMacReadonly: false,
  produceStatus: 'ES',
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    code: null,
    desc: null,
    manufactureDate: null,
  },
  rules: {
    code: [
      {required: true, message: "项目代码不能为空", trigger: "blur"}
    ], createBy: [
      {required: true, message: "创建者不能为空", trigger: "blur"}
    ], deptId: [
      {required: true, message: "部门id不能为空", trigger: "blur"}
    ], macAddress: [
      {validator: validateMacAddress, trigger: "change"}
    ], manufactureDate: [
      {required: true, message: "制造日期不能为空", trigger: "blur"}
    ], serialNum: [
      {required: true, message: "序号不能为空", trigger: "blur"}
    ], status: [
      {required: true, message: "生产状态不能为空", trigger: "change"}
    ],
  }
});

// 动态选项数据 - 可以从API获取
const options = reactive([
  {label: 'MAC1', value: 'MAC1'},
  {label: 'MAC2', value: 'MAC2'},
  {label: 'MAC3', value: 'MAC3'},
  {label: 'MAC4', value: 'MAC4'},
  {label: 'MAC5', value: 'MAC5'},
  {label: 'MAC6', value: 'MAC6'},
  {label: 'MAC7', value: 'MAC7'},
  {label: 'MAC8', value: 'MAC8'},
  {label: 'MAC9', value: 'MAC9'},
  {label: 'MAC10', value: 'MAC10'},
  {label: 'MAC11', value: 'MAC11'},
  {label: 'MAC12', value: 'MAC12'},
  {label: 'MAC13', value: 'MAC13'},
  {label: 'MAC14', value: 'MAC14'},
  {label: 'MAC15', value: 'MAC15'},
  {label: 'MAC16', value: 'MAC16'}
]);

const colSpan = 24 / 8;

const {queryParams, form, formEmail, rules} = toRefs(data);

/** 查询电子名牌管理列表 */
function getList() {
  loading.value = true;
  listManage(queryParams.value).then(response => {
    manageList.value = response.rows;
    total.value = response.total;
    loading.value = false;
  });
}

function getColumns() {
  listAllTable({tableName: 'brand_manage'})
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
  generateOpen.value = false;
  reset();
  resetEmail();
}

// 表单重置
function reset() {
  form.value = {
    code: null,
    createBy: null,
    createTime: null,
    delFlag: null,
    deptId: null,
    desc: null,
    eepromAddr: 'FF',
    generateCount: 1,
    id: null,
    macAddress: 'B2-DF-61-00-00-01',
    macCount: 0,
    manufactureDate: new Date(),
    passwd: 'deeab211@psd',
    pcbVersion: 1,
    serialNum: 1,
    status: 'ES',
    tag: 0,
    updateTime: null
  };
  proxy.resetForm("manageRef");
}

function resetEmail() {
  formEmail.value = {
    emailAddress: null
  };
  proxy.resetForm("generateRef");
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

// 处理全选/取消全选
const handleSelectAll = (checked) => {
  if (checked) {
    // 关键修复：使用数组方法确保响应式更新
    selectedOptions.value.splice(0, selectedOptions.value.length,
        ...options.map(option => option.value)
    );
  } else {
    // 取消全选：清空选中数组
    selectedOptions.value.splice(0, selectedOptions.value.length);
  }
  // 更新选中数量
  updateSelectedCount();
};

// 处理选项变化，更新全选状态
const handleOptionChange = (values) => {
  // 当所有选项都被选中时，全选框勾选
  isAllSelected.value = values.length === options.length;
  // 更新选中数量
  updateSelectedCount();
};

// 更新选中数量到输入框
const updateSelectedCount = () => {
  form.value.macCount = selectedOptions.value.length;
};

// 初始检查全选状态
watch(
    () => options.length,
    () => {
      isAllSelected.value = selectedOptions.value.length === options.length;
      updateSelectedCount();
    },
    {immediate: true}
);

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加电子名牌管理";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const brandManageId = row.id || ids.value
  getManage(brandManageId).then(response => {
    form.value = response.data;
    open.value = true;
    title.value = "修改电子名牌管理";
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["manageRef"].validate(valid => {
    if (valid) {
      if (form.value.id != null) {
        updateManage(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          isAllSelected.value = false;
          selectedOptions.value = [];
          getList();
        });
      } else {
        addManage(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          isAllSelected.value = false;
          selectedOptions.value = []
          getList();
        });
      }
    }
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const _ids = row.id || ids.value;
  proxy.$modal.confirm('是否确认删除电子名牌管理编号为"' + _ids + '"的数据项？').then(function () {
    return delManage(_ids);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {
  });
}

/** 导入按钮操作 */
function handleImport() {
  openImport.value = true
}

/** 导出按钮操作 */
function handleExport() {
  proxy.download('brand/manage/export', {
    ...queryParams.value
  }, `manage_${new Date().getTime()}.xlsx`)
}

/** 生成电子铭牌二进制文件按钮操作 */
function handleGenerate(row) {
  resetEmail();
  const brandManageId = row.id || ids.value
  getManage(brandManageId).then(response => {
    form.value = response.data;
    generateOpen.value = true;
    generateTitle.value = "生成电子铭牌二进制文件";
  });
}

/** 生成提交按钮 */
function generateForm() {
  if (form.value.id != null) {
    const id = form.value.id;
    const emailAddress = formEmail.value.emailAddress;
    let data = {
      id: id,
      emailAddress: emailAddress
    }
    generate(data).then(res => {
      proxy.$modal.msgSuccess(res.msg);
      // 如果选择了发送邮件
      if (emailAddress !== '') {
        proxy.$modal.msgSuccess('邮件正在发送中...');
        // 开始轮询检查邮件发送状态
        checkEmailStatus(emailAddress);
      }
      generateOpen.value = false;
      getList();
    });
  }
}

/** 检查邮件发送状态 */
function checkEmailStatus(emailAddress) {
  const maxRetries = 30;  // 最多重试30次
  const retryInterval = 2000;  // 每2秒重试一次
  let retries = 0;

  let data = {
    emailAddress: emailAddress
  }

  const intervalId = setInterval(() => {
    checkStatus(emailAddress).then(res => {
          if (data.status === 'success') {
            clearInterval(intervalId);
            alert('邮件发送成功!');
          } else if (data.status === 'failed') {
            clearInterval(intervalId);
            alert(`邮件发送失败: ${data.error || '未知错误'}`);
          } else {
            // 继续轮询
            retries++;
            if (retries >= maxRetries) {
              clearInterval(intervalId);
              alert('邮件发送超时，请稍后查看邮箱或联系管理员');
            }
          }
        })
        .catch(error => {
          console.error('检查邮件状态时发生错误:', error);
          retries++;
          if (retries >= maxRetries) {
            clearInterval(intervalId);
            alert('检查邮件状态超时，请稍后查看邮箱或联系管理员');
          }
        });
  }, retryInterval);
}

/** 生产状态监听事件 */
function handleStatusChange(status) {
  if (status === 'ES') {
    data.isMacReadonly = false;
    form.value.macAddress = 'B2-DF-61-00-00-01';
  } else {
    data.isMacReadonly = true;
    // 当状态为MP或WS时，从服务器获取MAC地址
    if (status === 'MP' || status === 'WS') {
      produceStatus.value = status;
      fetchMacAddressByStatus(status);
    } else {
      form.value.macAddress = '';
      produceStatus.value = 'ES';
    }
  }
}

/** 根据生产状态从服务器获取MAC地址 */
function fetchMacAddressByStatus(status) {
  getMacByStatus(status).then(response => {
    form.value.macAddress = response.data.macAddress;
  });
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
    tableName: 'brand_manage',
    filedInfo: filedInfo,
    fileName: fileName,
    sheetName: sheetName
  }
  importManage(data).then(() => {
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