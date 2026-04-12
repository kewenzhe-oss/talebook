<template>
    <v-container fluid class="px-0 px-md-4 py-6">
        <!-- Mobile Filter Trigger -->
        <div class="d-flex d-md-none mb-4 px-4">
            <v-btn block color="primary" variant="tonal" prepend-icon="mdi-filter-variant" @click="mobileFilterDrawer = true">
                篩選與分類
            </v-btn>
        </div>

        <!-- Mobile Drawer -->
        <v-navigation-drawer v-model="mobileFilterDrawer" temporary location="left" width="300">
            <div class="pa-4">
                <div class="d-flex justify-space-between align-center mb-6">
                    <h3 class="text-subtitle-1 font-weight-bold">篩選面板</h3>
                    <v-btn icon="mdi-close" variant="text" density="compact" @click="mobileFilterDrawer = false"></v-btn>
                </div>
                <!-- Filters content for mobile -->
                <div class="mb-4">
                    <div class="text-subtitle-2 font-weight-bold mb-1 text-grey-darken-1">出版社</div>
                    <v-autocomplete
                        v-model="filters.publisher"
                        :items="autocompletePublisherOptions"
                        variant="underlined"
                        density="compact"
                        hide-details
                        class="mb-4"
                        @update:model-value="onFilterChange"
                    ></v-autocomplete>
                </div>
                <div class="mb-4">
                    <div class="text-subtitle-2 font-weight-bold mb-1 text-grey-darken-1">作者</div>
                    <v-autocomplete
                        v-model="filters.author"
                        :items="autocompleteAuthorOptions"
                        variant="underlined"
                        density="compact"
                        hide-details
                        class="mb-4"
                        @update:model-value="onFilterChange"
                    ></v-autocomplete>
                </div>
                <div class="mb-4">
                    <div class="text-subtitle-2 font-weight-bold mb-1 text-grey-darken-1">標籤</div>
                    <v-autocomplete
                        v-model="filters.tag"
                        :items="autocompleteTagOptions"
                        variant="underlined"
                        density="compact"
                        hide-details
                        class="mb-4"
                        @update:model-value="onFilterChange"
                    ></v-autocomplete>
                </div>
                <div class="mb-4">
                    <div class="text-subtitle-2 font-weight-bold mb-1 text-grey-darken-1">格式</div>
                    <v-select
                        v-model="filters.format"
                        :items="formatOptions"
                        variant="underlined"
                        density="compact"
                        hide-details
                        @update:model-value="onFilterChange"
                    ></v-select>
                </div>
                <v-btn block color="primary" class="mt-4" @click="mobileFilterDrawer = false">完成</v-btn>
            </div>
        </v-navigation-drawer>

        <v-row class="ma-0">
            <!-- Desktop Sidebar -->
            <v-col cols="12" md="3" lg="2" class="d-none d-md-block px-2">
                <div style="position: sticky; top: 80px;">
                    <h3 class="text-subtitle-1 font-weight-bold mb-5 mt-2" style="letter-spacing: 0.05em; color: rgba(var(--v-theme-on-surface), 0.7);">篩選</h3>
                    
                    <div class="mb-5">
                        <div class="text-caption font-weight-bold mb-1 text-grey">出版社</div>
                        <v-autocomplete
                            v-model="filters.publisher"
                            :items="autocompletePublisherOptions"
                            variant="underlined"
                            density="compact"
                            hide-details
                            bg-color="transparent"
                            @update:model-value="onFilterChange"
                        ></v-autocomplete>
                    </div>
                    <div class="mb-5">
                        <div class="text-caption font-weight-bold mb-1 text-grey">作者</div>
                        <v-autocomplete
                            v-model="filters.author"
                            :items="autocompleteAuthorOptions"
                            variant="underlined"
                            density="compact"
                            hide-details
                            bg-color="transparent"
                            @update:model-value="onFilterChange"
                        ></v-autocomplete>
                    </div>
                    <div class="mb-5">
                        <div class="text-caption font-weight-bold mb-1 text-grey">標籤</div>
                        <v-autocomplete
                            v-model="filters.tag"
                            :items="autocompleteTagOptions"
                            variant="underlined"
                            density="compact"
                            hide-details
                            bg-color="transparent"
                            @update:model-value="onFilterChange"
                        ></v-autocomplete>
                    </div>
                    <div class="mb-5">
                        <div class="text-caption font-weight-bold mb-1 text-grey">格式</div>
                        <v-select
                            v-model="filters.format"
                            :items="formatOptions"
                            variant="underlined"
                            density="compact"
                            hide-details
                            bg-color="transparent"
                            @update:model-value="onFilterChange"
                        ></v-select>
                    </div>
                </div>
            </v-col>

            <!-- Right Results Area -->
            <v-col cols="12" md="9" lg="10" class="px-2">
                <!-- State Strip Header -->
                <div class="mb-6 pa-4 rounded-lg bg-surface d-flex flex-column" style="border: 1px solid rgba(var(--v-theme-on-surface), 0.08);">
                    <div class="d-flex flex-column flex-md-row align-start align-md-center justify-space-between w-100">
                        <div class="d-flex align-center flex-wrap">
                            <h2 class="text-h5 font-weight-bold mr-3" style="letter-spacing: 0.02em;">
                                {{ title }}
                            </h2>
                            <span class="text-subtitle-1 text-grey-darken-1" v-if="total > 0">
                                · 找到 {{ total }} 本結果
                            </span>
                            <span class="text-subtitle-1 text-grey-darken-1" v-else-if="total === 0 && inited">
                                · 0 本結果
                            </span>
                        </div>
                        
                        <div class="d-flex align-center mt-3 mt-md-0">
                            <span class="text-caption text-grey-darken-1 mr-2 d-none d-md-block">排序方式</span>
                            <v-select
                                v-model="sortBy"
                                :items="sortOptions"
                                item-title="text"
                                item-value="value"
                                variant="underlined"
                                density="compact"
                                hide-details
                                style="max-width: 140px; min-width: 120px;"
                                prepend-inner-icon="mdi-sort-variant"
                                bg-color="transparent"
                                @update:model-value="onSortChange"
                            />
                        </div>
                    </div>

                    <!-- Active Filters Row -->
                    <div v-if="hasActiveFilters" class="d-flex flex-wrap align-center ga-2 pt-3 mt-3" style="border-top: 1px dashed rgba(var(--v-theme-on-surface), 0.12);">
                        <span class="text-caption text-grey-darken-1 mr-1">篩選條件：</span>
                        
                        <v-chip closable size="small" color="grey-darken-3" variant="tonal" class="font-weight-medium"
                                v-if="filters.publisher && filters.publisher !== '全部'" 
                                @click:close="clearFilter('publisher')">
                            出版社: {{ filters.publisher }}
                        </v-chip>
                        
                        <v-chip closable size="small" color="grey-darken-3" variant="tonal" class="font-weight-medium"
                                v-if="filters.author && filters.author !== '全部'" 
                                @click:close="clearFilter('author')">
                            作者: {{ filters.author }}
                        </v-chip>

                        <v-chip closable size="small" color="grey-darken-3" variant="tonal" class="font-weight-medium"
                                v-if="filters.tag && filters.tag !== '全部'" 
                                @click:close="clearFilter('tag')">
                            標籤: {{ filters.tag }}
                        </v-chip>

                        <v-chip closable size="small" color="grey-darken-3" variant="tonal" class="font-weight-medium"
                                v-if="filters.format && filters.format !== '全部'" 
                                @click:close="clearFilter('format')">
                            格式: {{ filters.format }}
                        </v-chip>

                        <v-btn variant="text" size="small" color="grey-darken-1" class="ml-auto px-2" @click="clearAllFilters">清除全部</v-btn>
                    </div>
                </div>

                <div class="books-container">
                    <div v-if="total === 0 && inited" class="text-center pa-10 mt-6 rounded-lg bg-surface" style="border: 1px dashed rgba(var(--v-theme-on-surface), 0.12);">
                        <v-icon size="48" class="mb-4 text-grey-lighten-1">mdi-bookshelf</v-icon>
                        <div class="text-h6 text-grey-darken-2 mb-2">目前沒有符合條件的書籍</div>
                        <div class="text-body-2 text-grey">試著移除部分篩選條件，或探索其他分類。</div>
                        <v-btn v-if="hasActiveFilters" variant="outlined" color="grey-darken-2" class="mt-6 font-weight-medium" @click="clearAllFilters">清除全部篩選</v-btn>
                    </div>
                    <BookCards v-else :books="books" />
                </div>

                <v-container class="max-width mt-6">
                    <v-pagination
                        v-if="page_cnt > 0"
                        v-model="page"
                        :length="page_cnt"
                        rounded="circle"
                        @update:model-value="change_page"
                    />
                </v-container>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import BookCards from '~/components/BookCards.vue';
