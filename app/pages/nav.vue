<template>
    <div>
        <!-- Category-first view: when categories exist -->
        <template v-if="categories.length > 0">
            <v-row class="mb-4">
                <v-col cols="12">
                    <h2 class="text-h5 font-weight-bold">分类导航</h2>
                    <p class="text-subtitle-2 text-grey mt-1">按主题分类浏览书库</p>
                </v-col>
            </v-row>
            <v-row>
                <v-col
                    v-for="cat in categories"
                    :key="cat.id"
                    cols="12"
                    sm="6"
                    md="4"
                    lg="3"
                >
                    <v-card
                        :to="'/subject/' + encodeURIComponent(cat.id)"
                        class="category-card rounded-xl pa-5"
                        :color="cat.color || 'primary'"
                        variant="flat"
                        hover
                    >
                        <div class="d-flex align-center mb-3">
                            <v-icon size="36" class="text-white mr-3">
                                {{ cat.icon || 'mdi-folder' }}
                            </v-icon>
                            <div>
                                <div class="text-h6 font-weight-bold text-white">{{ cat.name }}</div>
                                <div class="text-caption text-white" style="opacity:0.8" v-if="categoryCounts[cat.id]">
                                    {{ categoryCounts[cat.id] }} 本书
                                </div>
                            </div>
                        </div>
                    </v-card>
                </v-col>
            </v-row>
        </template>

        <!-- Fallback: legacy tag-based nav (when no categories configured) -->
        <template v-else-if="navs.length > 0">
            <v-row>
                <v-col cols="12">
                    <h2 class="text-h5 font-weight-bold">分类导航</h2>
                    <p class="text-subtitle-2 text-grey mt-1">按主题分类浏览书库</p>
                </v-col>
            </v-row>
            <v-row>
                <v-col
                    v-for="nav in navs"
                    :key="nav.legend"
                    cols="12"
                    sm="6"
                    md="4"
                    lg="3"
                >
                    <v-card
                        :to="'/subject/' + encodeURIComponent(nav.legend)"
                        class="category-card rounded-xl pa-5"
                        color="primary"
                        variant="flat"
                        hover
                    >
                        <div class="d-flex align-center">
                            <v-icon size="36" class="text-white mr-3">mdi-folder</v-icon>
                            <div>
                                <div class="text-h6 font-weight-bold text-white">{{ nav.legend }}</div>
                                <div class="text-caption text-white" style="opacity:0.8">
                                    {{ nav.count || nav.tags?.length || 0 }} 本书
                                </div>
                            </div>
                        </div>
                    </v-card>
                </v-col>
            </v-row>
        </template>

        <!-- 空状态提示 -->
        <v-row
            v-if="!hasAnyData"
            class="empty-state"
        >
            <v-col cols="12">
                <v-card class="ma-1 pa-6 text-center">
                    <v-icon
                        large
                        color="grey lighten-2"
                    >
                        mdi-book-open-variant
                    </v-icon>
                    <h3 class="text-h6 grey--text">
                        {{ t('messages.noBooks') }}
                    </h3>
                    <p class="text-caption grey--text">
                        {{ t('messages.addBooksFirst') }}
                    </p>
                </v-card>
            </v-col>
        </v-row>
    </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAsyncData, useNuxtApp } from 'nuxt/app';
import { useMainStore } from '@/stores/main';

const store = useMainStore();
const { $backend } = useNuxtApp();
const { t } = useI18n();

const categories = ref([]);
const categoryCounts = ref({});
const navs = ref([]);

const { data: navData } = useAsyncData('nav', async () => {
    try {
        const response = await $backend('/book/nav');
        return response;
    } catch (error) {
        console.error('获取导航数据失败:', error);
        return { navs: [], categories: [] };
    }
});

// Watch data and populate reactive state
watch(navData, (newData) => {
    if (newData) {
        // Prefer categories (Category-first)
        const cats = newData.categories || [];
        categories.value = cats.filter(c => c.enabled !== false);
        categoryCounts.value = newData.category_counts || {};

        // Fallback navs (legacy BOOK_NAV)
        navs.value = (newData.navs || []).filter(n => n.legend !== '其他');
    }
}, { immediate: true });

const hasAnyData = computed(() => {
    return categories.value.length > 0 || navs.value.length > 0;
});

store.setNavbar(true);

useHead(() => ({
    title: t('messages.bookIndex')
}));
</script>

<style scoped>
.category-card {
    transition: transform 0.2s cubic-bezier(0.25, 0.8, 0.5, 1), box-shadow 0.2s;
    cursor: pointer;
}
.category-card:hover {
    transform: translateY(-2px);
}
</style>
