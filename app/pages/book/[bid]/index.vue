<template>
    <div>
        <!-- Main Content -->
        <v-row align="start">
            <v-col cols="12">
                <!-- Kindle Push Dialog (disabled - replaced by NotebookLM) -->
                <!--
                <v-dialog
                    v-model="dialog_kindle"
                    persistent
                    width="300"
                >
                    <v-card>
                        <v-card-title>{{ t('book.kindle.push') }}</v-card-title>
                        <v-card-text>
                            <p class="mb-4">
                                {{ t('book.kindle.emailPlaceholder') }}
                            </p>
                            <v-combobox
                                v-model="mail_to"
                                :items="email_items"
                                :rules="[check_email]"
                                variant="outlined"
                                density="compact"
                                label="Email*"
                                auto-select-first
                                required
                            />
                            <small>* 请先将本站邮箱加入到Kindle发件人中:<br>{{ kindle_sender }}</small>
                        </v-card-text>
                        <v-card-actions>
                            <v-btn
                                variant="text"
                                @click="dialog_kindle = false"
                            >
                                {{ t('common.cancel') }}
                            </v-btn>
                            <v-spacer />
                            <v-btn
                                color="primary"
                                variant="text"
                                @click="sendto_kindle"
                            >
                                {{ t('common.send') }}
                            </v-btn>
                        </v-card-actions>
                    </v-card>
                </v-dialog>
                -->

                <!-- Download Dialog -->
                <v-dialog
                    v-model="dialog_download"
                    persistent
                    width="300"
                >
                    <v-card>
                        <v-card-title>下載書籍</v-card-title>
                        <v-card-text>
                            <v-list v-if="book.files && book.files.length > 0">
                                <v-list-item
                                    v-for="file in book.files"
                                    :key="'file-'+file.format"
                                    target="_blank"
                                    :href="file.href"
                                >
                                    <template #prepend>
                                        <v-avatar color="primary">
                                            <v-icon color="white">
                                                mdi-download
                                            </v-icon>
                                        </v-avatar>
                                    </template>
                                    <v-list-item-title>{{ file.format }}</v-list-item-title>
                                    <v-list-item-subtitle v-if="file.size>=1048576">
                                        {{ parseInt(file.size / 1048576) }}MB
                                    </v-list-item-subtitle>
                                    <v-list-item-subtitle v-else>
                                        {{ parseInt(file.size / 1024) }}KB
                                    </v-list-item-subtitle>
                                </v-list-item>
                            </v-list>
                            <p v-else>
                                <br>暫無支援下載的格式
                            </p>
                        </v-card-text>
                        <v-card-actions>
                            <v-spacer />
                            <v-btn
                                variant="text"
                                @click="dialog_download = false"
                            >
                                關閉
                            </v-btn>
                            <v-spacer />
                        </v-card-actions>
                    </v-card>
                </v-dialog>



                <!-- Main Book Info -->
                <v-card>
                    <v-toolbar
                        flat
                        density="compact"
                        :color="store.theme === 'light' ? 'white' : 'grey-darken-4'"
                        class="px-2"
                    >
                        <v-spacer />

                        <!-- Primary 1 [立即操作]: 一键进入沉浸式阅读面板 -->
                        <v-btn
                            color="primary"
                            variant="elevated"
                            class="mx-1 font-weight-bold"
                            :disabled="book.id === 0"
                            :href="is_txt ? '/book/' + book.id + '/readtxt' : '/read/' + book.id"
                            target="_blank"
                            rounded="pill"
                            elevation="2"
                        >
                            <v-icon start>mdi-book-open-page-variant</v-icon>
                            沉浸式閱讀
                        </v-btn>

                        <!-- Primary 2 [深度解析]: 复制 NotebookLM 提示词 -->
                        <v-btn
                            color="primary"
                            variant="tonal"
                            class="mx-1 font-weight-medium"
                            rounded="pill"
                            @click="copyPrompt"
                        >
                            <v-icon v-if="!isCopied" start>mdi-robot-outline</v-icon>
                            {{ isCopied ? '✓ 已複製' : '✨ 複製 AI 助讀提示詞' }}
                        </v-btn>

                        <!-- Primary 3 [常规下载]: 常规打包下载 -->
                        <v-btn
                            color="grey-darken-2"
                            variant="text"
                            class="mx-1 font-weight-medium"
                            rounded="pill"
                            @click="dialog_download = true"
                        >
                            <v-icon start>mdi-cloud-download</v-icon>
                            獲取源文件
                        </v-btn>

                        <template v-if="book.is_owner">
                            <v-menu offset-y>
                                <template #activator="{ props }">
                                    <v-btn
                                        v-bind="props"
                                        variant="text"
                                        class="ml-1"
                                        icon="mdi-dots-vertical"
                                    ></v-btn>
                                </template>
                                <v-list density="compact">
                                    <v-list-item :to="'/book/' + book.id + '/edit'">
                                        <template #prepend>
                                            <v-icon>mdi-cog</v-icon>
                                        </template>
                                        <v-list-item-title>編輯書籍資訊</v-list-item-title>
                                    </v-list-item>

                                    <v-divider />
                                    <v-list-item @click="delete_book">
                                        <template #prepend>
                                            <v-icon color="error">
                                                mdi-delete-forever
                                            </v-icon>
                                        </template>
                                        <v-list-item-title>刪除書籍</v-list-item-title>
                                    </v-list-item>
                                </v-list>
                            </v-menu>
                        </template>
                    </v-toolbar>



                    <v-row>
                        <v-col
                            class="mx-auto"
                            cols="8"
                            sm="4"
                        >
                            <v-img
                                class="book-img"
                                :src="book.img"
                                :aspect-ratio="11 / 15"
                                max-height="500px"
                                contain
                            />
                        </v-col>
                        <v-col
                            cols="12"
                            sm="8"
                        >
                            <v-card-text>
                                <div>
                                    <p class="text-h4 font-weight-bold mb-3" style="letter-spacing: 0.02em; line-height: 1.3;">
                                        {{ book.title }}
                                    </p>
                                    
                                    <!-- Structured Metadata -->
                                    <div class="d-flex flex-wrap align-center pa-3 mb-4 rounded-lg border" style="gap: 16px; border-color: rgba(var(--v-theme-on-surface), 0.08) !important;">
                                        <div class="d-flex align-center">
                                            <v-icon size="small" color="grey-darken-1" class="mr-1">mdi-account</v-icon>
                                            <span class="text-subtitle-2 font-weight-bold text-grey-darken-3">{{ book.author }}</span>
                                        </div>
                                        <div class="d-flex align-center" v-if="pub_year !== 'N/A'">
                                            <v-icon size="small" color="grey-darken-1" class="mr-1">mdi-calendar</v-icon>
                                            <span class="text-subtitle-2 text-grey-darken-3">{{ pub_year }}<span class="d-none d-sm-inline"> 年版</span></span>
                                        </div>
                                        <div class="d-flex align-center" v-if="book.publisher">
                                            <v-icon size="small" color="grey-darken-1" class="mr-1">mdi-domain</v-icon>
                                            <span class="text-subtitle-2 text-grey-darken-3 w-100 text-truncate" style="max-width: 150px;">{{ book.publisher }}</span>
                                        </div>
                                        <div class="d-flex align-center" v-if="book.files && book.files.length > 0">
                                            <v-icon size="small" color="grey-darken-1" class="mr-1">mdi-file-document</v-icon>
                                            <span class="text-subtitle-2 font-weight-bold text-primary">{{ book.files.map(f => f.format).join(', ') }}</span>
                                            <span class="text-caption text-grey ml-1">
                                                <span v-if="book.files[0].size >= 1048576">({{ parseInt(book.files[0].size / 1048576) }}MB)</span>
                                                <span v-else-if="book.files[0].size > 0">({{ parseInt(book.files[0].size / 1024) }}KB)</span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </v-card-text>
                            <v-card-text class="pt-0">
                                <!-- Synopsis Clamp Area -->
                                <div class="text-subtitle-2 font-weight-bold mb-2 mt-2">內容簡介</div>
                                <div class="synopsis-content text-body-1 text-grey-darken-2" style="line-height: 1.8;">
                                    <p
                                        v-if="book.comments"
                                        v-html="book.comments"
                                    />
                                    <p v-else class="text-italic">
                                        無簡介資料
                                    </p>
                                </div>
                            </v-card-text>
                        </v-col>
                    </v-row>
                </v-card>
            </v-col>
        </v-row>



        <!-- Tags Section (Slim Version) -->
        <v-row class="mt-4" v-if="book.tags && book.tags.length > 0">
            <v-col cols="12">
                <v-card variant="text">
                    <v-card-text class="px-0 py-2">
                        <div class="d-flex align-center flex-wrap ga-2">
                            <span class="text-caption text-grey font-weight-bold mr-2"><v-icon size="small">mdi-bookshelf</v-icon> 主題分類:</span>
                            <v-chip
                                v-for="tag in book.tags.slice(0, 5)"
                                :key="'tag-' + tag"
                                size="small"
                                color="grey-darken-2"
                                variant="tonal"
                                :to="'/tag/' + encodeURIComponent(tag)"
                            >
                                {{ tag }}
                            </v-chip>
                            <span v-if="book.tags.length > 5" class="text-caption text-grey ml-1">+{{ book.tags.length - 5 }}</span>
                        </div>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { useAsyncData, useCookie, useNuxtApp } from 'nuxt/app';
