
import { test, expect } from '@playwright/test';

test.describe('Navigation Sidebar', () => {
    test.beforeEach(async ({ request }) => {
    // Ensure installed
        await request.post('http://127.0.0.1:8000/_test/reset', {
            data: { installed: true }
        });
    });

    test('Check all sidebar links', async ({ page }) => {
        await page.goto('/');

        // 1. Home
        await expect(page.locator('nav').getByRole('link', { name: '首页' })).toBeVisible();
        await expect(page.locator('nav').getByRole('link', { name: '首页' })).toHaveAttribute('href', '/');

        // 2. Library
        await expect(page.locator('nav').getByRole('link', { name: '书库' })).toBeVisible();
        await expect(page.locator('nav').getByRole('link', { name: '书库' })).toHaveAttribute('href', '/library');

        // 3. Category Links (only publisher, tags, formats)
        const links = [
            { name: '出版社', href: '/publisher' },
            { name: '标签', href: '/tag' },
            { name: '文件格式', href: '/format' },
        ];

        for (const link of links) {
            await expect(page.locator('nav').getByRole('link', { name: link.name })).toBeVisible();
            await expect(page.locator('nav').getByRole('link', { name: link.name })).toHaveAttribute('href', link.href);
        }

        // 4. Hidden items should NOT be visible
        const hiddenLinks = ['分类导览', '作者', '丛书', '评分', '热度榜单', '所有书籍'];
        for (const name of hiddenLinks) {
            await expect(page.locator('nav').getByRole('link', { name })).not.toBeVisible();
        }
    });

    test('Can navigate via all sidebar links', async ({ page }) => {
    // Define all links to test
        const linksToTest = [
            { name: '书库', url: '/library', expectedText: '书库' },
            { name: '出版社', url: '/publisher', expectedText: '出版社' },
            { name: '标签', url: '/tag', expectedText: '标签' },
            { name: '文件格式', url: '/format', expectedText: '文件格式' },
        ];

        for (const link of linksToTest) {
            await page.goto('/');
            console.log(`Testing navigation to ${link.name}...`);
        
            const navLink = page.locator('nav').getByRole('link', { name: link.name });
            await navLink.waitFor({ state: 'visible' });
            await navLink.click();
        
            await expect(page).toHaveURL(link.url);
            await expect(page.getByText(link.expectedText).first()).toBeVisible();
        }
    });
});

