<template>
  <!-- Login Form -->
  <div class="flex justify-center items-center mt-20">
    <n-form ref="formRef" :model="formValue" :rules="loginRules" :label-col="{ span: 8 }" :wrapper-col="{ span: 16 }">
      <n-form-item :label="$t('commons.username')" path="username">
        <n-input
          v-model:value="formValue.username"
          :placeholder="$t('tips.pleaseEnterUsername')"
          :input-props="{
            autoComplete: 'username',
          }"
        />
      </n-form-item>
      <n-form-item :label="$t('commons.password')" path="password">
        <n-input
          v-model:value="formValue.password"
          type="password"
          show-password-on="click"
          :placeholder="$t('tips.pleaseEnterPassword')"
          :input-props="{
            autoComplete: 'current-password',
          }"
          @keyup.enter="login"
        />
      </n-form-item>
      <n-form-item wrapper-col="{ span: 16, offset: 8 }">
        <n-button type="primary" :enabled="loading" @click="login">
          {{ $t('commons.login') }}
        </n-button>
      </n-form-item>
      <n-form-item wrapper-col="{ span: 16, offset: 8 }">
        <n-button type="primary" @click="drawer.open('create', null)">
          {{ $t('commons.addUser') }}
        </n-button>
      </n-form-item>
    </n-form>
  </div>
  <n-drawer
    v-if="drawer.show.value"
    v-model:show="drawer.show.value"
    :width="gtsm() ? '50%' : '80%'"
    :placement="'right'"
  >
    <n-drawer-content closable :title="drawer.title.value" :native-scrollbar="false">
      <CreateUserForm v-if="drawer.name.value == 'create'" @save="handleCreateUser" />
      <UpdateUserBasicForm
        v-else-if="drawer.name.value == 'updateBasic'"
        :user="currentUser"
        @save="handleUpdateUserBasic"
      />
      <UpdateUserSettingForm
        v-else-if="drawer.name.value == 'updateSetting'"
        :user="currentUser"
        @save="handleUpdateUserSetting"
      />
    </n-drawer-content>
  </n-drawer>
</template>

