import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import RecipesPage from './pages/RecipesPage';
import NutritionPage from './pages/NutritionPage';
import AuthPage from './pages/AuthPage';
import { useApp } from './contexts/AppContext';
import { TOKEN_KEY } from './config';

function ProtectedRoute({ children }) {
  const { user } = useApp();
  // 兜底检查 localStorage token，避免登录导航时 user 状态尚未提交导致误重定向
  const hasToken = localStorage.getItem(TOKEN_KEY);
  if (!user && !hasToken) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<HomePage />} />
        <Route path="recipes" element={<RecipesPage />} />
        <Route path="nutrition" element={<NutritionPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
