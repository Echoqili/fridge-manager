import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { ConfigProvider } from 'antd';
import RecipesPage from '../src/pages/RecipesPage';
import { AppContext } from '../src/contexts/AppContext';
import { recommendRecipes, getRecipeById } from '../src/api/recipes';

vi.mock('../src/api/recipes', () => ({
  recommendRecipes: vi.fn(),
  getRecipeById: vi.fn()
}));

function renderPage(contextValue = {}) {
  const value = {
    ingredients: [],
    ...contextValue
  };
  return render(
    <ConfigProvider>
      <AppContext.Provider value={value}>
        <RecipesPage />
      </AppContext.Provider>
    </ConfigProvider>
  );
}

describe('RecipesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('渲染页面标题和副标题', () => {
    recommendRecipes.mockResolvedValue([]);
    renderPage();
    expect(screen.getByText('菜谱推荐')).toBeInTheDocument();
    expect(screen.getByText('根据你的冰箱食材，AI 为你推荐最合适的菜谱')).toBeInTheDocument();
  });

  it('初始加载时显示 loading', () => {
    recommendRecipes.mockReturnValue(new Promise(() => {}));
    renderPage();
    expect(document.querySelector('.ant-spin-spinning')).toBeInTheDocument();
  });

  it('API 返回推荐菜谱时渲染卡片', async () => {
    recommendRecipes.mockResolvedValue([
      {
        recipe_id: 'api1',
        name: 'API 测试菜',
        tags: ['测试'],
        cook_time: 5,
        calories: 100,
        servings: 1,
        need: ['鸡蛋'],
        steps: ['测试步骤']
      }
    ]);
    renderPage({ ingredients: [{ name: '鸡蛋' }] });
    await waitFor(() => {
      expect(screen.getByText('API 测试菜')).toBeInTheDocument();
    });
    expect(recommendRecipes).toHaveBeenCalledWith({ ingredients: ['鸡蛋'] });
  });

  it('API 失败时使用本地兜底菜谱', async () => {
    recommendRecipes.mockRejectedValue(new Error('network error'));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText('西红柿炒鸡蛋')).toBeInTheDocument();
    });
    expect(screen.getByText('土豆炖牛肉')).toBeInTheDocument();
  });

  it('API 返回空时回退到本地兜底菜谱', async () => {
    recommendRecipes.mockResolvedValue([]);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText('西红柿炒鸡蛋')).toBeInTheDocument();
    });
    expect(screen.getByText('土豆炖牛肉')).toBeInTheDocument();
  });

  it('点击菜谱卡片进入详情并展示步骤', async () => {
    recommendRecipes.mockResolvedValue([
      {
        recipe_id: 'r1',
        name: '西红柿炒鸡蛋',
        tags: ['家常'],
        cook_time: 10,
        calories: 280,
        servings: 2,
        need: ['西红柿', '鸡蛋'],
        steps: ['步骤一', '步骤二']
      }
    ]);
    getRecipeById.mockResolvedValue({
      recipe_id: 'r1',
      name: '西红柿炒鸡蛋',
      need: ['西红柿', '鸡蛋'],
      steps: ['后端步骤一', '后端步骤二']
    });

    renderPage({ ingredients: [{ name: '西红柿' }] });
    await waitFor(() => {
      expect(screen.getByText('西红柿炒鸡蛋')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('recipe-card'));

    await waitFor(() => {
      expect(screen.getByText('所需食材：')).toBeInTheDocument();
    });
    expect(screen.getByText('西红柿')).toBeInTheDocument();
    expect(screen.getByText('鸡蛋')).toBeInTheDocument();
    expect(screen.getByText('烹饪步骤：')).toBeInTheDocument();
    expect(screen.getByText('后端步骤一')).toBeInTheDocument();
  });

  it('详情页点击返回回到列表', async () => {
    recommendRecipes.mockResolvedValue([
      {
        recipe_id: 'r1',
        name: '西红柿炒鸡蛋',
        tags: ['家常'],
        cook_time: 10,
        calories: 280,
        servings: 2,
        need: ['西红柿'],
        steps: ['步骤一']
      }
    ]);
    getRecipeById.mockResolvedValue({ recipe_id: 'r1', steps: ['步骤一'] });

    renderPage({ ingredients: [{ name: '西红柿' }] });
    await waitFor(() => {
      expect(screen.getByText('西红柿炒鸡蛋')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('recipe-card'));
    await waitFor(() => {
      expect(screen.getByText('返回列表')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('返回列表'));
    await waitFor(() => {
      expect(screen.getByText('根据你的冰箱食材，AI 为你推荐最合适的菜谱')).toBeInTheDocument();
    });
  });
});