import { useMainStore } from '@/stores/main';
import { useI18n } from 'vue-i18n';

const store = useMainStore();
const { t } = useI18n();
const { $backend, $alert } = useNuxtApp();
const route = useRoute();

store.setNavbar(true);

const title = ref('所有藏書');
const page = ref(1);
const books = ref([]);
const total = ref(0);
const page_size = 30;
const page_cnt = ref(1);
const inited = ref(false);

const filters = ref({
    publisher: '全部',
    author: '全部',
    tag: '全部',
    format: '全部'
});

const sortBy = ref('timestamp');
const sortOptions = [
    { text: '最新入庫', value: 'timestamp' },
    { text: '評分最高', value: 'rating' },
    { text: '書名 A-Z', value: 'title' },
];

const filterOptions = ref({
    publisher: [],
    author: [],
    tag: [],
    format: []
});

const mobileFilterDrawer = ref(false);

const autocompletePublisherOptions = computed(() => {
    return ['全部', ...filterOptions.value.publisher.map(p => p.name)];
});
const autocompleteAuthorOptions = computed(() => {
    return ['全部', ...filterOptions.value.author.map(a => a.name)];
});
const autocompleteTagOptions = computed(() => {
    return ['全部', ...filterOptions.value.tag.map(tag => tag.name)];
});
const formatOptions = computed(() => {
    return ['全部', ...filterOptions.value.format.map(f => f.name)];
});