import { useMainStore } from '@/stores/main';
import BookCards from '~/components/BookCards.vue';

const route = useRoute();
const router = useRouter();
const store = useMainStore();
const { $backend, $alert } = useNuxtApp();
const { t } = useI18n();
const cookie = useCookie('last_mailto');

const bookid = route.params.bid;
const book = ref({
    id: 0,
    title: '',
    files: [],
    tags: [],
    pubdate: '',
    authors: [],
    publisher: '',
    comments: '',
    rating: 0,
    img: '',
    isbn: '',
    collector: '',
    timestamp: '',
    is_owner: false,
    series: ''
});

// Dialogs
const dialog_download = ref(false);
const dialog_kindle = ref(false);

// Kindle
const mail_to = ref('');
const kindle_sender = ref('');

// NotebookLM Prompt
const isCopied = ref(false);
const getAIPrompt = (bookTitle) => `# Role: 首席閱讀助理與知識萃取專家

# Goal
你是一位具備頂級結構化思維的書籍分析師。你的任務是深度拆解我提供的文本，並輸出結構嚴謹、邏輯清晰的分析報告。這份報告將直接存入我的個人數位圖書館，並為 NotebookLM 等 RAG 系統進行最佳化。

# Constraints & Output Rules
- **Target Language**: 所有輸出內容（包含思考過程後的最終報告）必須使用流暢的繁體中文 (Traditional Chinese)。
- **Source Fidelity**: 嚴格基於提供的文本進行分析，絕不憑空捏造 (No hallucinations)。
- **Citations**: 必須善用 NotebookLM 的原生引用功能。在每個核心觀點、定義或重要引述後，標註來源以確保可追溯性。
- **Thinking Process**: 在生成最終報告前，請先使用 <think> 標籤，用英文簡述你的拆解邏輯與全書框架。
Formatting: 嚴格遵守下方的 Markdown 模板格式，確保乾淨、可直接複製。

---

在完成之後，請嚴格按照以下 6 個模塊輸出繁體中文報告：

書籍基本檔案
書名：${bookTitle}
核心分類：[虛構類 Fiction / 非虛構類 Non-Fiction / 技術類 Technical]
一句話推薦：[高度凝練的 1 句話總結其核心價值，適合用作圖書館索引]

核心論點與寫作意圖
寫作意圖：[作者為什麼寫這本書？為了解決什麼問題，或挑戰了什麼既定認知？]
全書主旨：[用 1-2 句話精準概括全書的最核心論點]

表達結構與內容骨架
全局架構：[宏觀敘事是如何組織的？例如："問題 -> 歸因 -> 解法" 或 "歷史 -> 現狀 -> 未來"]
脈絡拆解：[用條列式拆解核心章節之間的邏輯關聯]

關鍵知識點與洞察
(深度萃取 5-7 個書中最具顛覆性或實用價值的概念)
[概念標題 1]：詳細拆解該概念的運作機制，並結合書中具體案例說明。
[概念標題 2]：詳細拆解該概念的運作機制，並結合書中具體案例說明。
(以此類推)

邏輯評估與受眾分析
論證手法：[作者如何說服讀者？依靠數據、案例還是哲學思辨？]
護城河與局限：[論證最堅固的地方在哪？是否有時代侷限、預設門檻過高或理論難以落地？]
精準推薦：[什麼樣背景或面臨什麼困境的人，最應該立刻閱讀此書？]

思想火花與實踐指南
金句摘錄：[提取 3-5 句最能引發共鳴或深思的原文原話]
實作與啟發：[對於非虛構類：讀者可以立即採取的行動指南是什麼？對於虛構/哲學類：它帶來了什麼底層世界觀的轉變？]`;