<script setup lang="ts">
import { FormInst } from 'naive-ui';
import { FormValidationError } from 'naive-ui/es/form';
import { reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import { LoginData } from '@/api/user';
import { useUserStore } from '@/store';
import { Message } from '@/utils/tips';
import UpdateUserSettingForm from "@/views/admin/components/UpdateUserSettingForm.vue";
import CreateUserForm from "@/views/admin/components/CreateUserForm.vue";
import UpdateUserBasicForm from "@/views/admin/components/UpdateUserBasicForm.vue";

import { Pencil, TrashOutline } from '@vicons/ionicons5';
import { RefreshFilled, SettingsRound } from '@vicons/material';
import { DataTableColumns, NButton, NIcon } from 'naive-ui';
import { h, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { deleteUserApi, getAllUserApi, registerApi, updateUserByIdApi, updateUserSettingApi } from '@/api/user';
import ChatTypeTagInfoCell from '@/components/ChatTypeTagInfoCell.vue';
import { useDrawer } from '@/hooks/drawer';
import { chatStatusMap, UserCreate, UserReadAdmin, UserSettingSchema, UserUpdateAdmin } from '@/types/schema';
import { getCountTrans } from '@/utils/chat';
import { screenWidthGreaterThan } from '@/utils/media';
import { getDateStringSorter } from '@/utils/table';
import { Dialog, Message } from '@/utils/tips';
import { renderUserPerModelCounts } from '@/utils/user';

import CreateUserForm from '../components/CreateUserForm.vue';
import UpdateUserBasicForm from '../components/UpdateUserBasicForm.vue';
import UpdateUserSettingForm from '../components/UpdateUserSettingForm.vue';

const router = useRouter();
const { t } = useI18n();
const userStore = useUserStore();
const formRef = ref<FormInst>();

const gtsm = screenWidthGreaterThan('sm');

const data = ref<Array<UserReadAdmin>>([]);

const currentUser = ref<UserReadAdmin | null>(null);

const formValue = reactive({
  username: '',
  password: '',
});
const loading = ref(false);
const loginRules = {
  username: { required: true, message: t('tips.pleaseEnterUsername'), trigger: 'blur' },
  password: { required: true, message: t('tips.pleaseEnterPassword'), trigger: 'blur' },
};

const login = async () => {
  if (loading.value) return;
  formRef.value
    ?.validate((errors?: Array<FormValidationError>) => {
      if (!errors) {
        loading.value = true;
      }
    })
    .then(async () => {
      try {
        await userStore.login(formValue as LoginData);
        const { redirect } = router.currentRoute.value.query;
        await userStore.fetchUserInfo();
        Message.success(t('tips.loginSuccess'));
        if (redirect) {
          await router.push(redirect as string);
          return;
        }
        await router.push({
          name: userStore.user?.is_superuser ? 'admin' : 'conversation',
        });
        // TODO: 记住密码
      } catch (error) {
        console.log(error);
      } finally {
        loading.value = false;
      }
    });
};

if (userStore.user) {
  router.push({ name: 'conversation' });
}

const refreshData = () => {
  getAllUserApi().then((res) => {
    data.value = res.data;
    Message.success(t('tips.refreshed'));
  });
};

getAllUserApi().then((res) => {
  data.value = res.data;
});

const drawer = useDrawer([
  { name: 'create', title: t('commons.createUser') },
  {
    name: 'updateBasic',
    title: t('commons.updateUserBasic'),
    beforeOpen: (row: UserReadAdmin) => {
      currentUser.value = JSON.parse(JSON.stringify(row));
    },
    afterClose: () => {
      currentUser.value = null;
    },
  },
  {
    name: 'updateSetting',
    title: t('commons.updateUserSetting'),
    beforeOpen: (row: UserReadAdmin) => {
      currentUser.value = JSON.parse(JSON.stringify(row));
    },
    afterClose: () => {
      currentUser.value = null;
    },
  },
]);

const handleCreateUser = (userCreate: UserCreate) => {
  registerApi(userCreate)
    .then(() => {
      Message.success(t('tips.createSuccess'));
      getAllUserApi().then((res) => {
        data.value = res.data;
      });
    })
    .finally(() => {
      drawer.close();
    });
};

const handleUpdateUserBasic = (userUpdate: Partial<UserUpdateAdmin>) => {
  if (!currentUser.value) return;
  if (userUpdate.password === '') {
    delete userUpdate.password;
  }
  updateUserByIdApi(currentUser.value.id, userUpdate)
    .then((res) => {
      Message.success(t('tips.updateSuccess'));
      data.value = data.value.map((item) => {
        if (item.id === res.data.id) {
          return res.data;
        } else {
          return item;
        }
      });
    })
    .finally(() => {
      drawer.close();
    });
};

const handleUpdateUserSetting = (userSetting: Partial<UserSettingSchema>) => {
  if (!currentUser.value) return;
  updateUserSettingApi(currentUser.value.id, userSetting)
    .then((res) => {
      Message.success(t('tips.updateSuccess'));
      data.value = data.value.map((item) => {
        if (item.id === res.data.id) {
          return res.data;
        } else {
          return item;
        }
      });
    })
    .finally(() => {
      drawer.close();
    });
};

const handleDeleteUser = (row: UserReadAdmin) => {
  const d = Dialog.warning({
    title: t('commons.deleteUser'),
    content: t('tips.deleteUserConfirm'),
    positiveText: t('commons.confirm'),
    negativeText: t('commons.cancel'),
    onPositiveClick: () => {
      d.loading = true;
      return new Promise((resolve, reject) => {
        deleteUserApi(row.id)
          .then(() => {
            Message.success(t('tips.deleteUserSuccess'));
            getAllUserApi().then((res) => {
              data.value = res.data;
            });
            resolve(true);
          })
          .catch((err) => {
            Message.error(t('tips.deleteUserFailed') + ': ' + err);
            reject(err);
          })
          .finally(() => {
            d.loading = false;
          });
      });
    },
  });
};
</script>
