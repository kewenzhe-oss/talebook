<template>
    <v-row>
        <v-col
            cols="12"
            class="text-center"
        >
            <v-divider class="mt-10 mb-3" />
            <p
                v-if="footer_extra_html"
                class="mb-0 text-center footer-text press-content"
                v-html="footer_extra_html"
            />
            <p
                class="mb-0 text-center footer-text press-content"
                v-html="footer_text"
            />
            <p>
                <v-btn
                    small
                    variant="text"
                    target="_blank"
                    href="https://www.postsoma-2050.com/"
                    class="text-grey-darken-1 font-weight-light"
                    style="letter-spacing: 0.05em;"
                >
                    POSTSOMA-2050
                </v-btn>
            </p>
        </v-col>
    </v-row>
</template>

<script setup>
import { useMainStore } from '@/stores/main';

const store = useMainStore();
const footer_text = computed(() => store.sys.footer || '');
const footer_extra_html = computed(() => store.sys.footer_extra_html || '');
</script>

<style>

</style>
