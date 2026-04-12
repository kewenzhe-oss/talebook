
<template>
    <v-container fluid class="px-md-6 py-6" style="max-width: 1200px;">
        <!-- Page Context Header -->
        <div class="mb-8">
            <h1 class="text-h4 font-weight-bold mb-1" style="letter-spacing: 0.02em;">{{ pageTitle }}</h1>
            <p class="text-subtitle-1 text-grey-darken-1 mb-0" style="font-weight: 400;">{{ pageSubtitle }}</p>
        </div>

        <!-- Search Bar -->
        <div class="mb-6" style="max-width: 480px;">
            <v-text-field
                v-model="searchQuery"
                :placeholder="searchPlaceholder"
                variant="outlined"
                density="compact"
                hide-details
                clearable
                rounded="lg"
                prepend-inner-icon="mdi-magnify"
                class="directory-search"
            ></v-text-field>
        </div>

        <!-- Rating Special Layout -->
        <template v-if="meta === 'rating'">
            <v-row>
                <v-col cols="12" sm="6" md="4" v-for="item in filteredItems" :key="item.name">
                    <v-card
                        :to="item.href"
                        variant="outlined"
                        class="directory-card pa-4 d-flex align-center justify-space-between"
                        hover
                    >
                        <div class="d-flex align-center">
                            <v-rating
                                :model-value="Number(item.name)"
                                readonly
                                density="compact"
                                size="small"
                                color="amber-darken-1"
                                class="mr-2"
                            ></v-rating>
                            <span class="text-body-2 text-grey-darken-1">{{ item.name }} 星</span>
                        </div>
                        <span class="text-caption text-grey">{{ item.count }} 本</span>
                    </v-card>
                </v-col>
            </v-row>
        </template>

        <!-- Directory List Layout (Default) -->
        <template v-else>
            <!-- Results count -->
            <div class="d-flex align-center justify-space-between mb-4" v-if="filteredItems.length > 0">
                <span class="text-caption text-grey-darken-1">
                    <template v-if="searchQuery && searchQuery.trim()">
                        搜尋到 {{ filteredItems.length }} {{ unitLabel }}
                    </template>
                    <template v-else>
                        共 {{ total }} {{ unitLabel }}
                    </template>
                </span>
                <v-btn
                    v-if="!show_all && total > items.length"
                    variant="text"
                    size="small"
                    color="primary"
                    @click="expand()"
                    class="font-weight-medium"
                >
                    載入全部 {{ total }} 項
                    <v-icon end size="small">mdi-chevron-right</v-icon>
                </v-btn>
            </div>

            <!-- Two-column directory grid -->
            <v-row>
                <v-col cols="12" md="6" v-for="item in filteredItems" :key="item.name">
                    <router-link
                        :to="item.href"
                        class="directory-item d-flex align-center justify-space-between text-decoration-none"
                    >
                        <div class="d-flex align-center overflow-hidden mr-3">
                            <v-icon size="18" class="text-grey-darken-1 mr-3 flex-shrink-0">{{ metaIcon }}</v-icon>
                            <span class="text-body-1 text-grey-darken-4 font-weight-medium text-truncate">{{ item.name }}</span>
                        </div>
                        <div class="d-flex align-center flex-shrink-0">
                            <span class="text-caption text-grey">{{ item.count }} 本</span>
                            <v-icon size="16" class="text-grey-lighten-1 ml-2">mdi-chevron-right</v-icon>
                        </div>
                    </router-link>
                </v-col>
            </v-row>

            <!-- Empty state -->
            <div v-if="filteredItems.length === 0 && searchQuery" class="text-center pa-10 mt-4">
                <v-icon size="40" class="text-grey-lighten-1 mb-3">mdi-magnify</v-icon>
                <div class="text-body-1 text-grey-darken-1 mb-1">找不到符合「{{ searchQuery }}」的結果</div>
                <div class="text-body-2 text-grey">請嘗試其他關鍵詞</div>
            </div>

            <div v-if="filteredItems.length === 0 && !searchQuery && items.length === 0" class="text-center pa-10 mt-4">
                <v-icon size="40" class="text-grey-lighten-1 mb-3">mdi-bookshelf</v-icon>
                <div class="text-body-1 text-grey-darken-1">目前沒有任何資料</div>
            </div>
        </template>
    </v-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAsyncData, useNuxtApp } from 'nuxt/app';
import { useMainStore } from '@/stores/main';
import { useI18n } from 'vue-i18n';

