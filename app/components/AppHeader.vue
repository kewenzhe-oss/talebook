<template>
    <div>
        <v-app-bar
            class="px-0 border-subtle-b"
            color="surface"
            density="compact"
            :theme="store.theme"
            :order="0"
            flat
        >
            <template
                v-if="btn_search && display.xs.value"
                #extension
            >
                <v-container fluid>
                    <v-form @submit.prevent="do_search">
                        <v-row>
                            <v-col cols="9">
                                <v-text-field
                                    ref="mobile_search"
                                    v-model="search"
                                    class="ma-0 pa-0 custom-header-search"
                                    hide-details
                                    single-line
                                    variant="solo"
                                />
                            </v-col>
                            <v-col cols="3">
                                <v-btn
                                    :theme="store.theme"
                                    rounded
                                    color="primary"
                                    @click="do_mobile_search"
                                >
                                    搜尋
                                </v-btn>
                            </v-col>
                        </v-row>
                    </v-form>
                </v-container>
            </template>
 
            <v-app-bar-nav-icon @click.stop="sidebar = !sidebar" />
            <v-toolbar-title
                class="ml-2 mr-4 align-center"
                style="cursor: pointer"
                @click="router.push('/')"
            >
                <span class="mobile-site-title">{{ store.sys.title }}</span>
            </v-toolbar-title>
 
            <template v-if="display.smAndUp.value && route.path !== '/'">
                <div class="search-wrapper">
                    <v-text-field
                        ref="search_input"
                        v-model="search"
                        flat
                        variant="solo"
                        hide-details
                        prepend-inner-icon="mdi-magnify"
                        name="name"
                        placeholder="搜尋..."
                        class="d-none d-sm-flex search-field custom-header-search"
                        @keyup.enter="do_search"
                    />
                </div>
            </template>

            <v-btn
                v-else-if="route.path !== '/'"
                icon
                class="d-flex d-sm-none"
                @click="btn_search = !btn_search"
            >
                <v-icon>mdi-magnify</v-icon>
            </v-btn>

            <template v-if="err == 'ok'">
                <template v-if="store.user.is_login">
                    <v-menu
                        v-if="messages.length > 0"
                        offset-y
                        right
                        :close-on-content-click="false"
                    >
                        <template #activator="{ props }">
                            <v-btn
                                v-bind="props"
                                icon
                                class="d-none d-sm-inline-flex"
                            >
                                <v-icon>mdi-bell</v-icon>
                            </v-btn>
                        </template>
                        <v-list
                            lines="three"
                            density="compact"
                            width="400"
                        >
                            <v-list-item
                                v-for="(msg, idx) in messages"
                                :key="msg.id"
                            >
                                <template #prepend>
                                    <v-avatar>
                                        <v-icon
                                            v-if="msg.status == 'success'"
                                            size="large"
                                            color="green"
                                        >
                                            mdi-information
                                        </v-icon>
                                        <v-icon
                                            v-else
                                            size="large"
                                            color="red"
                                        >
                                            mdi-alert
                                        </v-icon>
                                    </v-avatar>
                                </template>

                                <v-list-item-title style="white-space: normal; word-break: break-word;">
                                    {{ msg.data.message }}
                                </v-list-item-title>
                                <v-list-item-subtitle>{{ msg.create_time }}</v-list-item-subtitle>

                                <template #append>
                                    <v-btn @click.prevent="hidemsg(idx, msg.id)">
                                        {{ $t('messages.ok') }}
                                    </v-btn>
                                </template>
                            </v-list-item>
                        </v-list>
                    </v-menu>

                    <!-- 主题切换按钮 -->
                    <v-btn
                        icon
                        class="d-none d-sm-inline-flex"
                        @click="toggleTheme"
                    >
                        <v-icon>{{ store.theme === 'light' ? 'mdi-weather-night' : 'mdi-weather-sunny' }}</v-icon>
                    </v-btn>


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
                                    :image="store.user.avatar"
                                />
                            </v-btn>
                        </template>
                        <v-list min-width="240">
                            <v-list-item>
                                <template #prepend>
                                    <v-avatar
                                        size="40"
                                        :image="store.user.avatar"
                                    />
                                </template>
                                <v-list-item-title> {{ store.user.nickname }} </v-list-item-title>
                                <v-list-item-subtitle> {{ store.user.email }} </v-list-item-subtitle>
                            </v-list-item>
                            <v-divider class="my-2" />
                            <v-list-item
                                to="/user/detail"
                                title="個人中心"
                                prepend-icon="mdi-account-box"
                            />
                            <v-list-item
                                to="/user/history"
                                title="閱讀歷史"
                                prepend-icon="mdi-history"
                            />
                            <v-list-item
                                v-if="store.sys.allow.FEEDBACK"
                                target="_blank"
                                :href="store.sys.FEEDBACK_URL"
                                title="問題反映"
                                prepend-icon="mdi-message-alert"
                            />
                            <v-divider />
                            <template v-if="store.user.is_admin">
                                <v-list-item
                                    to="/admin/settings"
                                    title="管理後台"
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
                                title="登出"
                                prepend-icon="mdi-exit-to-app"
                            />
                        </v-list>
                    </v-menu>
                </template>

                <template v-else>
                    <!-- 主题切换按钮（未登录状态） -->
                    <v-btn
                        icon
                        class="d-none d-sm-inline-flex"
                        @click="toggleTheme"
                    >
                        <v-icon>{{ store.theme === 'light' ? 'mdi-weather-night' : 'mdi-weather-sunny' }}</v-icon>
                    </v-btn>

                    <!-- 桌面端显示文字按钮 -->
                    <v-btn
                        class="login-btn mr-4 text-none font-weight-medium d-none d-sm-inline-flex"
                        to="/login"
                        variant="text"
                        :color="store.theme === 'light' ? 'grey-darken-3' : 'grey-lighten-2'"
                    >
                        請登入
                    </v-btn>

                    <!-- 手机端显示简洁登录图标按钮 -->
                    <v-btn
                        class="d-inline-flex d-sm-none mr-2"
                        icon
                        to="/login"
                        aria-label="登入"
                    >
                        <v-icon>mdi-login</v-icon>
                    </v-btn>
                </template>
            </template>
        </v-app-bar>

        <v-navigation-drawer
            v-model="sidebar"
            :order="1"
            width="240"
        >
            <v-list
                v-if="items.length > 0"
                density="compact"
                nav
                color="primary"
            >
                <template
                    v-for="(item, idx) in items"
                    :key="idx"
                >
                    <v-list-subheader v-if="item.heading">
                        {{ item.heading }}
                    </v-list-subheader>

                    <!-- 二级菜单 -->
                    <v-list-group
                        v-else-if="item.groups"
                        :value="item.text"
                    >
                        <template #activator="{ props }">
                            <v-list-item
                                v-bind="props"
                                :prepend-icon="item.icon"
                                :title="item.text"
                            />
                        </template>

                        <v-list-item
                            v-for="link in item.groups"
                            :key="link.href"
                            :to="link.href"
                            :title="link.text"
                            :subtitle="link.subtitle"
                            :prepend-icon="link.icon"
                        />
                    </v-list-group>

                    <!-- 友情链接 -->
                    <template v-else-if="item.links">
                        <v-list-item
                            v-for="(links, cidx) in chunk(item.links, 2)"
                            :key="idx + 'chunk' + cidx"
                            class="nav-links-item"
                        >
                            <v-row no-gutters>
                                <v-col
                                    v-for="link in links"
                                    :key="link.href"
                                    cols="6"
                                    class="nav-link-col"
                                >
                                    <v-btn
                                        v-if="item.target != ''"
                                        variant="text"
                                        target="_blank"
                                        :href="link.href"
                                        class="nav-link-btn"
                                    >
                                        <v-icon
                                            v-if="link.icon"
                                            start
                                        >
                                            {{ link.icon }}
                                        </v-icon> {{ link.text }}
                                    </v-btn>
                                    <v-btn
                                        v-else
                                        variant="text"
                                        :to="link.href"
                                        class="nav-link-btn"
                                    >
                                        <v-icon
                                            v-if="link.icon"
                                            start
                                        >
                                            {{ link.icon }}
                                        </v-icon> {{ link.text }}
                                    </v-btn>
                                </v-col>
                            </v-row>
                        </v-list-item>
                    </template>

                    <!-- 导航菜单 -->
                    <v-list-item
                        v-else
                        :key="item.text"
                        density="compact"
                        :to="item.href"
                        :target="item.target"
                        :title="item.text"
                        :prepend-icon="item.icon"
                    >
                        <template
                            v-if="item.count"
                            #append
                        >
                            <v-chip
                                size="small"
                                variant="outlined"
                            >
                                {{ item.count }}
                            </v-chip>
                        </template>
                    </v-list-item>
                </template>

                <!-- Mobile only configurations (Theme & Notifications) (PR2) -->
                <v-divider class="my-2 d-sm-none" />
                
                <!-- Notification list item inside drawer (with menu dropdown) -->
                <v-menu
                    v-if="messages.length > 0 && store.user.is_login"
                    offset-y
                    :close-on-content-click="false"
                >
                    <template #activator="{ props }">
                        <v-list-item
                            v-bind="props"
                            prepend-icon="mdi-bell"
                            title="系統消息"
                            density="compact"
                            class="d-sm-none"
                        >
                            <template #append>
                                <v-chip
                                    size="small"
                                    color="error"
                                    variant="flat"
                                >
                                    {{ messages.length }}
                                </v-chip>
                            </template>
                        </v-list-item>
                    </template>
                    <v-list
                        lines="three"
                        density="compact"
                        width="280"
                    >
                        <v-list-item
                            v-for="(msg, idx) in messages"
                            :key="msg.id"
                        >
                            <template #prepend>
                                <v-avatar size="24">
                                    <v-icon
                                        v-if="msg.status == 'success'"
                                        size="small"
                                        color="green"
                                    >
                                        mdi-information
                                    </v-icon>
                                    <v-icon
                                        v-else
                                        size="small"
                                        color="red"
                                    >
                                        mdi-alert
                                    </v-icon>
                                </v-avatar>
                            </template>

                            <v-list-item-title style="white-space: normal; word-break: break-word; font-size: 13px !important; font-weight: normal !important;">
                                {{ msg.data.message }}
                            </v-list-item-title>
                            <v-list-item-subtitle style="font-size: 11px !important;">{{ msg.create_time }}</v-list-item-subtitle>

                            <template #append>
                                <v-btn size="x-small" variant="outlined" @click.prevent="hidemsg(idx, msg.id)">
                                    {{ $t('messages.ok') }}
                                </v-btn>
                            </template>
                        </v-list-item>
                    </v-list>
                </v-menu>

                <!-- Theme toggle list item inside drawer -->
                <v-list-item
                    :prepend-icon="store.theme === 'light' ? 'mdi-weather-night' : 'mdi-weather-sunny'"
                    :title="store.theme === 'light' ? '切換深色模式' : '切換淺色模式'"
                    density="compact"
                    class="d-sm-none"
                    @click="toggleTheme"
                />

                <!-- HIDDEN: sidebar extra HTML (QR code etc.) -->
                <v-list-item
                    v-if="false && store.sys.sidebar_extra_html"
                    class="sidebar-extra-item"
                >
                    <div
                        class="sidebar-extra-content press-content"
                        v-html="store.sys.sidebar_extra_html"
                    />
                </v-list-item>
            </v-list>
        </v-navigation-drawer>
    </div>
