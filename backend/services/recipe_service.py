"""菜谱服务层：本地预设菜谱库 + AI 推荐。"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import NotFoundException
from models.ingredient import IngredientModel
from models.recipe import RecipeModel
from schemas.recipe import RecipeIngredient, RecipeResponse, RecipeStep

logger = logging.getLogger(__name__)


# 本地预设菜谱库（至少 5 道菜）
LOCAL_RECIPES: list[dict[str, Any]] = [
    {
        "name": "西红柿炒蛋",
        "description": "家常经典菜，简单易做，酸甜可口。",
        "cook_time": 15,
        "calories": 220.0,
        "servings": 2,
        "ingredients": [
            {"ingredient_name": "西红柿", "amount": "2个", "is_required": True},
            {"ingredient_name": "鸡蛋", "amount": "3个", "is_required": True},
            {"ingredient_name": "盐", "amount": "适量", "is_required": False},
            {"ingredient_name": "糖", "amount": "少许", "is_required": False},
        ],
        "steps": [
            {"step": 1, "description": "西红柿洗净切块，鸡蛋打散加少许盐。"},
            {"step": 2, "description": "热锅冷油，倒入蛋液炒至凝固盛出。"},
            {"step": 3, "description": "锅中下西红柿翻炒出汁，加糖调味。"},
            {"step": 4, "description": "倒回鸡蛋翻炒均匀即可出锅。"},
        ],
    },
    {
        "name": "土豆炖牛肉",
        "description": "软烂入味的炖菜，营养丰富。",
        "cook_time": 60,
        "calories": 380.0,
        "servings": 3,
        "ingredients": [
            {"ingredient_name": "土豆", "amount": "2个", "is_required": True},
            {"ingredient_name": "牛肉", "amount": "300克", "is_required": True},
            {"ingredient_name": "胡萝卜", "amount": "1根", "is_required": False},
            {"ingredient_name": "酱油", "amount": "2勺", "is_required": False},
        ],
        "steps": [
            {"step": 1, "description": "牛肉切块焯水去血沫，土豆、胡萝卜切块。"},
            {"step": 2, "description": "锅中放油，下牛肉翻炒上色，加酱油。"},
            {"step": 3, "description": "加水没过牛肉，大火烧开转小火炖 40 分钟。"},
            {"step": 4, "description": "加入土豆、胡萝卜继续炖 15 分钟至软烂。"},
        ],
    },
    {
        "name": "蒜蓉西兰花",
        "description": "清淡健康，保留蔬菜营养。",
        "cook_time": 10,
        "calories": 120.0,
        "servings": 2,
        "ingredients": [
            {"ingredient_name": "西兰花", "amount": "1颗", "is_required": True},
            {"ingredient_name": "大蒜", "amount": "4瓣", "is_required": True},
            {"ingredient_name": "盐", "amount": "适量", "is_required": False},
        ],
        "steps": [
            {"step": 1, "description": "西兰花掰小朵洗净，大蒜切末。"},
            {"step": 2, "description": "沸水焯烫西兰花 1 分钟捞出。"},
            {"step": 3, "description": "热锅下蒜末爆香，倒入西兰花翻炒。"},
            {"step": 4, "description": "加盐调味，翻炒均匀出锅。"},
        ],
    },
    {
        "name": "胡萝卜炒肉",
        "description": "色泽诱人，荤素搭配。",
        "cook_time": 20,
        "calories": 260.0,
        "servings": 2,
        "ingredients": [
            {"ingredient_name": "胡萝卜", "amount": "2根", "is_required": True},
            {"ingredient_name": "猪肉", "amount": "150克", "is_required": True},
            {"ingredient_name": "生抽", "amount": "1勺", "is_required": False},
        ],
        "steps": [
            {"step": 1, "description": "胡萝卜切丝，猪肉切丝用生抽腌制。"},
            {"step": 2, "description": "热锅下肉丝滑炒至变色盛出。"},
            {"step": 3, "description": "下胡萝卜丝翻炒至软。"},
            {"step": 4, "description": "倒回肉丝，调味翻炒均匀。"},
        ],
    },
    {
        "name": "牛奶麦片",
        "description": "快手早餐，营养均衡。",
        "cook_time": 5,
        "calories": 280.0,
        "servings": 1,
        "ingredients": [
            {"ingredient_name": "牛奶", "amount": "250ml", "is_required": True},
            {"ingredient_name": "麦片", "amount": "50克", "is_required": True},
            {"ingredient_name": "蜂蜜", "amount": "适量", "is_required": False},
        ],
        "steps": [
            {"step": 1, "description": "牛奶倒入锅中加热至温热（不要煮沸）。"},
            {"step": 2, "description": "麦片放入碗中。"},
            {"step": 3, "description": "将热牛奶倒入麦片中，搅拌均匀。"},
            {"step": 4, "description": "根据口味加入蜂蜜即可。"},
        ],
    },
]


def _build_recipe_response(
    recipe_data: dict[str, Any],
    source: str = "local",
    user_ingredients: list[str] | None = None,
) -> RecipeResponse:
    """根据菜谱字典构造响应对象。"""
    ingredients = [RecipeIngredient(**item) for item in recipe_data.get("ingredients", [])]
    steps = [RecipeStep(**item) for item in recipe_data.get("steps", [])]

    match_count = None
    if user_ingredients is not None:
        user_set = {name.lower() for name in user_ingredients}
        match_count = sum(1 for ing in ingredients if ing.ingredient_name.lower() in user_set)

    return RecipeResponse(
        recipe_id=recipe_data.get("recipe_id", ""),
        name=recipe_data["name"],
        description=recipe_data.get("description"),
        cook_time=recipe_data.get("cook_time"),
        calories=recipe_data.get("calories"),
        servings=recipe_data.get("servings"),
        steps=steps,
        image_url=recipe_data.get("image_url"),
        source=source,  # type: ignore[arg-type]
        ingredients=ingredients,
        match_count=match_count,
        created_at=recipe_data.get("created_at"),
    )


def _match_score(recipe_data: dict[str, Any], user_ingredients: list[str]) -> int:
    """计算菜谱与用户食材的匹配数。"""
    user_set = {name.lower() for name in user_ingredients}
    score = 0
    for item in recipe_data.get("ingredients", []):
        if item["ingredient_name"].lower() in user_set:
            score += 1
    return score


async def recommend_recipes(
    db: AsyncSession,
    user_id: str,
    user_ingredients: list[str] | None = None,
    limit: int = 5,
) -> list[RecipeResponse]:
    """基于现有食材匹配推荐菜谱。

    优先使用本地预设菜谱库进行匹配排序；当配置了 AI 且本地匹配不足时，
    可调用 AI 生成（此处保留接口，AI 不可用时降级到本地库）。
    """
    # 若未指定食材，则从数据库读取用户库存
    if user_ingredients is None:
        result = await db.execute(select(IngredientModel).where(IngredientModel.user_id == user_id))
        user_ingredients = [ing.name for ing in result.scalars().all()]

    # 本地菜谱匹配排序
    scored = [(recipe, _match_score(recipe, user_ingredients)) for recipe in LOCAL_RECIPES]
    # 必需食材匹配优先，按匹配数降序
    scored.sort(key=lambda x: x[1], reverse=True)

    recommendations: list[RecipeResponse] = []
    for recipe_data, _ in scored[:limit]:
        recommendations.append(_build_recipe_response(recipe_data, source="local", user_ingredients=user_ingredients))

    # AI 推荐降级提示：当无 OPENAI_API_KEY 时仅返回本地结果
    if not settings.OPENAI_API_KEY:
        logger.info("OPENAI_API_KEY 未配置，仅返回本地菜谱推荐")

    return recommendations


async def get_recipe_by_id(db: AsyncSession, recipe_id: str) -> RecipeResponse:
    """根据 ID 获取菜谱详情。

    本地预设菜谱使用固定 recipe_id（基于索引），数据库菜谱从表中查询。
    """
    # 先尝试本地预设菜谱（recipe_id 形如 local-0、local-1）
    if recipe_id.startswith("local-"):
        try:
            idx = int(recipe_id.split("-", 1)[1])
            if 0 <= idx < len(LOCAL_RECIPES):
                recipe_data = dict(LOCAL_RECIPES[idx])
                recipe_data["recipe_id"] = recipe_id
                return _build_recipe_response(recipe_data, source="local")
        except (ValueError, IndexError):
            pass
        raise NotFoundException(message="菜谱不存在")

    # 数据库查询
    result = await db.execute(select(RecipeModel).where(RecipeModel.recipe_id == recipe_id))
    recipe = result.scalar_one_or_none()
    if recipe is None:
        raise NotFoundException(message="菜谱不存在")

    recipe_data = {
        "recipe_id": recipe.recipe_id,
        "name": recipe.name,
        "description": recipe.description,
        "cook_time": recipe.cook_time,
        "calories": recipe.calories,
        "servings": recipe.servings,
        "steps": recipe.steps or [],
        "image_url": recipe.image_url,
        "source": recipe.source,
        "ingredients": [],
        "created_at": recipe.created_at,
    }
    return _build_recipe_response(recipe_data, source=recipe.source)  # type: ignore[arg-type]


def get_local_recipe_index(recipe_name: str) -> int | None:
    """根据菜名获取本地菜谱索引，便于生成稳定的 recipe_id。"""
    for idx, recipe in enumerate(LOCAL_RECIPES):
        if recipe["name"] == recipe_name:
            return idx
    return None
