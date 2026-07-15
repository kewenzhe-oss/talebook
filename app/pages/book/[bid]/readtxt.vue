<template>
    <div id="txt-main" :class="mainStore.theme === 'dark' ? 'v-theme--dark' : 'v-theme--light'">
        <v-navigation-drawer
            v-model="sidebar"
            :order="1"
            width="240"
            :theme="mainStore.theme"
        >
            <v-list-subheader
                class="d-flex align-center px-4"
                style="height: 48px; font-size: 14px; font-weight: 500;"
            >
                {{ name }}
            </v-list-subheader>
            <v-virtual-scroll
                style="height: calc(100% - 48px)"
                :items="content"
                :item-height="48"
            >
                <template #default="{ item, index }">
                    <v-list-item
                        :key="item.title"
                        :active="selected === index"
                        color="primary"
                        @click="getNovelContent(index)"
                    >
                        <v-list-item-title style="font-size: 13px; font-weight: 500;">
                            {{ item.title }}
                        </v-list-item-title>
                    </v-list-item>
                </template>
            </v-virtual-scroll>
        </v-navigation-drawer>

        <v-app-bar
            class="px-0"
            :color="mainStore.theme === 'light' ? 'blue' : undefined"
            density="compact"
            :theme="mainStore.theme"
        >
            <v-app-bar-nav-icon @click.stop="sidebar = !sidebar" />
            <v-toolbar-title
                class="ml-2 mr-4 align-center"
                style="cursor: pointer"
                @click="router.push('/')"
            >
                {{ name }}
            </v-toolbar-title>
            <v-spacer />
            <!-- 主题切换按钮 -->
            <v-btn
                icon
                @click="toggleTheme"
            >
                <v-icon>{{ mainStore.theme === 'light' ? 'mdi-weather-night' : 'mdi-weather-sunny' }}</v-icon>
            </v-btn>
            <!-- 多语言切换入口 -->
            <v-menu
                offset-y
                right
            >
                <template #activator="{ props }">
                    <v-btn
                        v-bind="props"
                        icon
                    >
                        <v-icon>mdi-translate</v-icon>
                    </v-btn>
                </template>
                <v-list min-width="240">
                    <v-list-item
                        v-for="localeItem in allLocales"
                        :key="localeItem.code"
                        :active="localeItem.code === locale"
                        @click="setLocale(localeItem.code)"
                    >
                        <template #prepend>
                            <v-icon v-if="localeItem.code === locale">
                                mdi-check
                            </v-icon>
                            <v-icon v-else>
                                mdi-translate
                            </v-icon>
                        </template>
                        <v-list-item-title>{{ localeItem.name }}</v-list-item-title>
                    </v-list-item>
                </v-list>
            </v-menu>

            <!-- 用户头像菜单（登录状态） -->
            <template v-if="mainStore.user.is_login">
                <v-menu
                    offset-y
                    right
                >
                    <template #activator="{ props }">
                        <v-btn
                            v-bind="props"
                            class="mr-4"
                            icon
                            size="45"
                            variant="outlined"
                        >
                            <v-avatar
                                size="32"
                                :image="mainStore.user.avatar"
                            />
                        </v-btn>
                    </template>
                    <v-list min-width="240">
                        <v-list-item>
                            <template #prepend>
                                <v-avatar
                                    size="40"
                                    :image="mainStore.user.avatar"
                                />
                            </template>
                            <v-list-item-title> {{ mainStore.user.nickname }} </v-list-item-title>
                            <v-list-item-subtitle> {{ mainStore.user.email }} </v-list-item-subtitle>
                        </v-list-item>
                        <v-divider class="my-2" />
                        <v-list-item
                            to="/user/detail"
                            :title="t('messages.userCenter')"
                            prepend-icon="mdi-account-box"
                        />
                        <v-list-item
                            to="/user/history"
                            :title="t('messages.readingHistory')"
                            prepend-icon="mdi-history"
                        />
                        <v-list-item
                            v-if="mainStore.sys.allow.FEEDBACK"
                            target="_blank"
                            :href="mainStore.sys.FEEDBACK_URL"
                            :title="t('messages.feedback')"
                            prepend-icon="mdi-message-alert"
                        />
                        <v-divider />
                        <template v-if="mainStore.user.is_admin">
                            <v-list-item
                                to="/admin/settings"
                                :title="t('messages.adminEntry')"
                            >
                                <template #prepend>
                                    <v-icon color="red">
                                        mdi-console
                                    </v-icon>
                                </template>
                            </v-list-item>
                        </template>
                        <v-list-item
                            to="/logout"
                            :title="t('messages.logout')"
                            prepend-icon="mdi-exit-to-app"
                        />
                    </v-list>
                </v-menu>
            </template>
            <!-- 登录按钮（未登录状态） -->
            <template v-else>
                <v-btn
                    class="px-xs-1 login-btn mr-4"
                    to="/login"
                    color="#304ffe"
                    variant="elevated"
                >
                    <v-icon
                        class="d-none d-sm-flex me-0"
                        size="24"
                    >
                        mdi-account-circle
                    </v-icon> {{ t('messages.pleaseLogin') }}
                </v-btn>
            </template>
        </v-app-bar>

        <div class="content-area">
            <v-container>
                <div
                    v-if="!inited"
                    class="study-txt-prep pa-8 rounded-lg text-center mx-auto mt-12"
                    style="max-width: 420px; border: 1px solid rgba(var(--v-theme-on-surface), 0.08); background-color: rgb(var(--v-theme-surface));"
                >
                    <div class="tb-book-icon-wrap mb-5 text-grey-darken-2">
                        <svg viewBox="0 0 24 24" style="width: 42px; height: 42px; fill: none; stroke: currentColor; stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; display: inline-block;">
                            <path d="M12 21c-1.2-1.2-3.2-1.5-4.8-1.5H3v-13h4.2c1.2 0 2.8.3 3.8 1.5M12 21c1.2-1.2 3.2-1.5 4.8-1.5H21v-13h-4.2c-1.2 0-2.8.3-3.8 1.5M12 8v13" />
                        </svg>
                    </div>
                    <div class="text-subtitle-1 font-weight-bold mb-2 text-grey-darken-4" style="letter-spacing: 0.02em;">
                        {{ tip.title }}
                    </div>
                    <div class="text-body-2 text-grey-darken-1 mb-4" style="line-height: 1.6; letter-spacing: 0.01em;">
                        {{ tip.content }}
                    </div>
                    <v-progress-linear
                        color="grey-darken-1"
                        indeterminate
                        height="2"
                        class="mx-auto rounded-pill"
                        style="max-width: 160px;"
                    />
                </div>
                <div v-else>
                    <div
                        v-if="loading"
                        class="d-flex flex-column align-center justify-center py-12 text-center"
                        style="color: rgba(var(--v-theme-on-surface), 0.6);"
                    >
                        <v-progress-linear
                            color="grey-darken-1"
                            indeterminate
                            height="1"
                            class="mb-4 rounded-pill"
                            style="max-width: 100px;"
                        />
                        <span class="text-caption" style="letter-spacing: 0.05em;">正在調取書頁...</span>
                    </div>
                    <div
                        v-show="!loading"
                        class="novel-content"
                        v-html="novelContent"
                    />
                    <div
                        v-show="novelContent && !loading"
                        class="d-flex justify-space-between mt-4"
                    >
                        <v-btn
                            color="info"
                            elevation="0"
                            :disabled="selected===0"
                            @click="getNovelContent(selected-1)"
                        >
                            {{ t('book.previousChapter') }}
                        </v-btn>
                        <v-btn
                            v-show="!sidebar"
                            variant="outlined"
                            elevation="0"
                            @click="sidebar=true"
                        >
                            {{ t('book.tableOfContents') }}
                        </v-btn>
                        <v-btn
                            color="primary"
                            elevation="0"
                            :disabled="selected===content.length-1"
                            @click="getNovelContent(selected+1)"
                        >
                            {{ t('book.nextChapter') }}
                        </v-btn>
                    </div>
                </div>
                <app-footer v-if="mainStore.nav" />
            </v-container>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { useMainStore } from '@/stores/main';
