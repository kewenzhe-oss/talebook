<template>
    <div>
        <v-row>
            <v-col cols="12" class="mb-4 d-flex align-center">
                <v-btn
                    icon="mdi-arrow-left"
                    variant="text"
                    size="small"
                    class="mr-2"
                    @click="router.back()"
                />
                <p class="text-h5 font-weight-bold ma-0">
                    {{ title }}
                </p>
                <v-spacer />
                <v-chip
                    color="primary"
                    variant="flat"
                    size="small"
                    class="ml-3"
                    v-if="!loading"
                >
                    共 {{ allBooks.length }} 本书
                </v-chip>
            </v-col>
            
            <v-col cols="12">
                <Loading v-if="loading" />
                <template v-else>
                    <BookCards :books="displayBooks" />
                    
                    <div v-if="hasMore" class="d-flex justify-center mt-6 mb-4">
                        <v-btn
                            color="primary"
                            variant="tonal"
                            @click="loadMore"
                            :loading="loadingMore"
                        >
                            加载更多
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
const title = computed(() => targetSubject.value);

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
    title: () => targetSubject.value
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
