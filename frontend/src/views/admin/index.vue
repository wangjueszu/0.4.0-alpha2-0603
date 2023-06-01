<template>
  <!-- Vue组件的HTML模板 -->

  <!-- 定义一个有侧边栏的布局组件，高度占满90%的视口高度 -->
  <n-layout has-sider class="h-90vh h-full">
    <!-- 定义侧边栏组件，可以展开和收起，含有触发按钮 -->
    <n-layout-sider
      bordered
      :collapsed="collapsed"
      collapse-mode="width"
      :collapsed-width="64"
      :width="200"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <!-- 定义菜单组件，菜单选项来源于menuOptions，绑定的激活菜单项为activeKey -->
      <n-menu v-model:value="activeKey" :collapsed-width="64" :collapsed-icon-size="22" :options="menuOptions" />
    </n-layout-sider>
    <!-- 定义主体布局，包含滚动条和路由视图 -->
    <n-layout class="m-4">
      <n-scrollbar>
        <!-- 根据路由展示不同的组件 -->
        <router-view v-slot="{ Component, route }">
          <component :is="Component" :key="route.fullPath" />
        </router-view>
      </n-scrollbar>
    </n-layout>
  </n-layout>
</template>


<script setup lang="ts">
  // 引入所需的依赖

  // 引入ionicons5图标
  import { ChatbubbleEllipses, FileTrayFull, InformationCircle } from '@vicons/ionicons5';
  // 引入material图标
  import { SettingsRound, SupervisedUserCircleRound } from '@vicons/material';
  // 引入naive-ui的图标组件
  import { NIcon } from 'naive-ui';
  // 引入Vue 3的必要模块
  import { h, ref, watch } from 'vue';
  // 引入vue-i18n实现国际化
  import { useI18n } from 'vue-i18n';
  // 引入vue-router实现路由管理
  import { useRouter } from 'vue-router';

  // 初始化国际化对象
  const { t } = useI18n();
  // 初始化路由对象
  const router = useRouter();

  // 定义侧边栏折叠状态，使用ref创建响应式对象，默认值为true
  const collapsed = ref(true);
  // 定义当前激活菜单项的key，初始值为当前路由的名字
  const activeKey = ref<string>(router.currentRoute.value.name as string);

  // 定义函数用于渲染图标
  function renderIcon(icon: any) {
    return () => h(NIcon, null, { default: () => h(icon) });
  }



  // 定义菜单选项，包括标签名，key值和图标
  const menuOptions = [
    {
      label: t('commons.systemManagement'), // 使用i18n实现国际化
      key: 'systemManagement',
      icon: renderIcon(InformationCircle), // 使用函数渲染图标
    },
    {
      label: t('commons.userManagement'),
      key: 'userManagement',
      icon: renderIcon(SupervisedUserCircleRound),
    },
    {
      label: t('commons.conversationManagement'),
      key: 'conversationManagement',
      icon: renderIcon(ChatbubbleEllipses),
    },
    {
      label: t('commons.logViewer'),
      key: 'logViewer',
      icon: renderIcon(FileTrayFull),
    },
    {
      label: t('commons.configManager'),
      key: 'configManagement',
      icon: renderIcon(SettingsRound),
    },
  ];

  // 使用watch监听activeKey的变化，当activeKey变化时，跳转到对应的路由
  watch(
    async () => activeKey.value,
    (_newName: any) => {
      router.push({ name: activeKey.value });
    }
  );
</script>

