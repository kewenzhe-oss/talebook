<template>
    <div>
        <!-- Hero Search Section -->
        <v-row class="hero-search-row justify-center">
            <v-col cols="12">
                <div class="hero-card-container">
                    <div class="hero-card pa-8 pa-sm-12 text-center">
                        <h1 class="hero-title font-weight-black mb-3">探索您的數位書房</h1>
                        <p class="hero-subtitle text-grey-darken-1">依主題整理，為深度閱讀而設計</p>
                        <div class="search-input-wrapper">
                            <v-text-field
                                v-model="searchQuery"
                                prepend-inner-icon="mdi-magnify"
                                label="搜尋書名、作者、標籤，快速進入閱讀..."
                                variant="solo"
                                rounded="pill"
                                clearable
                                @keyup.enter="doSearch"
                                hide-details
                                class="custom-search-input"
                            ></v-text-field>
                        </div>
                    </div>
                </div>
            </v-col>
        </v-row>

        <!-- Continue Reading -->
        <v-row v-if="continue_reading && continue_reading.length > 0" class="mb-10">
            <v-col cols="12">
                <div class="d-flex align-center justify-space-between mb-4">
                    <h2 class="text-h5 font-weight-bold ma-0" style="letter-spacing: 0.02em;">
                        <v-icon class="mr-2" color="primary">mdi-book-open-page-variant</v-icon>
                        繼續閱讀
                    </h2>
                </div>
                <BookCards :books="continue_reading" />
            </v-col>
        </v-row>

        <!-- Curated Categories (Moved up before Recent Books) -->
        <v-row v-if="categories && categories.length > 0" class="mb-10">
            <v-col cols="12">
                <div class="mb-5">
                    <h2 class="text-h5 font-weight-bold mb-1 text-primary" style="letter-spacing: 0.02em;">精選分類館</h2>
                    <p class="text-subtitle-2 text-secondary mb-0" style="font-weight: 400;">從主題進入你的下一本書</p>
                </div>
            </v-col>
            <v-col cols="6" sm="4" md="3" v-for="cat in categories.slice(0, 8)" :key="cat.id">
                <v-card :to="'/subject/' + encodeURIComponent(cat.id)" class="category-card pa-5 transition-swing border-subtle bg-surface" variant="outlined" hover>
                    <div class="d-flex flex-column align-center text-center">
                        <v-icon size="36" class="mb-3 text-secondary">{{ cat.icon || 'mdi-bookshelf' }}</v-icon>
                        <div class="text-subtitle-1 font-weight-bold text-truncate w-100 text-primary">{{ getLocalizedCatName(cat.id, cat.name) }}</div>
                        <div v-if="store.sys?.category_counts && store.sys.category_counts[cat.id]" class="text-caption text-tertiary mt-1">
                            {{ store.sys.category_counts[cat.id] }} 本藏書
                        </div>
                        <div v-else class="text-caption text-tertiary mt-1">
                            {{ getLocalizedCatSubtitle(cat.id, cat.name) }}
                        </div>
                    </div>
                </v-card>
            </v-col>
        </v-row>

        <!-- Recent Books -->
        <v-row v-if="get_recent_books && get_recent_books.length > 0" class="mb-10">
            <v-col cols="12">
                <div class="d-flex align-center justify-space-between mb-4">
                    <h2 class="text-h5 font-weight-bold ma-0" style="letter-spacing: 0.02em;">最近入庫</h2>
                </div>
                <BookCards :books="get_recent_books" />
            </v-col>
        </v-row>
    </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useAsyncData, useNuxtApp, useRoute, useRouter } from 'nuxt/app';
import { useMainStore } from '@/stores/main';
import BookCards from '@/components/BookCards.vue';

const store = useMainStore();
const { $backend, $alert } = useNuxtApp();
const router = useRouter();
const route = useRoute();

const searchQuery = ref('');

onMounted(() => {
    if (route.query.err === 'opds_disabled' && route.query.msg) {
        if ($alert) {
            $alert('error', route.query.msg);
        }
    }
});

const { data: indexData } = useAsyncData('index', () => $backend('/index?recent=12'));
const { data: navData } = useAsyncData('categories', () => $backend('/book/nav'));

store.setNavbar(true);

const get_recent_books = computed(() => {
    const books = indexData.value?.recent_books || [];
    return books.map(b => ({
        ...b,
        href: '/book/' + b.id
    }));
});

const continue_reading = computed(() => {
    const books = indexData.value?.continue_reading || [];
    return books.map(b => ({
        ...b,
        href: '/book/' + b.id
    }));
});

const categories = computed(() => {
    // Return dynamically configured categories, ensuring they are enabled
    const cats = navData.value?.categories || [];
    return cats.filter(c => c.enabled !== false);
});