import AppFooter from '~/components/AppFooter.vue';

const { locale, locales, setLocale } = useI18n();

const allLocales = computed(() => {
    return locales.value || [];
});

function toggleTheme() {
    mainStore.toggleTheme();
}

definePageMeta({
    layout: 'blank'
});

const route = useRoute();
const router = useRouter();
const mainStore = useMainStore();
const { $backend } = useNuxtApp();

const bookid = route.params.bid;
const sidebar = ref(false);
const content = ref([]);
const inited = ref(false);
const wait = ref(0);
const name = ref(null);
const novelContent = ref('');
const selected = ref(-1);
const loading = ref(true);
const { t } = useI18n();
const tip = reactive({
    title: t('messages.parsing'),
    content: t('messages.parsingContent')
});

let intvl = null;

onMounted(() => {
    mainStore.setNavbar(false);
    // 获取用户信息
    $backend('/user/info').then((rsp) => {
        if (rsp.err === 'ok') {
            mainStore.login(rsp);
        }
    });
    init();
});

onUnmounted(() => {
    if (intvl) clearInterval(intvl);
});

const init = () => {
    loading.value = true;
    $backend(`/book/txt/init?id=${bookid}&test=0`)
        .then(rsp => {
            if (rsp.err !== 'ok') {
                tip.title = t('messages.error');
                tip.content = rsp.msg;
                return;
            }
            if (rsp.msg === '已解析') {
                inited.value = true;
                content.value = rsp.data.content;
                name.value = rsp.data.name;
                getNovelContent(0);
            } else {
                wait.value = parseInt(rsp.data.wait);
                let queLen = parseInt(rsp.data.que);
                name.value = rsp.data.name;
                if (queLen > 0) {
                    tip.title = t('book.inQueue');
                    tip.content = t('book.queueMessage', { count: queLen });
                    return;
                }
                intvl = setInterval(() => {
                    wait.value--;
                    tip.content = t('book.parsingMessage', { seconds: wait.value });
                    if (wait.value <= 0) {
                        clearInterval(intvl);
                        tip.content = t('book.timeoutMessage');
                        tip.title = t('book.parseTimeout');
                        return;
                    }
                    if (wait.value % 5 !== 0) return;
                    $backend(`/book/txt/init?id=${bookid}&test=1`,)
                        .then(res => {
                            if (res.err === 'ok' && res.msg === '已解析') {
                                inited.value = true;
                                content.value = res.data.content;
                                name.value = res.data.name;
                                getNovelContent(0);
                                clearInterval(intvl);
                            }
                        });
                }, 1000);
            }
        }).finally(() => {
            loading.value = false;
        });
};

const getNovelContent = (i) => {
    if (selected.value === i) return;
    selected.value = i;
    const {title, start, end} = {...content.value[i]};
    loading.value = true;
    // console.log(title, start, end)
    $backend(`/read/txt?id=${bookid}&start=${start}&end=${end}`)
        .then(res => {
            if (res.err !== 'ok') {
                novelContent.value = t('book.contentError') + res.msg;
                return;
            }
            novelContent.value = `<h3>${title}</h3><br>${res.content}`;
        }).finally(() => {
            loading.value = false;
            if (process.client) {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
};
</script>

<style scoped>
#txt-main {
    background-color: #f5f5f5;
    min-height: 100vh;
}

#txt-main.v-theme--dark {
    background-color: #121212;
}

.content-area {
    color: #333;
}

#txt-main.v-theme--dark .content-area {
    color: #e0e0e0;
}

.novel-content {
    word-wrap: break-word;
    line-height: 1.8;
}

#txt-main.v-theme--dark .novel-content :deep(h3) {
    color: #e0e0e0;
}

#txt-main.v-theme--dark .novel-content :deep(p) {
    color: #e0e0e0;
}
</style>