</template>

<script setup>
import { useDisplay } from 'vuetify';
import { useMainStore } from '@/stores/main';
import { useI18n } from '#i18n';

const store = useMainStore();
const { $backend } = useNuxtApp();
const display = useDisplay();
const router = useRouter();
const route = useRoute();
const { locale, locales, setLocale, t } = useI18n();

const err = ref('');
const visit_admin_pages = ref(false);
const sidebar = ref(null);
const btn_search = ref(false);
const search = ref('');
const messages = ref([]);

const mobile_search = ref(null);
const search_input = ref(null);

// 多语言相关
const availableLocales = computed(() => {
    return (locales.value || []).filter(l => l.code !== locale.value);
});

const allLocales = computed(() => {
    return locales.value || [];
});

const navData = ref(null);

const items = computed(() => {
    var home_links = [
        // home
        { icon: 'mdi-home', href: '/', text: '首頁' },
    ];
    var library_links = [
        // home
        { icon: 'mdi-book', href: '/library', text: '書庫' },
    ];
    var admin_links = [
        {
            icon: 'mdi-cog',
            text: '管理',
            groups: [
                { icon: 'mdi-cog', href: '/admin/settings', text: '設定' },
                { icon: 'mdi-human-greeting', href: '/admin/users', text: '使用者' },
                { icon: 'mdi-library-shelves', href: '/admin/books', text: '書籍' },
                { icon: 'mdi-import', href: '/admin/imports', text: '匯入' },
            ],
        },
    ];

    // Dynamic category navigation (Category-first, no tag buttons)
    var nav_links = [];
    const cats = navData.value?.categories || [];
    const navs = navData.value?.navs || [];

    if (cats.length > 0) {
        // New: BOOK_CATEGORIES exist → render as category groups
        const catIcons = {
            '工作': 'mdi-briefcase',
            '交友': 'mdi-account-group',
            '爱': 'mdi-heart',
        };
        const categoryMap = {
            'philosophy': '哲學與思想',
            'history-politics': '歷史與政治',
            'science-history': '科學史',
            'sociology': '社會學',
            'logic': '邏輯學',
            'business-management': '商業與管理',
            'economics-investment': '經濟與投資',
            'genius-madness': '天才與瘋狂',
            'science': '科學史',
            'history': '歷史與政治',
            'business': '商業與管理',
            'economics': '經濟與投資',
            '科学史': '科學史',
            '天才与疯狂': '天才與瘋狂',
            '社会学': '社會學',
            '逻辑学': '邏輯學',
            '历史与政治': '歷史與政治',
            '商业与管理': '商業與管理',
            '经济与投资': '經濟與投資'
        };
        const catGroups = cats
            .filter(c => c.enabled !== false)
            .map(c => ({
                icon: c.icon || catIcons[c.name] || 'mdi-folder',
                href: '/subject/' + encodeURIComponent(c.id),
                text: categoryMap[c.id] || categoryMap[c.name] || categoryMap[c.name.toLowerCase()] || c.name,
                subtitle: (navData.value?.category_counts?.[c.id] || 0) + ' 本藏書',
            }));
        if (catGroups.length > 0) {
            nav_links.push({
                icon: 'mdi-view-grid',
                text: '分類導航',
                groups: catGroups,
            });
        }
    } else if (navs.length > 0) {
        // Fallback: BOOK_NAV exists → render legend groups as categories (no tag buttons)
        const navGroups = navs
            .filter(n => n.legend !== '其他')
            .map(n => ({
                icon: 'mdi-folder',
                href: '/subject/' + encodeURIComponent(n.legend),
                text: n.legend,
                subtitle: '',
            }));
        if (navGroups.length > 0) {
            nav_links.push({
                icon: 'mdi-view-grid',
                text: '分類導航',
                groups: navGroups,
            });
        }
    }

    // Always show browse-by-metadata group
    nav_links.push({
        icon: 'mdi-dots-horizontal',
        text: '展開全部分類',
        groups: [
            { icon: 'mdi-home-group', href: '/publisher', text: '出版社', subtitle: store.sys.publishers + ' 間' },
            { icon: 'mdi-tag-heart', href: '/tag', text: '標籤', subtitle: store.sys.tags + ' 個' },
            { icon: 'mdi-file', href: '/format', text: '格式', subtitle: store.sys.formats + ' 種' }
        ]
    });

    var friend_links = [
        // links
        { heading: '友情連結' },
        { links: store.sys.friends, target: '_blank' },
    ];
    // HIDDEN: 系统 section (version, user count, OPDS, QR code)
    // var sys_links = [
    //     { heading: $t('messages.system') },
    //     { icon: 'mdi-history', text: $t('messages.systemVersion'), href: '', count: store.sys.version },
    //     { icon: 'mdi-human', text: $t('messages.userCount'), href: '', count: store.sys.users },
    //     { icon: 'mdi-cellphone', text: $t('messages.opdsIntroduction'), href: '/opds-readme', count: 'OPDS', target: '_blank' },
    // ];

    return home_links
        .concat(library_links)
        .concat(store.user.is_admin ? admin_links : [])
        .concat(nav_links)
        .concat(store.sys.friends.length > 0 ? friend_links : []);
    // HIDDEN: sys_links
    // .concat(store.sys.show_sidebar_sys !== false ? sys_links : []);
});

