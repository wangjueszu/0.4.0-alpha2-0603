<template>  <!-- Vue组件的HTML模板 -->
  <!-- Login Form -->
  <div class="flex justify-center items-center mt-20">  <!-- 创建一个居中块 -->
    <n-form ref="formRef" :model="formValue" :rules="loginRules" :label-col="{ span: 8 }" :wrapper-col="{ span: 16 }">  <!-- 使用Naive UI的n-form组件创建一个表单 -->
      <n-form-item :label="$t('commons.username')" path="username">  <!-- 创建一个标签为username的表单项 -->
        <n-input
          v-model:value="formValue.username"  <!-- 将input绑定到username -->
          :placeholder="$t('tips.pleaseEnterUsername')"  <!-- 设置输入提示 -->
          :input-props="{  <!-- 设置输入属性 -->
            autoComplete: 'username',  <!-- 设置自动完成为username -->
          }"
        />
      </n-form-item>
      <n-form-item :label="$t('commons.password')" path="password">  <!-- 创建一个标签为password的表单项 -->
        <n-input
          v-model:value="formValue.password"  <!-- 将input绑定到password -->
          type="password"  <!-- 设置输入类型为password -->
          show-password-on="click"  <!-- 设置点击时显示密码 -->
          :placeholder="$t('tips.pleaseEnterPassword')"  <!-- 设置输入提示 -->
          :input-props="{  <!-- 设置输入属性 -->
            autoComplete: 'current-password',  <!-- 设置自动完成为current-password -->
          }"
          @keyup.enter="login"  <!-- 当用户按下回车键时触发login操作 -->
        />
      </n-form-item>
      <n-form-item wrapper-col="{ span: 16, offset: 8 }">  <!-- 创建一个包裹列 -->
        <n-button type="primary" :enabled="loading" @click="login">  <!-- 创建一个按钮，当用户点击时触发login操作 -->
          {{ $t('commons.login') }}
        </n-button>
      </n-form-item>
      <n-form-item wrapper-col="{ span: 16, offset: 8 }">  <!-- 创建一个包裹列 -->
        <n-button type="primary" @click="drawer.open('create', null)">  <!-- 创建一个主要按钮，点击时打开抽屉（Drawer）并显示创建用户的表单 -->
          {{ $t('commons.addUser') }}  <!-- 设置按钮的文本，这里使用了 i18n 国际化 -->
        </n-button>
      </n-form-item>
    </n-form>
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

<script setup lang="ts">  //使用TypeScript编写Vue 3 setup脚本
import { Pencil, TrashOutline } from '@vicons/ionicons5';  // 导入图标
import { RefreshFilled, SettingsRound } from '@vicons/material';  // 导入图标
import { DataTableColumns, NButton, NIcon } from 'naive-ui';  // 导入 naive-ui 的组件
import { h, ref } from 'vue';  // 导入 Vue 的函数
import { FormInst } from 'naive-ui';  //<!-- 导入naive-ui的FormInst -->
import { FormValidationError } from 'naive-ui/es/form';  //<!-- 导入naive-ui的FormValidationError -->
import { reactive, ref } from 'vue';  //<!-- 导入vue的reactive和ref -->
import { useI18n } from 'vue-i18n';  //<!-- 导入vue-i18n的useI18n -->
import { useRouter } from 'vue-router';  //<!-- 导入vue-router的useRouter -->

import { LoginData } from '@/api/user';  //<!-- 导入LoginData类型 -->
import { useUserStore } from '@/store';  //<!-- 导入useUserStore钩子 -->
import { Message } from '@/utils/tips';
import CreateUserForm from "@/views/admin/components/CreateUserForm.vue";  //<!-- 导入Message工具 -->

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

const router = useRouter(); // <!-- 设置路由 -->
const { t } = useI18n();  //<!-- 设置国际化变量 -->
const userStore = useUserStore();  //<!-- 设置用户数据存储 -->
const formRef = ref<FormInst>();  //<!-- 创建表单实例 -->

const formValue = reactive({  //<!-- 创建反应式对象formValue，
  username: '',  //<!-- 初始化用户名字段为空字符串 -->
  password: '',  //<!-- 初始化密码字段为空字符串 -->
});
const loading = ref(false); // <!-- 创建引用变量loading，用于追踪登录操作是否正在进行 -->

const loginRules = {  //<!-- 创建验证规则 -->
  username: { required: true, message: t('tips.pleaseEnterUsername'), trigger: 'blur' }, // <!-- 用户名字段是必需的，且在失去焦点时触发验证 -->
  password: { required: true, message: t('tips.pleaseEnterPassword'), trigger: 'blur' }, // <!-- 密码字段是必需的，且在失去焦点时触发验证 -->
};

const login = async () => { // <!-- 定义login函数 -->
  if (loading.value) return;  //<!-- 如果登录操作正在进行，则不做任何事情 -->
  formRef.value
    ?.validate((errors?: Array<FormValidationError>) => {  //<!-- 验证表单数据 -->
      if (!errors) {
        loading.value = true; // <!-- 如果没有错误，则开始登录操作 -->
      }
    })
    .then(async () => {
      try {
        await userStore.login(formValue as LoginData); // <!-- 执行登录操作 -->
        const { redirect } = router.currentRoute.value.query;
        await userStore.fetchUserInfo(); // <!-- 获取用户信息 -->
        Message.success(t('tips.loginSuccess')); // <!-- 显示登录成功信息 -->
        if (redirect) {
          await router.push(redirect as string);  //<!-- 如果有重定向，则导航到重定向路由 -->
          return;
        }
        await router.push({ // <!-- 否则，根据用户类型导航到适当的路由 -->
          name: userStore.user?.is_superuser ? 'admin' : 'conversation',
        });
        // TODO: 记住密码
      } catch (error) {
        console.log(error); // <!-- 如果操作失败，则记录错误 -->
      } finally {
        loading.value = false;  //<!-- 无论成功还是失败，最后都会将loading设置为false -->
      }
    });
};

if (userStore.user) {
  router.push({ name: 'conversation' }); // <!-- 如果用户已经登录，则自动导航到conversation路由 -->
}

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

</script>