const hasActiveFilters = computed(() => {
    return (filters.value.publisher && filters.value.publisher !== '全部') ||
           (filters.value.author && filters.value.author !== '全部') ||
           (filters.value.tag && filters.value.tag !== '全部') ||
           (filters.value.format && filters.value.format !== '全部');
});

// 监听total变化，动态更新page_cnt
watch(total, (newTotal) => {
    page_cnt.value = newTotal > 0 ? Math.max(1, Math.ceil(newTotal / page_size)) : 0;
});

// 获取书籍数据
const fetchBooks = async (p = 1) => {
    // 构建查询参数
    const query = {
        start: (p - 1) * page_size,
        size: page_size,
        sort: sortBy.value
    };
  
    // 添加筛选条件
    Object.keys(filters.value).forEach(key => {
        if (filters.value[key] !== '全部') {
            query[key] = filters.value[key];
        }
    });
  
    // 构建查询字符串
    const queryString = Object.keys(query)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(query[key])}`)
        .join('&');
  
    try {
        const rsp = await $backend(`/library?${queryString}`);
        if (rsp.err === 'exception' || rsp.err === 'network_error') {
            if ($alert) $alert('error', rsp.msg || t('errors.networkError'));
            return;
        }
    
        books.value = rsp.books || [];
        total.value = rsp.total || 0;
        page_cnt.value = total.value > 0 ? Math.max(1, Math.ceil(total.value / page_size)) : 0;
        page.value = p;
        title.value = rsp.title || '所有藏書';
    } catch (error) {
        console.error('Failed to fetch books:', error);
        if ($alert) $alert('error', '獲取書籍失敗');
    }
};

// 排序变更
const onSortChange = () => {
    fetchBooks(1);
};

// 加载筛选选项
const loadFilterOptions = async () => {
    const filterTypes = ['publisher', 'author', 'tag', 'format'];
    for (const type of filterTypes) {
        try {
            const rsp = await $backend(`/${type}?show=all`);
            if (rsp.items) {
                filterOptions.value[type] = rsp.items;
            }
        } catch (error) {
            console.error(`Failed to load ${type} options:`, error);
        }
    }
};

// 初始化函数
const init = async () => {
    inited.value = true;
  
    // 从URL查询参数中解析筛选条件
    const query = route.query;
    Object.keys(filters.value).forEach(key => {
        if (query[key] && query[key] !== '全部') {
            filters.value[key] = query[key];
        }
    });
  
    // 解析页码
    let p = 1;
    if (query.start) {
        p = 1 + parseInt(query.start / page_size);
    }
  
    await fetchBooks(p);
    await loadFilterOptions();
};

// 翻页
const change_page = (newPage) => {
    page.value = newPage;
    fetchBooks(newPage);
};

// 更新筛选 (Select / Autocomplete bindings)
const onFilterChange = () => {
    // Check if null (cleared from autocomplete)
    if (!filters.value.publisher) filters.value.publisher = '全部';
    if (!filters.value.author) filters.value.author = '全部';
    if (!filters.value.tag) filters.value.tag = '全部';
    if (!filters.value.format) filters.value.format = '全部';
    
    fetchBooks(1);
};

const clearFilter = (type) => {
    filters.value[type] = '全部';
    fetchBooks(1);
};

const clearAllFilters = () => {
    filters.value = {
        publisher: '全部',
        author: '全部',
        tag: '全部',
        format: '全部'
    };
    fetchBooks(1);
};

// 监听路由变化
watch(() => route.query, () => {
    if (inited.value) {
        init();
    }
}, { deep: true });

// 初始加载
onMounted(() => {
    init();
});

useHead(() => ({
    title: '所有藏書'
}));
</script>

<style scoped>
.books-container {
    min-height: 400px;
}
.bg-grey-lighten-4 {
    background-color: #f5f5f5;
}
</style>
