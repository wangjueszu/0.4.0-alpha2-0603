<template>
  <div class="mb-4 mt-1 ml-1 flex flex-row space-x-2 justify-between">
    <n-button circle @click="refreshData">  <!-- 创建一个圆形的按钮，点击时调用 refreshData 函数，用于刷新用户数据 -->
      <template #icon>  <!-- 设置按钮的图标 -->
        <n-icon>
          <RefreshFilled />
        </n-icon>
      </template>
    </n-button>
    <n-button type="primary" @click="drawer.open('create', null)">  <!-- 创建一个主要按钮，点击时打开抽屉（Drawer）并显示创建用户的表单 -->
      {{ $t('commons.addUser') }}  <!-- 设置按钮的文本，这里使用了 i18n 国际化 -->
    </n-button>
  </div>
  <n-data-table
    :scroll-x="1600"  <!-- 设置表格的横向滚动距离 -->
    size="small"  <!-- 设置表格的尺寸 -->
    :columns="columns"  <!-- 设置表格的列 -->
    :data="data"  <!-- 设置表格的数据 -->
    :bordered="true"  <!-- 设置表格为带边框的样式 -->
    :pagination="{  <!-- 设置表格的分页 -->
      pageSize: 20,
    }"
  />
  <n-drawer
    v-if="drawer.show.value"  <!-- 如果抽屉需要显示，则渲染这个组件 -->
    v-model:show="drawer.show.value"  <!-- 抽屉的显示状态由 drawer.show.value 控制 -->
    :width="gtsm() ? '50%' : '80%'"  <!-- 设置抽屉的宽度，根据屏幕的宽度选择不同的宽度 -->
    :placement="'right'"  <!-- 设置抽屉从右边滑出 -->
  >
    <n-drawer-content closable :title="drawer.title.value" :native-scrollbar="false">  <!-- 设置抽屉的内容，这里使用了 n-drawer-content 组件 -->
      <CreateUserForm v-if="drawer.name.value == 'create'" @save="handleCreateUser" />  <!-- 如果抽屉需要显示创建用户的表单，则渲染 CreateUserForm 组件，并监听其 save 事件 -->
      <UpdateUserBasicForm
        v-else-if="drawer.name.value == 'updateBasic'"  <!-- 如果抽屉需要显示更新用户基本信息的表单，则渲染 UpdateUserBasicForm 组件 -->
        :user="currentUser"
        @save="handleUpdateUserBasic"
      />
      <UpdateUserSettingForm
        v-else-if="drawer.name.value == 'updateSetting'"  <!-- 如果抽屉需要显示更新用户设置的表单，则渲染 UpdateUserSettingForm 组件 -->
        :user="currentUser"
        @save="handleUpdateUserSetting"
      />
    </n-drawer-content>
  </n-drawer>
</template>

<script setup lang="ts">  //<!-- 使用 Vue 3 的 <script setup>
// 导入所需的库和组件
import { Pencil, TrashOutline } from '@vicons/ionicons5';  // 导入图标
import { RefreshFilled, SettingsRound } from '@vicons/material';  // 导入图标
import { DataTableColumns, NButton, NIcon } from 'naive-ui';  // 导入 naive-ui 的组件
import { h, ref } from 'vue';  // 导入 Vue 的函数
import { useI18n } from 'vue-i18n';  // 导入 i18n 的钩子函数

import { deleteUserApi, getAllUserApi, registerApi, updateUserByIdApi, updateUserSettingApi } from '@/api/user';  // 导入用户相关的 API 函数
import ChatTypeTagInfoCell from '@/components/ChatTypeTagInfoCell.vue';  // 导入自定义的 Vue 组件
import { useDrawer } from '@/hooks/drawer';  // 导入自定义的钩子函数
import { chatStatusMap, UserCreate, UserReadAdmin, UserSettingSchema, UserUpdateAdmin } from '@/types/schema';  // 导入类型定义
import { getCountTrans } from '@/utils/chat';  // 导入工具函数
import { screenWidthGreaterThan } from '@/utils/media';  // 导入工具函数
import { getDateStringSorter } from '@/utils/table';  // 导入工具函数
import { Dialog, Message } from '@/utils/tips';  // 导入工具函数
import { renderUserPerModelCounts } from '@/utils/user';  // 导入工具函数

import CreateUserForm from '../components/CreateUserForm.vue';  // 导入自定义的 Vue 组件
import UpdateUserBasicForm from '../components/UpdateUserBasicForm.vue';  // 导入自定义的 Vue 组件
import UpdateUserSettingForm from '../components/UpdateUserSettingForm.vue';  // 导入自定义的 Vue 组件

// 使用 i18n 钩子函数获取 t 函数，用于实现文本的国际化
const { t } = useI18n();

// 创建一个函数用于检查屏幕的宽度是否大于 'sm'
const gtsm = screenWidthGreaterThan('sm');

// 创建一个响应式引用存储用户数据
const data = ref<Array<UserReadAdmin>>([]);

// 创建一个响应式引用存储当前用户
const currentUser = ref<UserReadAdmin | null>(null);

