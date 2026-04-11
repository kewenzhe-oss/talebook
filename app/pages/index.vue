<template>
    <div>
        <!-- Hero Search -->
        <v-row class="mt-8 mb-10 justify-center">
            <v-col cols="12" md="8" class="text-center">
                <h1 class="text-h3 font-weight-bold mb-4">探索您的数字书房</h1>
                <p class="text-subtitle-1 text-grey mb-6">按拼音首字母、书名、作者或主标签快速查找</p>
                <v-text-field
                    v-model="searchQuery"
                    prepend-inner-icon="mdi-magnify"
                    label="在此搜寻书籍灵感..."
                    variant="solo"
                    rounded="pill"
                    clearable
                    @keyup.enter="doSearch"
                    hide-details
                    class="elevation-2"
                ></v-text-field>
            </v-col>
        </v-row>

        <!-- Continue Reading / Recent Books -->
        <v-row v-if="get_recent_books && get_recent_books.length > 0" class="mb-8">
            <v-col cols="12">
                <div class="d-flex align-center justify-space-between mb-4">
                    <h2 class="text-h5 font-weight-bold ma-0">最近入库</h2>
                </div>
                <BookCards :books="get_recent_books" />
            </v-col>
        </v-row>

        <!-- Curated Categories -->
        <v-row v-if="categories && categories.length > 0" class="mb-4">
            <v-col cols="12">
                <h2 class="text-h5 font-weight-bold ma-0 mb-4">精选分类馆</h2>
            </v-col>
            <v-col cols="12" sm="4" md="3" v-for="cat in categories.slice(0, 8)" :key="cat.id">
                <v-card :color="cat.color || 'primary'" variant="flat" :to="'/subject/' + cat.name" class="text-center pa-6 transition-swing rounded-xl" hover>
                    <v-icon size="48" class="mb-3 text-white">{{ cat.icon || 'mdi-folder' }}</v-icon>
                    <div class="text-h6 font-weight-bold text-white">{{ cat.name }}</div>
                </v-card>
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

const categories = computed(() => {
    // Return dynamically configured categories, ensuring they are enabled
    const cats = navData.value?.categories || [];
    return cats.filter(c => c.enabled !== false);
});

function doSearch() {
    if (searchQuery.value && searchQuery.value.trim()) {
        router.push({ path: '/search', query: { title: searchQuery.value.trim() } });
    }
}
</script>

<style scoped>
.transition-swing {
    transition: 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
}
</style>