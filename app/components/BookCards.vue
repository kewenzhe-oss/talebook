<template>
    <div>
        <v-row>
            <v-col
                v-for="(book,idx) in render_books"
                :key="idx+'-books-'+book.id"
                cols="6"
                sm="4"
                md="3"
                lg="3"
                xl="2"
                class="book-list-card pa-2 pa-sm-3"
            >
                <v-hover v-slot="{ isHovering, props }">
                    <v-card 
                        v-bind="props" 
                        :to="book.href"
                        :elevation="isHovering ? 8 : 2"
                        class="d-flex flex-column h-100 position-relative transition-swing"
                        color="surface"
                    >
                        <v-img
                            :src="book.img"
                            :aspect-ratio="3/4"
                            cover
                            :lazy-src="book.thumb"
                            loading="lazy"
                            class="align-end bg-grey-lighten-2"
                        >
                            <v-fade-transition>
                                <div
                                    v-if="isHovering"
                                    class="d-flex flex-column align-center justify-center align-self-stretch w-100 h-100"
                                    style="background-color: rgba(0,0,0,0.65);"
                                >
                                    <v-btn
                                        color="primary"
                                        variant="elevated"
                                        class="mb-2 mx-1"
                                        size="small"
                                        rounded
                                        v-if="book.id > 0"
                                        @click.prevent="openUrl('/read/' + book.id)"
                                    >
                                        <v-icon start size="small">mdi-book-open-page-variant</v-icon>
                                        開始閱讀
                                    </v-btn>
                                    <v-btn
                                        color="white"
                                        variant="outlined"
                                        class="mb-2 mx-1"
                                        size="small"
                                        rounded
                                        v-if="book.id > 0"
                                        @click.prevent="openUrl(book.href)"
                                    >
                                        <v-icon start size="small">mdi-download</v-icon>
                                        下載
                                    </v-btn>
                                </div>
                            </v-fade-transition>
                        </v-img>
                        <v-card-text class="d-flex flex-column pa-3 flex-grow-1 text-center">
                            <div class="book-title mb-1 text-subtitle-1 font-weight-bold text-left text-primary" :title="book.title">
                                {{ book.title }}
                            </div>
                            <div class="d-flex align-center justify-space-between w-100 mt-auto px-1" style="min-width: 0;">
                                <div class="text-caption text-secondary text-truncate text-left flex-grow-1 mr-2" style="min-width: 0;" :title="book.author">
                                    {{ book.author }}
                                </div>
                                <v-chip
                                    v-if="book.tags && book.tags.length > 0"
                                    size="small"
                                    color="primary"
                                    variant="tonal"
                                    class="flex-shrink-0 font-weight-medium px-2"
                                >
                                    {{ book.tags[0] }}
                                </v-chip>
                            </div>
                        </v-card-text>
                    </v-card>
                </v-hover>
            </v-col>
        </v-row>
        
        <!-- 空状态提示 -->
        <v-row
            v-if="render_books.length === 0"
            class="empty-state"
        >
            <v-col cols="12">
                <v-card class="ma-1 pa-6 text-center bg-surface border-subtle elevation-1">
                    <v-icon
                        large
                        class="text-tertiary mb-2"
                    >
                        mdi-book-open-variant
                    </v-icon>
                    <h3 class="text-h6 text-secondary font-weight-bold mb-1">
                        暫無藏書
                    </h3>
                    <p class="text-caption text-tertiary">
                        請先新增或匯入書籍
                    </p>
                </v-card>
            </v-col>
        </v-row>
    </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
    books: {
        type: Array,
        default: () => [],
    },
});

const render_books = computed(() => {
    return props.books.map( b => ({
        ...b,
        href: b.href ?? '/book/' + b.id,
    }));
});

const openUrl = (url) => {
    window.open(url, '_blank', 'noopener,noreferrer');
};
</script>

<style scoped>
.book-title {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.3em;
    height: 2.6em; /* 1.3em * 2 lines */
}
.book-author {
    width: 100%;
}
.bg-grey-lighten-2 {
    background-color: #e0e0e0;
}

@media (max-width: 600px) {
    .book-title {
        font-size: 0.875rem !important; /* text-subtitle-2 equivalent */
        line-height: 1.3em !important;
        height: 2.6em !important;
    }
    .book-list-card .text-caption.text-grey {
        opacity: 0.85;
    }
    .book-list-card :deep(.v-chip) {
        font-size: 10px !important;
        height: 20px !important;
        padding: 0 6px !important;
    }
}
</style>