onMounted(() => {
    visit_admin_pages.value = route.path.indexOf('/admin/') == 0;
    sidebar.value = false; // Changed to default off for mobile-first clean view
    $backend('/user/info').then((rsp) => {
        err.value = rsp.err;
        store.login(rsp);
        store.setTitle(rsp.sys.title);
    });
    $backend('/user/messages').then((rsp) => {
        if (rsp.err == 'ok') {
            messages.value = rsp.messages;
        }
    });
    $backend('/book/nav').then((rsp) => {
        if (rsp.err == 'ok') {
            navData.value = rsp;
        }
    });
});

function chunk(arr, len) {
    var e = arr.length;
    var r = [];
    for (var idx = 0; idx < e; idx += len) {
        var n = Math.min(idx + len, e);
        r.push(arr.slice(idx, n));
    }
    return r;
}

function do_mobile_search() {
    if (search.value.trim() != '') {
        router.push('/search?name=' + search.value.trim());
    } else {
        mobile_search.value?.focus();
    }
}

function do_search() {
    if (search.value.trim() != '') {
        router.push('/search?name=' + search.value.trim());
    } else {
        search_input.value?.focus();
    }
}

function hidemsg(idx, msgid) {
    $backend('/user/messages', {
        method: 'POST',
        body: JSON.stringify({ id: msgid }),
    }).then((rsp) => {
        if (rsp.err == 'ok') {
            messages.value.splice(idx, 1);
        }
    });
}

