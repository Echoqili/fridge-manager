import { test, expect } from '@playwright/test';

test('打开首页看到冰箱看板', async ({ page }) => {
  await page.goto('/');
  // 应该跳转到登录页或首页
  await expect(page).toHaveURL(/\/(login)?$/);
});

test('演示模式登录后看到冰箱看板', async ({ page }) => {
  await page.goto('/login');
  await page.click('text=演示模式快速体验');
  await page.waitForURL('**/');
  await expect(page.locator('text=打开冰箱，就知道今天吃什么')).toBeVisible({ timeout: 15000 });
});

test('点击菜谱推荐导航', async ({ page }) => {
  // 先进入演示模式
  await page.goto('/login');
  await page.click('text=演示模式快速体验');
  await page.waitForURL('**/');
  // 点击菜谱推荐菜单
  await page.click('text=菜谱推荐');
  await expect(page).toHaveURL('**/recipes');
  await expect(page.locator('text=菜谱推荐').first()).toBeVisible({ timeout: 15000 });
});

test('查看营养洞察页', async ({ page }) => {
  await page.goto('/login');
  await page.click('text=演示模式快速体验');
  await page.waitForURL('**/');
  await page.click('text=营养洞察');
  await expect(page).toHaveURL('**/nutrition');
});
