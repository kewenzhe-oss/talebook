<template>
    <div class="category-editor pt-4">
        <v-alert
            v-if="!modelValue || modelValue.length === 0"
            color="warning"
            icon="mdi-alert"
            class="mb-4"
            variant="tonal"
        >
            <div class="d-flex align-center justify-space-between">
                <div>
                    未检测到新版分类数据。你可以从旧版 BOOK_NAV 文本配置进行一键迁移。
                </div>
                <v-btn color="primary" @click="migrateFromOld" :loading="migrating">
                    开始迁移
                </v-btn>
            </div>
        </v-alert>

        <div class="d-flex align-center justify-space-between mb-4">
            <h3 class="text-h6">前台分离与规则配置</h3>
            <v-btn color="primary" @click="openEditDialog()">
                <v-icon start>mdi-plus</v-icon> 添加主分类
            </v-btn>
        </div>

        <v-expansion-panels v-if="modelValue && modelValue.length > 0">
            <v-expansion-panel
                v-for="(cat, idx) in modelValue"
                :key="cat.id || idx"
            >
                <v-expansion-panel-title>
                    <v-icon :color="cat.color || 'primary'" class="mr-3">{{ cat.icon || 'mdi-folder' }}</v-icon>
                    <strong>{{ cat.name }}</strong>
                    <v-chip size="small" class="ml-3" v-if="!cat.enabled" color="error">已停用</v-chip>
                    <v-spacer></v-spacer>
                    <span class="text-caption text-grey mr-4">ID: {{ cat.id }}</span>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                    <div class="d-flex justify-end mb-2 pt-2">
                        <v-btn size="small" variant="text" color="primary" @click="openEditDialog(cat, idx)">编辑分类</v-btn>
                        <v-btn size="small" variant="text" color="error" @click="deleteCategory(idx)">删除</v-btn>
                    </div>
                    
                    <div class="rules-container pl-4 border-s-sm border-primary">
                        <div class="text-subtitle-2 mb-2">匹配规则 ({{ cat.match_rules ? cat.match_rules.length : 0 }} 条)</div>
                        <v-card 
                            v-for="(rule, rhIdx) in (cat.match_rules || [])" 
                            :key="rhIdx" 
                            variant="outlined" 
                            class="mb-2 pa-2"
                            :color="rule.enabled ? '' : 'grey'"
                        >
                            <div class="d-flex text-body-2">
                                <div style="min-width: 80px" class="font-weight-bold">关键词:</div>
                                <div>
                                    <v-chip size="x-small" v-for="(k, kid) in rule.keywords" :key="kid" class="mr-1 mb-1">{{ k }}</v-chip>
                                </div>
                            </div>
                            <div class="d-flex text-body-2 mt-1">
                                <div style="min-width: 80px" class="font-weight-bold">匹配字段:</div>
                                <div>{{ (rule.match_fields || []).join(', ') }}</div>
                            </div>
                            <div class="d-flex text-body-2 mt-1" v-if="rule.exclude_keywords && rule.exclude_keywords.length > 0">
                                <div style="min-width: 80px" class="font-weight-bold text-error">排除词:</div>
                                <div>{{ rule.exclude_keywords.join(', ') }}</div>
                            </div>
                        </v-card>
                    </div>

                    <!-- 子分类暂时隐藏渲染以保持UI简单，可以扩展 -->
                </v-expansion-panel-text>
            </v-expansion-panel>
        </v-expansion-panels>
        <div v-else class="text-center text-grey py-8">
            暂无分类配置
        </div>

        <div class="mt-4 pt-4 border-t">
            <v-btn block color="secondary" variant="tonal" @click="previewHits" :loading="previewing">
                <v-icon start>mdi-eye-check</v-icon> 预览全库命中情况
            </v-btn>
        </div>

        <!-- 编辑弹窗 -->
        <v-dialog v-model="editDialog" max-width="600px" persistent>
            <v-card>
                <v-card-title>{{ editingIdx > -1 ? '编辑分类' : '添加主分类' }}</v-card-title>
                <v-card-text>
                    <v-text-field v-model="editForm.name" label="分类名称 (如: 编程)" required></v-text-field>
                    <v-text-field v-model="editForm.id" label="URL/ID标识 (如: coding)" required></v-text-field>
                    <v-row>
                        <v-col cols="6">
                            <v-text-field v-model="editForm.icon" label="MDI 图标 (如: mdi-code-tags)"></v-text-field>
                        </v-col>
                        <v-col cols="6">
                            <v-text-field v-model="editForm.color" label="颜色 (如: primary)"></v-text-field>
                        </v-col>
                    </v-row>
                    <v-switch v-model="editForm.enabled" label="前台启用可见" color="primary"></v-switch>

                    <v-divider class="my-4"></v-divider>
                    <div class="d-flex align-center justify-space-between mb-2">
                        <h4 class="text-subtitle-1">匹配规则</h4>
                        <v-btn size="small" variant="text" @click="addRule">添加规则</v-btn>
                    </div>

                    <v-card v-for="(rule, ridx) in editForm.match_rules" :key="ridx" class="pa-3 mb-3" variant="outlined">
                        <div class="d-flex justify-space-between align-center mb-2">
                            <strong>规则 #{{ ridx + 1 }}</strong>
                            <v-btn size="small" icon="mdi-delete" variant="text" color="error" @click="removeRule(ridx)"></v-btn>
                        </div>
                        <v-textarea 
                            v-model="editRuleTexts[ridx].keywords" 
                            label="触发关键词 (逗号、空格或换行分隔)" 
                            rows="2" 
                            density="compact"
                        ></v-textarea>
                        
                        <v-select
                            v-model="rule.match_fields"
                            :items="['tags', 'title', 'author']"
                            label="检测以下字段"
                            multiple
                            chips
                            density="compact"
                        ></v-select>

                        <v-text-field
                            v-model="editRuleTexts[ridx].exclude"
                            label="排除词 (如有这些词则跳过，逗号分隔)"
                            density="compact"
                        ></v-text-field>
                        
                        <v-switch v-model="rule.enabled" label="启用此规则" density="compact" hide-details></v-switch>
                    </v-card>

                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn variant="text" @click="editDialog = false">取消</v-btn>
                    <v-btn color="primary" @click="saveEdit">确认</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- 预览弹窗 -->
        <v-dialog v-model="previewDialog" max-width="800px">
            <v-card>
                <v-card-title>全库命中预测 (基于当前尚未保存的配置)</v-card-title>
                <v-card-text v-if="previewResults">
                    <v-alert type="info" variant="text" class="mb-4">
                        测试了全库书籍并计算动态视图归属结果，这不是对原始书库标签的修改。
                    </v-alert>
                    <v-data-table
                        :items="previewResults"
                        :headers="[
                            { title: '被命中的分类', key: 'category_name' },
                            { title: '致效词', key: 'matched_keyword' },
                            { title: '命中字段', key: 'matched_field' },
                            { title: '书名', key: 'book' },
                        ]"
                        items-per-page="10"
                        class="elevation-1"
                    >
                    </v-data-table>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" @click="previewDialog = false">关闭</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
    modelValue: {
        type: Array,
        default: () => []
    }
});