const copyPrompt = () => {
    const payload = getAIPrompt(book.value.title);
    navigator.clipboard.writeText(payload);
    isCopied.value = true;
    setTimeout(() => {
        isCopied.value = false;
    }, 2000);
};

// TXT
const txt_parse_inited = ref(false);

// 数据获取状态
const pending = ref(true);
const error = ref(null);

store.setNavbar(true);

// Methods
const get_txt_parse_status = async () => {
    try {
        const res = await $backend(`/book/txt/init?id=${bookid}&test=1`);
        if (res.err === 'ok' && res.msg === '已解析') {
            txt_parse_inited.value = true;
        }
    } catch (e) {
        console.error(e);
    }
};

// 数据获取逻辑
const { data: fetchData, error: fetchError, pending: fetchPending } = useAsyncData(`book-${bookid}`, async () => {
    const response = await $backend(`/book/${bookid}`);
    
    if (response.err === 'ok') {
        return response;
    } else {
        throw new Error(response.msg || '获取书籍信息失败');
    }
});

// 监听数据变化
watch(() => fetchData.value, (newData) => {
    if (newData && newData.book) {
        book.value = newData.book;
        mail_to.value = newData.user?.kindle_email || '';
        kindle_sender.value = newData.kindle_sender || '';
        
        if (cookie.value) {
            mail_to.value = cookie.value;
        }
        
        // 获取 TXT 解析状态
        get_txt_parse_status();
    }
}, { immediate: true });