const route = useRoute();
const store = useMainStore();
const { $backend } = useNuxtApp();
const { t } = useI18n();

const props = defineProps({
    metaType: {
        type: String,
        default: ''
    }
});

store.setNavbar(true);

const meta = computed(() => props.metaType || route.path.split('/')[1]);
const show_all = ref(false);
const items = ref([]);
const total = ref(0);
const searchQuery = ref('');

// Page context configuration
const metaConfig = {
    publisher: {
        title: '出版社',
        subtitle: '瀏覽館藏中的所有出版社索引',
        searchPlaceholder: '搜尋出版社…',
        unit: '間',
        icon: 'mdi-domain'
    },
    tag: {
        title: '標籤',
        subtitle: '瀏覽所有主題與關鍵詞',
        searchPlaceholder: '搜尋標籤…',
        unit: '個',
        icon: 'mdi-tag-outline'
    },
    format: {
        title: '格式',
        subtitle: '依檔案格式瀏覽館藏',
        searchPlaceholder: '搜尋格式…',
        unit: '種',
        icon: 'mdi-file-document-outline'
    },
    author: {
        title: '作者',
        subtitle: '瀏覽館藏中的所有作者',
        searchPlaceholder: '搜尋作者…',
        unit: '位',
        icon: 'mdi-account-outline'
    },
    rating: {
        title: '評分',
        subtitle: '依評分高低瀏覽館藏',
        searchPlaceholder: '搜尋評分…',
        unit: '級',
        icon: 'mdi-star-outline'
    },
    series: {
        title: '叢書',
        subtitle: '瀏覽館藏中的所有系列叢書',
        searchPlaceholder: '搜尋叢書…',
        unit: '套',
        icon: 'mdi-bookshelf'
    }
};

const config = computed(() => metaConfig[meta.value] || { title: '索引', subtitle: '', searchPlaceholder: '搜尋…', unit: '項', icon: 'mdi-bookmark-outline' });
const pageTitle = computed(() => config.value.title);
const pageSubtitle = computed(() => config.value.subtitle);
const searchPlaceholder = computed(() => config.value.searchPlaceholder);
const unitLabel = computed(() => config.value.unit);
const metaIcon = computed(() => config.value.icon);

const { data, refresh } = useAsyncData(`meta-${meta.value}`, async () => {
    const path = '/' + meta.value + (show_all.value ? '?show=all' : '');
    try {
        const rsp = await $backend(path);
        items.value = rsp.items || [];
        total.value = rsp.total || 0;
        return rsp;
    } catch (e) {
        console.error(e);
        return null;
    }
}, {
    watch: [meta, show_all]
});

watch([meta, show_all], () => {
    refresh();
});

const expand = () => {
    show_all.value = !show_all.value;
};

const meta_items = computed(() => {
    var prefix = '/' + meta.value + '/';
    return items.value.map(d => {
        d.href = prefix + encodeURIComponent(d.name);
        return d;
    });
});

const filteredItems = computed(() => {
    const q = (searchQuery.value || '').trim().toLowerCase();
    if (!q) return meta_items.value;
    return meta_items.value.filter(item =>
        item.name.toLowerCase().includes(q)
    );
});

useHead({
    title: () => pageTitle.value || t(`messages.titles.${meta.value}`) || ''
});
</script>

<style scoped>
.directory-item {
    padding: 14px 16px;
    border-radius: 10px;
    border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
    background-color: rgb(var(--v-theme-surface));
    transition: all 0.2s ease;
    cursor: pointer;
}

.directory-item:hover {
    background-color: rgba(var(--v-theme-primary), 0.04);
    border-color: rgba(var(--v-theme-primary), 0.15);
}

.directory-item:hover .text-grey-darken-4 {
    color: rgb(var(--v-theme-primary)) !important;
}

.directory-item:hover .mdi-chevron-right {
    color: rgba(var(--v-theme-on-surface), 0.5) !important;
}

.directory-card {
    border-radius: 10px !important;
    border-color: rgba(var(--v-theme-on-surface), 0.08) !important;
    transition: all 0.2s ease;
}

.directory-card:hover {
    border-color: rgba(var(--v-theme-primary), 0.2) !important;
    background-color: rgba(var(--v-theme-primary), 0.03);
}

.directory-search :deep(.v-field) {
    border-color: rgba(var(--v-theme-on-surface), 0.12);
}

.directory-search :deep(.v-field:hover) {
    border-color: rgba(var(--v-theme-on-surface), 0.25);
}
</style>