# 鲜知 fridge · AI 冰箱管家

> TRAE AI 创造力大赛 Demo —— 用 AI 让冰箱开口说话，打开冰箱就知道今天吃什么。

## 在线预览

🔗 https://echoqili.github.io/fridge-manager-demo/

## 项目简介

鲜知 fridge 是一个面向家庭厨房的 AI 冰箱管家，通过拍照识别、智能库存管理和 AI 菜谱推荐，帮助用户减少食材浪费、优化膳食搭配，让每一餐都更简单、更健康。

## 功能亮点

- **📸 拍照识食材**：上传冰箱照片，AI 自动识别食材种类、数量与建议存放位置
- **🧊 智能库存**：可视化冰箱分区（冷藏室、冷冻室、蔬果室、pantry），食材一目了然
- **⏰ 临期提醒**：自动标记即将过期的食材，优先消耗，减少浪费
- **✨ AI 菜谱推荐**：根据现有食材智能推荐菜谱，优先使用临期食材
- **🛒 购物清单**：基于推荐菜谱自动生成缺失食材的购物清单
- **📊 营养洞察**：统计蔬菜、肉蛋奶、主食、水果摄入，并给出 AI 饮食建议

## 技术栈

### 前端
- React 18 + Vite 5 + Ant Design 5
- React Router 6 + Axios + ECharts
- Vitest + Testing Library + Playwright

### 后端
- FastAPI + SQLAlchemy 2.0 (async) + SQLite
- Pydantic 2 + python-jose (JWT) + passlib (bcrypt)
- OpenAI / 智谱 GLM-4V 多模态 AI
- Alembic 数据库迁移 + Ruff + Bandit

### 基础设施
- Docker + docker-compose
- GitHub Actions CI/CD
- GitHub Pages 部署

## 项目结构

```
fridge-manager-demo/
├── backend/              # FastAPI 后端
│   ├── core/             # 配置、安全、异常
│   ├── models/           # ORM 模型
│   ├── schemas/          # Pydantic 模型
│   ├── services/         # 业务逻辑层
│   ├── routers/          # API 路由
│   ├── tests/            # 单元测试
│   └── main.py           # 应用入口
├── frontend/             # React 前端
│   ├── src/api/          # API 调用层
│   ├── src/components/   # 通用组件
│   ├── src/pages/        # 页面组件
│   ├── src/contexts/     # 状态管理
│   └── src/styles/       # 主题样式
├── docs/                 # 设计规范文档
├── Dockerfile            # 后端容器化
├── docker-compose.yml    # 全栈编排
└── .github/workflows/    # CI/CD 流水线
```

## 本地开发

### 环境要求
- Python 3.10+
- Node.js 20+
- Git

### 后端启动

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
pip install -r requirements-test.txt

cp .env.example .env
# 编辑 .env 填入配置

# 初始化数据库
alembic upgrade head

# 启动开发服务器
uvicorn main:app --reload --port 8000
```

API 文档：http://localhost:8000/docs

### 前端启动

```bash
cd frontend
npm install
npm run dev    # http://localhost:3000
```

### Docker 一键启动

```bash
docker-compose up -d
# 前端：http://localhost:3000
# 后端：http://localhost:8000
```

## 测试

```bash
# 后端测试
cd backend
pytest tests/ -v --cov

# 前端测试
cd frontend
npm run test:run

# E2E 测试
cd frontend
npx playwright test
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/register | 用户注册 |
| POST | /api/v1/auth/login | 用户登录 |
| GET | /api/v1/ingredients | 获取食材列表 |
| POST | /api/v1/ingredients | 添加食材 |
| PUT | /api/v1/ingredients/{id} | 更新食材 |
| DELETE | /api/v1/ingredients/{id} | 删除食材 |
| GET | /api/v1/ingredients/expiring | 获取临期食材 |
| POST | /api/v1/recognition/recognize | AI 识别食材 |
| GET | /api/v1/recipes/recommend | 推荐菜谱 |
| GET | /api/v1/nutrition/summary | 营养分析 |

详细文档：[docs/DESIGN_SPEC.md](docs/DESIGN_SPEC.md)

## 赛事信息

本项目为 **TRAE AI 创造力大赛** 参赛作品，演示 AI 在日常生活中的创意应用。