// 监听错误状态
watch(() => fetchError.value, (newError) => {
    error.value = newError;
    if (newError && $alert) {
        $alert('error', newError.message || '获取书籍信息失败');
    }
});

// 监听加载状态
watch(() => fetchPending.value, (newPending) => {
    pending.value = newPending;
});

// Computed properties
const pub_year = computed(() => {
    if (!book.value || !book.value.pubdate) {
        return 'N/A';
    }
    return book.value.pubdate.split('-')[0];
});

const is_txt = computed(() => {
    if (!book.value || !book.value.files) return false;
    const formats = book.value.files.map(x => x.format.toLowerCase());
    return formats.includes('txt');
});

const email_items = computed(() => {
    const emails = [mail_to.value].filter(Boolean);
    if (cookie.value && !emails.includes(cookie.value)) {
        emails.push(cookie.value);
    }
    return emails;
});

useHead({
    title: () => book.value.title || '書籍資訊'
});

// Other methods
const sendto_kindle = async () => {
    if (!mail_to.value) {
        if ($alert) $alert('error', '请填写邮箱地址');
        return;
    }

    cookie.value = mail_to.value;

    try {
        const rsp = await $backend(`/book/${bookid}/push`, {
            method: 'POST',
            body: `mail_to=${encodeURIComponent(mail_to.value)}`,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });

        dialog_kindle.value = false;
        if (rsp.err === 'ok') {
            if ($alert) $alert('success', rsp.msg, '#');
        } else {
            if ($alert) $alert('error', rsp.msg, '#');
        }
    } catch (e) {
        if ($alert) $alert('error', '发送失败');
    }
};



const delete_book = async () => {
    if (!confirm('确定要删除这本书吗？')) return;

    try {
        const rsp = await $backend(`/book/${bookid}/delete`, {
            method: 'POST',
        });

        if (rsp.err === 'ok') {
            if ($alert) $alert('success', '删除成功');
            router.push('/');
        } else {
            if ($alert) $alert('error', rsp.msg);
        }
    } catch (e) {
        if ($alert) $alert('error', '删除失败');
    }
};

const check_email = (email) => {
    if (email === kindle_sender.value) {
        return '发件邮件不可作为收件人';
    }
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email) || 'Email格式错误';
};
</script>

<style scoped>
.book-img {
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.align-right {
    text-align: right;
}

.book-footer {
    padding-top: 0;
    padding-bottom: 3px;
}

.synopsis-content p {
    margin-bottom: 12px;
}

/* 减小管理菜单图标和文字的间距 */
:deep(.v-list-item__spacer) {
    width: 8px !important;
}
</style>