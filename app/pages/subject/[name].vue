<template>
    <div>
        <v-row>
            <v-col cols="12" class="mb-6 d-flex align-start flex-column pl-4">
                <div class="d-flex align-center">
                    <v-btn
                        icon="mdi-arrow-left"
                        variant="text"
                        size="small"
                        class="mr-2"
                        @click="router.back()"
                    />
                    <h1 class="text-h4 font-weight-medium ma-0" style="letter-spacing: 0.05em;">
                        {{ localizedTitle }}
                    </h1>
                    <span class="ml-4 text-subtitle-2 text-grey-darken-1" style="font-weight: 300;" v-if="!loading">
                        {{ allBooks.length }} 本藏書
                    </span>
                </div>
                <div class="mt-2 ml-10 pl-1">
                    <p class="text-body-2 text-grey-darken-1 ma-0" style="font-weight: 300;">{{ localizedSubtitle }}</p>
                </div>
            </v-col>
            
            <v-col cols="12">
                <Loading v-if="loading" />
                <template v-else>
                    <BookCards :books="displayBooks" />
                    
                    <div v-if="hasMore" class="d-flex justify-center mt-6 mb-4">
                        <v-btn
                            color="primary"
                            variant="text"
                            @click="loadMore"
                            :loading="loadingMore"
                        >
                            載入更多
                        </v-btn>
                    </div>
                </template>
            </v-col>
        </v-row>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter, useNuxtApp } from 'nuxt/app';
import { useMainStore } from '@/stores/main';
import BookCards from '@/components/BookCards.vue';
import Loading from '@/components/Loading.vue';

// --- 全局模块级缓存 ---
// 存储格式: { [subjectName]: { timestamp: number, books: Array, hasMoreRemote: boolean } }
const CACHE_TTL = 10 * 60 * 1000; // 10分钟缓存
const subjectCache = new Map();

const store = useMainStore();
const { $backend } = useNuxtApp();
const route = useRoute();
const router = useRouter();

const targetSubject = computed(() => route.params.name);

const categoryMap = {
    'philosophy': { title: '哲學與思想', subtitle: '收錄哲學、邏輯、思想史與相關領域的重要著作' },
    'history-politics': { title: '歷史與政治', subtitle: '收錄歷史、政治學與社會發展之關鍵論述' },
    'science-history': { title: '科學史', subtitle: '匯總科學發展里程碑與重要探索紀錄' },
    'sociology': { title: '社會學', subtitle: '探討社會結構、群體行為與文化現象' },
    'logic': { title: '邏輯學', subtitle: '收錄邏輯推理與批判性思維相關著作' },
    'business-management': { title: '商業與管理', subtitle: '涵蓋商業策略、組織管理與領導力經典' },
    'economics-investment': { title: '經濟與投資', subtitle: '包含總體經濟、個體經濟與投資理財實務' },
    'genius-madness': { title: '天才與瘋狂', subtitle: '探索人類心智邊界與非凡創造力的故事' },
    'science': { title: '科學史', subtitle: '匯總科學發展里程碑與重要探索紀錄' },
    'history': { title: '歷史與政治', subtitle: '收錄歷史、政治學與社會發展之關鍵論述' },
    'business': { title: '商業與管理', subtitle: '涵蓋商業策略、組織管理與領導力經典' },
    'economics': { title: '經濟與投資', subtitle: '包含總體經濟、個體經濟與投資理財實務' },
    '科学史': { title: '科學史', subtitle: '匯總科學發展里程碑與重要探索紀錄' },
    '天才与疯狂': { title: '天才與瘋狂', subtitle: '探索人類心智邊界與非凡創造力的故事' },
    '社会学': { title: '社會學', subtitle: '探討社會結構、群體行為與文化現象' },
    '逻辑学': { title: '邏輯學', subtitle: '收錄邏輯推理與批判性思維相關著作' },
    '历史与政治': { title: '歷史與政治', subtitle: '收錄歷史、政治學與社會發展之關鍵論述' },
    '商业与管理': { title: '商業與管理', subtitle: '涵蓋商業策略、組織管理與領導力經典' },
    '经济与投资': { title: '經濟與投資', subtitle: '包含總體經濟、個體經濟與投資理財實務' }
};

const localizedTitle = computed(() => {
    const key = targetSubject.value || '';
    return categoryMap[key]?.title || categoryMap[key.toLowerCase()]?.title || key;
});

const localizedSubtitle = computed(() => {
    const key = targetSubject.value || '';
    return categoryMap[key]?.subtitle || categoryMap[key.toLowerCase()]?.subtitle || `收錄匯總${localizedTitle.value}之各類館藏經典`;
});

const allBooks = ref([]);
const displayBooks = ref([]);

const loading = ref(true);
const loadingMore = ref(false);
const hasMoreRemote = ref(false);

const pageSize = 24;
const currentPage = ref(1);

const hasMore = computed(() => {
    return displayBooks.value.length < allBooks.value.length;
});

store.setNavbar(true);
useHead({
    title: () => localizedTitle.value
});

async function fetchCategoryBooks() {
    try {
        const url = `/category/${encodeURIComponent(targetSubject.value)}?start=0&size=1000`;
        const rsp = await $backend(url);
        
        if (rsp && rsp.err === 'ok' && rsp.books) {
            allBooks.value = rsp.books;
           
            allBooks.value.sort((a, b) => {
                const ratingA = a.rating || 0;
                const ratingB = b.rating || 0;
                if (ratingA !== ratingB) return ratingB - ratingA;
                
                const downA = a.count_download || 0;
                const downB = b.count_download || 0;
                if (downA !== downB) return downB - downA;
                
                return b.id - a.id;
            });
            
            displayBooks.value = allBooks.value.slice(0, pageSize);
            await new Promise(resolve => setTimeout(resolve, 20));
        } else {
            console.error('获取分类书籍失败:', rsp);
        }
    } catch (e) {
        console.error('获取分类书籍出错:', e);
    }
}

function loadMore() {
    loadingMore.value = true;
    
    setTimeout(() => {
        currentPage.value++;
        const endIndex = currentPage.value * pageSize;
        displayBooks.value = allBooks.value.slice(0, endIndex);
        loadingMore.value = false;
    }, 50);
}

onMounted(async () => {
    loading.value = true;
    try {
        const subjectName = targetSubject.value;
        
        const cachedData = subjectCache.get(subjectName);
        if (cachedData && (Date.now() - cachedData.timestamp < CACHE_TTL)) {
            allBooks.value = [...cachedData.books];
            hasMoreRemote.value = false;
            currentPage.value = 1;
            displayBooks.value = allBooks.value.slice(0, pageSize);
            loading.value = false;
            return;
        }

        await fetchCategoryBooks();
        
        subjectCache.set(subjectName, {
            timestamp: Date.now(),
            books: [...allBooks.value]
        });
    } catch (error) {
        console.error('获取课题书籍列表初始化出错:', error);
    } finally {
        loading.value = false;
    }
});
</script>