const categoryMap = {
    'philosophy': { title: '哲學與思想', subtitle: '哲學、邏輯與思想史' },
    'psychology': { title: '心理與自我', subtitle: '人格、情緒與自我成長' },
    'relationship': { title: '關係與家庭', subtitle: '親密關係、溝通與家庭議題' },
    'literature': { title: '文學與敘事', subtitle: '小說、散文與敘事寫作' },
    'society': { title: '社會與文化', subtitle: '社會理論、文化觀察與媒介批評' },
    'technology': { title: '科技與計算', subtitle: '程式設計、AI 與技術思維' },
    'history-politics': { title: '歷史與政治', subtitle: '歷史、政治與社會發展' },
    'business-management': { title: '商業與管理', subtitle: '商業策略與組織領導' },
    'economics-investment': { title: '經濟與投資', subtitle: '總體經濟與理財實務' },
    'science-history': { title: '科學史', subtitle: '科學里程碑與探索紀錄' },
    'sociology': { title: '社會學', subtitle: '社會結構與文化現象' },
    'logic': { title: '邏輯學', subtitle: '邏輯推理與批判性思維' },
    'genius-madness': { title: '天才與瘋狂', subtitle: '心智邊界與非凡創造力' },
    'science': { title: '科學史', subtitle: '科學里程碑與探索紀錄' },
    'history': { title: '歷史與政治', subtitle: '歷史、政治與社會發展' },
    'business': { title: '商業與管理', subtitle: '商業策略與組織領導' },
    'economics': { title: '經濟與投資', subtitle: '總體經濟與理財實務' },
    '心理与自我': { title: '心理與自我', subtitle: '人格、情緒與自我成長' },
    '关系与家庭': { title: '關係與家庭', subtitle: '親密關係、溝通與家庭議題' },
    '文学与叙事': { title: '文學與敘事', subtitle: '小說、散文與敘事寫作' },
    '社会与文化': { title: '社會與文化', subtitle: '社會理論、文化觀察與媒介批評' },
    '科技与计算': { title: '科技與計算', subtitle: '程式設計、AI 與技術思維' },
    '哲学与思想': { title: '哲學與思想', subtitle: '哲學、邏輯與思想史' },
    '科学史': { title: '科學史', subtitle: '科學里程碑與探索紀錄' },
    '天才与疯狂': { title: '天才與瘋狂', subtitle: '心智邊界與非凡創造力' },
    '社会学': { title: '社會學', subtitle: '社會結構與文化現象' },
    '逻辑学': { title: '邏輯學', subtitle: '邏輯推理與批判性思維' },
    '历史与政治': { title: '歷史與政治', subtitle: '歷史、政治與社會發展' },
    '商业与管理': { title: '商業與管理', subtitle: '商業策略與組織領導' },
    '经济与投资': { title: '經濟與投資', subtitle: '總體經濟與理財實務' }
};

function getLocalizedCatName(id, name) {
    return categoryMap[id]?.title || categoryMap[name]?.title || categoryMap[name.toLowerCase()]?.title || name;
}

function getLocalizedCatSubtitle(id, name) {
    return categoryMap[id]?.subtitle || categoryMap[name]?.subtitle || categoryMap[name.toLowerCase()]?.subtitle || '相關主題精華典藏';
}

function doSearch() {
    if (searchQuery.value && searchQuery.value.trim()) {
        router.push({ path: '/search', query: { name: searchQuery.value.trim() } });
    }
}
</script>

<style scoped>
.transition-swing {
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
}
.category-card {
    border-radius: 12px;
    padding: 20px;
}
.category-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

/* Hero Section Styles */
.hero-search-row {
    margin-top: 24px;
    margin-bottom: 40px;
}
.hero-card-container {
    width: 100%;
}
.hero-card {
    background-color: var(--bg-muted);
    border: 1px solid var(--border-subtle);
    border-radius: 24px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.015);
    transition: all 0.3s ease;
}

.hero-title {
    font-size: 2.5rem;
    line-height: 1.25;
    letter-spacing: 0.05em;
    color: var(--text-primary);
}

.hero-subtitle {
    font-size: 1.05rem;
    font-weight: 300;
    margin-top: 12px; /* Title to subtitle: 12px */
    margin-bottom: 28px !important; /* Subtitle to search box: 28px (24px-32px) */
    color: var(--text-secondary);
}

.search-input-wrapper {
    max-width: 640px; /* Limit input width to max-w-2xl equivalent */
    margin: 0 auto;
}

/* Custom Search Input override */
.custom-search-input :deep(.v-field) {
    background-color: var(--bg-surface-raised) !important;
    border: 1px solid var(--border-subtle) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Hover state */
.custom-search-input :deep(.v-field:hover) {
    border-color: var(--border-strong) !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
}

/* Focus state */
.custom-search-input :deep(.v-field--focused) {
    border-color: rgb(var(--v-theme-primary)) !important;
    box-shadow: 0 4px 20px rgba(var(--v-theme-primary), 0.15) !important;
}

.custom-search-input :deep(.v-field__input) {
    font-size: 1.05rem !important;
    padding-top: 14px !important;
    padding-bottom: 14px !important;
}

/* Layout & Spacing */
.category-row {
    margin-bottom: 40px;
}
.category-header-col {
    padding-bottom: 20px;
}
.category-icon {
    margin-bottom: 12px;
}
.category-card-content {
    width: 100%;
}
.category-card-subtitle {
    font-size: 0.825rem;
}
.section-row {
    margin-bottom: 40px;
}

@media (max-width: 600px) {
    .hero-search-row {
        margin-top: 12px !important;
        margin-bottom: 24px !important;
    }
    .hero-card {
        padding: 32px 16px !important;
        border-radius: 16px !important;
    }
    .hero-title {
        font-size: 1.75rem !important;
    }
    .hero-subtitle {
        font-size: 0.875rem !important;
        margin-top: 8px !important;
        margin-bottom: 20px !important;
    }
    .category-row {
        margin-bottom: 24px !important;
    }
    .category-header-col {
        padding-bottom: 8px !important;
    }
    .category-card {
        padding: 12px 8px !important;
    }
    .category-icon {
        font-size: 28px !important;
        margin-bottom: 8px !important;
    }
    .category-card-title {
        font-size: 14px !important;
    }
    .category-card-subtitle {
        font-size: 11px !important;
        margin-top: 2px !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        max-width: 100% !important;
    }
    .section-row {
        margin-bottom: 24px !important;
    }
}
</style>