const emit = defineEmits(['update:modelValue']);

// Local state
const config = ref([]);
const migrating = ref(false);
const previewing = ref(false);

const editDialog = ref(false);
const editingIdx = ref(-1);
const editForm = ref({});
const editRuleTexts = ref([]);

const previewDialog = ref(false);
const previewResults = ref([]);

watch(() => props.modelValue, (val) => {
    config.value = JSON.parse(JSON.stringify(val || []));
}, { immediate: true, deep: true });

function updateModel() {
    emit('update:modelValue', config.value);
}

async function migrateFromOld() {
    migrating.value = true;
    try {
        const fetchMethod = $fetch || fetch; // Nuxt 3 uses $fetch globally, fallback to fetch
        const res = await fetchMethod('/api/admin/categories/migrate', {
            method: 'POST'
        });
        const data = res.err ? res : await res.json();
        
        if (data.err === 'ok' && data.categories) {
            config.value = data.categories;
            updateModel();
        } else {
            console.error('Migration failed', data);
            alert('迁移失败: ' + (data.msg || '未知错误'));
        }
    } catch (e) {
        console.error(e);
        alert('网络请求失败');
    } finally {
        migrating.value = false;
    }
}

async function previewHits() {
    previewing.value = true;
    try {
        const fetchMethod = $fetch || fetch;
        const res = await fetchMethod('/api/admin/categories/preview', {
            method: 'POST',
            body: JSON.stringify({ categories: config.value })
        });
        const data = res.err ? res : await res.json();

        if (data.err === 'ok' && data.results) {
            // Flatten results for table
            const flatResults = [];
            data.results.forEach(b => {
                b.hits.forEach(h => {
                    flatResults.push({
                        category_name: h.category_name,
                        matched_keyword: h.matched_keyword,
                        matched_field: h.matched_field,
                        book: b.title
                    });
                });
            });
            previewResults.value = flatResults;
            previewDialog.value = true;
        } else {
            alert('获取预览失败');
        }
    } catch (e) {
        console.error(e);
        alert('网络请求失败');
    } finally {
        previewing.value = false;
    }
}

function openEditDialog(cat = null, idx = -1) {
    editingIdx.value = idx;
    if (cat) {
        editForm.value = JSON.parse(JSON.stringify(cat));
    } else {
        editForm.value = {
            id: '', name: '', icon: 'mdi-folder', color: 'primary',
            enabled: true, sort_order: config.value.length + 1,
            match_rules: [], children: []
        };
    }
    
    // Parse keywords arrays to text for editing
    editRuleTexts.value = (editForm.value.match_rules || []).map(r => ({
        keywords: r.keywords.join(', '),
        exclude: (r.exclude_keywords || []).join(', ')
    }));
    
    editDialog.value = true;
}

function addRule() {
    if (!editForm.value.match_rules) editForm.value.match_rules = [];
    editForm.value.match_rules.push({
        id: 'rule_' + Date.now(),
        keywords: [],
        match_fields: ['tags', 'title'],
        exclude_keywords: [],
        enabled: true
    });
    editRuleTexts.value.push({ keywords: '', exclude: '' });
}

function removeRule(idx) {
    editForm.value.match_rules.splice(idx, 1);
    editRuleTexts.value.splice(idx, 1);
}

function saveEdit() {
    // Parse texts back to arrays
    editForm.value.match_rules.forEach((r, idx) => {
        const textObj = editRuleTexts.value[idx];
        r.keywords = textObj.keywords.split(/[\s,，]+/).map(s => s.trim()).filter(s => s);
        r.exclude_keywords = textObj.exclude.split(/[\s,，]+/).map(s => s.trim()).filter(s => s);
    });

    if (editingIdx.value > -1) {
        config.value[editingIdx.value] = editForm.value;
    } else {
        config.value.push(editForm.value);
    }
    
    updateModel();
    editDialog.value = false;
}

function deleteCategory(idx) {
    if(confirm('确认删除此主分类吗？')) {
        config.value.splice(idx, 1);
        updateModel();
    }
}

</script>

<style scoped>
.category-editor {
    width: 100%;
}
</style>
