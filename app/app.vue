<template>
    <NuxtLayout>
        <NuxtPage />
    </NuxtLayout>
</template>

<style>
/* Color system variables */
:root {
  --bg-canvas: #F6F6F3;
  --bg-sidebar: #ECECE8;
  --bg-surface: #FFFFFF;
  --bg-surface-raised: #FFFFFF;
  --bg-muted: #EFEFEB;
  --border-subtle: #DDDCD6;
  --border-strong: #CAC9C2;

  --text-primary: #20201D;
  --text-secondary: #5E5E57;
  --text-tertiary: #7B7B73;
  --text-disabled: #A4A49C;

  --accent: #3B82C4;
  --accent-hover: #256AA7;
  --accent-soft: rgba(59, 130, 196, 0.12);
  --focus-ring: rgba(59, 130, 196, 0.22);
  
  color-scheme: light dark;
}

.v-theme--dark {
  --bg-canvas: #141414;
  --bg-sidebar: #1B1B1B;
  --bg-surface: #212121;
  --bg-surface-raised: #292929;
  --bg-muted: #252525;
  --border-subtle: #353535;
  --border-strong: #484848;

  --text-primary: #F4F4F0;
  --text-secondary: #C7C7C1;
  --text-tertiary: #969690;
  --text-disabled: #656560;

  --accent: #78B9F2;
  --accent-hover: #9CCCF7;
  --accent-soft: rgba(120, 185, 242, 0.14);
  --focus-ring: rgba(120, 185, 242, 0.20);
}

/* Global utility classes */
.bg-canvas {
  background-color: var(--bg-canvas) !important;
}
.bg-sidebar {
  background-color: var(--bg-sidebar) !important;
}
.bg-surface {
  background-color: var(--bg-surface) !important;
}
.bg-surface-raised {
  background-color: var(--bg-surface-raised) !important;
}
.bg-muted {
  background-color: var(--bg-muted) !important;
}
.border-subtle {
  border: 1px solid var(--border-subtle) !important;
}
.border-subtle-b {
  border-bottom: 1px solid var(--border-subtle) !important;
}
.border-strong {
  border: 1px solid var(--border-strong) !important;
}
.text-primary {
  color: var(--text-primary) !important;
}
.text-secondary {
  color: var(--text-secondary) !important;
}
.text-tertiary {
  color: var(--text-tertiary) !important;
}
.text-disabled {
  color: var(--text-disabled) !important;
}
.text-accent {
  color: var(--accent) !important;
}
.bg-accent {
  background-color: var(--accent) !important;
}
.bg-accent-soft {
  background-color: var(--accent-soft) !important;
}

/* Custom Scrollbars */
* {
  scrollbar-color: var(--border-strong) var(--bg-canvas);
  scrollbar-width: thin;
}

/* Legacy webkit scrollbars override */
@supports not (scrollbar-color: auto) {
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  ::-webkit-scrollbar-track {
    background: var(--bg-canvas);
  }
  ::-webkit-scrollbar-thumb {
    background: var(--border-strong);
    border-radius: 4px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: var(--text-tertiary);
  }
}

/* 全局样式：为所有卡片标题添加顶部空隙 */
.v-card-title {
  padding-top: 16px !important;
}

/* 公告内容链接样式 */
.press-content a,
a.press-content {
  color: var(--accent) !important;
}
</style>