function toggleTheme() {
    store.toggleTheme();
}
</script>

<style scoped>
.search-wrapper {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    width: 40vw;
    max-width: 600px;
    min-width: 250px;
}
.search-field {
    width: 100% !important;
}
.search-field :deep(.v-input__control) {
    width: 100% !important;
}

/* Custom Header Search */
.custom-header-search :deep(.v-field) {
    background-color: var(--bg-muted) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}

.custom-header-search :deep(.v-field__input) {
    color: var(--text-primary) !important;
    padding-top: 6px !important;
    padding-bottom: 6px !important;
    font-size: 14px !important;
}

.custom-header-search :deep(.v-field__input::placeholder) {
    color: var(--text-tertiary) !important;
    opacity: 1 !important;
}

.custom-header-search :deep(.v-icon) {
    color: var(--text-tertiary) !important;
    opacity: 1 !important;
}

/* Focus and hover states */
.custom-header-search :deep(.v-field:hover) {
    border-color: var(--border-strong) !important;
}

.custom-header-search :deep(.v-field--focused) {
    border-color: var(--accent) !important;
    background-color: var(--bg-surface) !important;
    box-shadow: 0 0 0 3px var(--focus-ring) !important;
}

/* Navigation Drawer Override */
:deep(.v-navigation-drawer) {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

/* Sidebar item colors and states */
:deep(.v-navigation-drawer) .v-list-item {
    color: var(--text-secondary) !important;
    border-radius: 8px;
    margin: 4px 8px;
    transition: all 0.2s ease;
}

:deep(.v-navigation-drawer) .v-list-item:hover {
    color: var(--text-primary) !important;
    background-color: var(--bg-muted) !important;
}

/* Sidebar active item */
:deep(.v-navigation-drawer) .v-list-item--active {
    color: var(--accent) !important;
    background-color: var(--accent-soft) !important;
}

:deep(.v-navigation-drawer) .v-list-item--active .v-list-item__prepend > .v-icon {
    color: var(--accent) !important;
    opacity: 1 !important;
}

:deep(.v-navigation-drawer) .v-list-item__prepend > .v-icon {
    color: var(--text-secondary) !important;
    opacity: 0.7 !important;
}

:deep(.v-navigation-drawer) .v-list-item--active:hover {
    background-color: var(--accent-soft) !important;
}

/* Sidebar subheaders */
:deep(.v-navigation-drawer) .v-list-subheader {
    color: var(--text-tertiary) !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding-left: 16px;
    margin-top: 12px;
    margin-bottom: 4px;
}

:deep(.v-navigation-drawer) .v-list-subheader__text {
    font-size: 11px !important;
    font-weight: 600 !important;
}

/* Expand arrows */
:deep(.v-navigation-drawer) .v-list-group__header .v-list-item__append > .v-icon {
    color: var(--text-tertiary) !important;
}

:deep(.v-navigation-drawer) .v-divider {
    border-color: var(--border-subtle) !important;
    opacity: 1 !important;
}

/* Icons, chip, list layout overrides */
:deep(.v-navigation-drawer) .v-list-item-title {
    font-size: 14px !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em;
}

:deep(.v-navigation-drawer) .v-list-item--density-compact .v-list-item-title {
    font-size: 14px !important;
    font-weight: 500 !important;
}

:deep(.v-navigation-drawer) .v-btn__content {
    font-size: 14px !important;
    font-weight: 500 !important;
}

:deep(.v-navigation-drawer) .v-chip {
    font-weight: 500;
    opacity: 0.8;
    border: none;
    background-color: rgba(var(--v-theme-on-surface), 0.05);
}

:deep(.v-navigation-drawer) .sidebar-extra-item .v-list-item__content {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}
:deep(.v-navigation-drawer) .sidebar-extra-content {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
}
:deep(.v-navigation-drawer) .sidebar-extra-content img {
    margin: 0 auto;
    display: block;
}

:deep(.v-navigation-drawer) .v-list-item__spacer {
    width: 8px !important;
}

:deep(.v-navigation-drawer) .nav-links-item {
    padding-left: 8px;
    padding-right: 8px;
}
:deep(.v-navigation-drawer) .nav-links-item .v-list-item__content {
    display: block;
    width: 100%;
}
:deep(.v-navigation-drawer) .nav-link-col {
    padding: 0 4px;
    display: flex;
    justify-content: flex-start;
}
:deep(.v-navigation-drawer) .nav-link-btn {
    justify-content: flex-start;
    padding-left: 8px;
    padding-right: 8px;
    width: auto;
    min-width: unset;
}

.mobile-site-title {
    display: inline-block;
}
@media (max-width: 600px) {
    .mobile-site-title {
        max-width: 120px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-size: 16px;
        vertical-align: middle;
    }
}
</style>