// 创建一个函数用于获取所有用户的数据并存储在 data 中
const refreshData = () => {
  getAllUserApi().then((res) => {
    data.value = res.data;
    Message.success(t('tips.refreshed'));
  });
};

// 初始化时，调用 refreshData 函数获取所有用户的数据
getAllUserApi().then((res) => {
  data.value = res.data;
});

// 定义表格的列
const columns: DataTableColumns<UserReadAdmin> = [
  // 每一列的定义都包含标题、键、渲染函数等属性
  // 这里的渲染函数用于自定义单元格的内容，例如，为状态列添加国际化，为时间列添加格式化等
  // ...
];

// 使用自定义的钩子函数创建一个抽屉的状态和配置
const drawer = useDrawer([
  // 钩子函数useDrawer接收一个数组参数，数组的每一项定义一个抽屉的状态和配置
  { name: 'create', title: t('commons.createUser') },  // 创建用户的抽屉
  {
    name: 'updateBasic',
    title: t('commons.updateUserBasic'),
    beforeOpen: (row: UserReadAdmin) => {  // 在打开抽屉之前，将当前用户的信息复制到currentUser
      currentUser.value = JSON.parse(JSON.stringify(row));
    },
    afterClose: () => {  // 在关闭抽屉后，将currentUser设置为null
      currentUser.value = null;
    },
  },
  {
    name: 'updateSetting',
    title: t('commons.updateUserSetting'),
    beforeOpen: (row: UserReadAdmin) => {  // 与updateBasic的处理逻辑类似
      currentUser.value = JSON.parse(JSON.stringify(row));
    },
    afterClose: () => {  // 与updateBasic的处理逻辑类似
      currentUser.value = null;
    },
  },
]);

// 定义创建用户的处理函数
const handleCreateUser = (userCreate: UserCreate) => {
  registerApi(userCreate)  // 调用API函数进行注册
    .then(() => {
      Message.success(t('tips.createSuccess'));  // 注册成功后，弹出成功的提示消息
      getAllUserApi().then((res) => {  // 注册成功后，重新获取所有用户的数据
        data.value = res.data;
      });
    })
    .finally(() => {
      drawer.close();  // 不论注册是否成功，最后都关闭抽屉
    });
};

// 定义更新用户基本信息的处理函数
const handleUpdateUserBasic = (userUpdate: Partial<UserUpdateAdmin>) => {
  // 检查当前用户是否存在
  if (!currentUser.value) return;
  // 如果用户没有输入密码，那么删除密码字段
  if (userUpdate.password === '') {
    delete userUpdate.password;
  }
  // 调用API函数更新用户信息
  updateUserByIdApi(currentUser.value.id, userUpdate)
    .then((res) => {
      Message.success(t('tips.updateSuccess'));  // 更新成功后，弹出成功的提示消息
      // 更新成功后，将新的用户信息更新到data中
      data.value = data.value.map((item) => {
        if (item.id === res.data.id) {
          return res.data;
        } else {
          return item;
        }
      });
    })
    .finally(() => {
      drawer.close();  // 不论更新是否成功，最后都关闭抽屉
    });
};

// 定义更新用户设置的处理函数
const handleUpdateUserSetting = (userSetting: Partial<UserSettingSchema>) => {
  // 检查当前用户是否存在
  if (!currentUser.value) return;
  // 调用API函数更新用户设置
  updateUserSettingApi(currentUser.value.id, userSetting)
    .then((res) => {
      Message.success(t('tips.updateSuccess'));  // 更新成功后，弹出成功的提示消息
      // 更新成功后，将新的用户信息更新到data中
      data.value = data.value.map((item) => {
        if (item.id === res.data.id) {
          return res.data;
        } else {
          return item;
        }
      });
    })
    .finally(() => {
      drawer.close();  // 不论更新设置是否成功，最后都关闭抽屉
    });
};

// 定义删除用户的处理函数
const handleDeleteUser = (row: UserReadAdmin) => {
  // 弹出警告对话框，提示用户确认是否删除
  const d = Dialog.warning({
    title: t('commons.deleteUser'),
    content: t('tips.deleteUserConfirm'),
    positiveText: t('commons.confirm'),
    negativeText: t('commons.cancel'),
    onPositiveClick: () => {  // 用户点击确认后的处理函数
      d.loading = true;  // 设置对话框为加载状态
      return new Promise((resolve, reject) => {
        // 调用API函数删除用户
        deleteUserApi(row.id)
          .then(() => {
            Message.success(t('tips.deleteUserSuccess'));  // 删除成功后，弹出成功的提示消息
            // 删除成功后，重新获取所有用户的数据
            getAllUserApi().then((res) => {
              data.value = res.data;
            });
            resolve(true);  // 成功后，解析Promise
          })
          .catch((err) => {  // 捕获错误
            Message.error(t('tips.deleteUserFailed') + ': ' + err);  // 弹出错误提示消息
            reject(err);  // 错误后，拒绝Promise
          })
          .finally(() => {
            d.loading = false;  // 最后，设置对话框为非加载状态
          });
      });
    },
  });
};
</script>`
