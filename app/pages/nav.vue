<template>
    <div>
        <!-- Category-first view: when categories exist -->
        <template v-if="categories.length > 0">
            <v-row class="mb-6">
                <v-col cols="12">
                    <h2 class="text-h4 font-weight-bold" style="letter-spacing: 0.02em;">分類導航</h2>
                    <p class="text-subtitle-1 text-grey-darken-1 mt-2" style="font-weight: 300;">從主題進入你的下一本書，按知識領域探索這座書房</p>
                </v-col>
            </v-row>
            <v-row>
                <v-col
                    v-for="cat in categories"
                    :key="cat.id"
                    cols="6"
                    sm="4"
                    md="3"
                    lg="3"
                >
                    <v-card
                        :to="'/subject/' + encodeURIComponent(cat.id)"
                        class="category-card rounded-xl pa-5 transition-swing"
                        variant="outlined"
                        style="border-width: 1px; border-color: rgba(var(--v-theme-on-surface), 0.12);"
                        hover
                    >
                        <div class="d-flex align-center mb-3">
                            <v-icon size="36" class="text-grey-darken-2 mr-3">
                                {{ cat.icon || 'mdi-folder' }}
                            </v-icon>
                            <div style="min-width: 0;">
                                <div class="text-h6 font-weight-bold text-truncate">{{ cat.name }}</div>
                                <div class="text-caption text-grey" v-if="categoryCounts[cat.id]">
                                    {{ categoryCounts[cat.id] }} 本書
                                </div>
                            </div>
                        </div>
                    </v-card>
                </v-col>
            </v-row>
        </template>

        <!-- Fallback: legacy tag-based nav (when no categories configured) -->
        <template v-else-if="navs.length > 0">
            <v-row class="mb-6">
                <v-col cols="12">
                    <h2 class="text-h4 font-weight-bold" style="letter-spacing: 0.02em;">分類導航</h2>
                    <p class="text-subtitle-1 text-grey-darken-1 mt-2" style="font-weight: 300;">從主題進入你的下一本書，按知識領域探索這座書房</p>
                </v-col>
            </v-row>
            <v-row>
                <v-col
                    v-for="nav in navs"
                    :key="nav.legend"
                    cols="6"
                    sm="4"
                    md="3"
                    lg="3"
                >
                    <v-card
                        :to="'/subject/' + encodeURIComponent(nav.legend)"
                        class="category-card rounded-xl pa-5 transition-swing"
                        variant="outlined"
                        style="border-width: 1px; border-color: rgba(var(--v-theme-on-surface), 0.12);"
                        hover
                    >
                        <div class="d-flex align-center">
                            <v-icon size="36" class="text-grey-darken-2 mr-3">mdi-folder</v-icon>
                            <div style="min-width: 0;">
                                <div class="text-h6 font-weight-bold text-truncate">{{ nav.legend }}</div>
                                <div class="text-caption text-grey">
                                    {{ nav.count || nav.tags?.length || 0 }} 本書
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
.transition-swing {
    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.5, 1);
}
.category-card {
    cursor: pointer;
}
.category-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
</style>
