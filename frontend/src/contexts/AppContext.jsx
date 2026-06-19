import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import * as authApi from '../api/auth';
import * as ingredientApi from '../api/ingredients';
import { TOKEN_KEY, USER_KEY } from '../config';

export const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem(USER_KEY);
    return stored ? JSON.parse(stored) : null;
  });
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(false);

  // 登录
  const login = useCallback(async (credentials) => {
    const data = await authApi.login(credentials);
    const { access_token, user: userInfo } = data;
    localStorage.setItem(TOKEN_KEY, access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(userInfo));
    setUser(userInfo);
    return userInfo;
  }, []);

  // 登出
  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch (e) {
      // 忽略登出接口错误
    }
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
    setIngredients([]);
  }, []);

  // 刷新食材列表
  const refreshIngredients = useCallback(async () => {
    if (!user) return [];
    setLoading(true);
    try {
      const data = await ingredientApi.getIngredients();
      const list = Array.isArray(data) ? data : data?.items || [];
      setIngredients(list);
      return list;
    } catch (e) {
      return [];
    } finally {
      setLoading(false);
    }
  }, [user]);

  // 添加食材
  const addIngredient = useCallback(async (ingredient) => {
    const created = await ingredientApi.createIngredient(ingredient);
    setIngredients((prev) => [...prev, created]);
    return created;
  }, []);

  // 移除食材
  const removeIngredient = useCallback(async (id) => {
    await ingredientApi.deleteIngredient(id);
    setIngredients((prev) => prev.filter((item) => item.ingredient_id !== id && item.id !== id));
  }, []);

  // 更新食材
  const updateIngredient = useCallback(async (id, data) => {
    const updated = await ingredientApi.updateIngredient(id, data);
    setIngredients((prev) =>
      prev.map((item) =>
        (item.ingredient_id === id || item.id === id) ? { ...item, ...updated } : item
      )
    );
    return updated;
  }, []);

  // 登录后加载食材
  useEffect(() => {
    if (user) {
      refreshIngredients();
    }
  }, [user, refreshIngredients]);

  const value = {
    user,
    ingredients,
    loading,
    login,
    logout,
    refreshIngredients,
    addIngredient,
    removeIngredient,
    updateIngredient,
    setIngredients
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) {
    throw new Error('useApp 必须在 AppProvider 内使用');
  }
  return ctx;
}

export default AppContext;
