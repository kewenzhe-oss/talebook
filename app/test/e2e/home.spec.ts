
import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const mockDir = path.join(__dirname, 'mocks');
const apiIndex = JSON.parse(fs.readFileSync(path.join(mockDir, 'api_index.json'), 'utf-8'));

test.describe('Homepage', () => {
    test.beforeEach(async ({ request }) => {
    // Reset mock server to installed state
        const response = await request.post('http://127.0.0.1:8000/_test/reset', {
            data: { installed: true }
        });
        expect(response.ok()).toBeTruthy();
    });

    test('displays hero search and recent books', async ({ page }) => {
        await page.goto('/');

        // Check Hero Search area
        await expect(page.getByText('探索您的数字书房')).toBeVisible();
        await expect(page.locator('input[type="text"]').first()).toBeVisible();

        // Check "最近入库" section
        await expect(page.getByText('最近入库')).toBeVisible();

        // Check if at least one book from recent books is visible
        if (apiIndex.recent_books && apiIndex.recent_books.length > 0) {
            const firstBook = apiIndex.recent_books[0];
            await expect(page.getByText(firstBook.title).first()).toBeVisible();
        }
    });

    test('hero search navigates to search page', async ({ page }) => {
        await page.goto('/');

        const searchInput = page.locator('input[type="text"]').first();
        await searchInput.fill('百年孤独');
        await searchInput.press('Enter');

        // Should navigate to /search?name=百年孤独
        await expect(page).toHaveURL(/\/search\?name=/);
    });
});
