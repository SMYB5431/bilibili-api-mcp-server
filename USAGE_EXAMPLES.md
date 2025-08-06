# bilibili-api-mcp-server 使用示例

本文档展示了如何使用 bilibili-mcp-server 的各种功能，特别是新增的用户内容获取功能。

## 功能使用示例

### 1. 智能视频搜索和推荐 (`search_and_recommend_videos`)

**功能描述**：一站式视频搜索和推荐功能，集成了搜索、过滤、分析和推荐

**使用场景**：
- "请你搜索AI相关的视频，请你总结和推荐"
- "帮我找一些机器学习的优质视频内容"
- "搜索Python教程视频并推荐最好的"

**参数**：
- `keyword` (str): 搜索关键词，如"AI"
- `count` (int, 可选): 推荐视频数量，默认15条

**核心功能**：
- 🔍 按综合排序搜索视频内容
- 🚫 自动过滤课堂视频（cheese链接）
- 📊 智能分析视频质量和热度
- 💡 生成个性化推荐理由
- 📈 提供内容总结和统计分析

**返回示例**：
```json
{
  "keyword": "AI",
  "search_url": "https://search.bilibili.com/all?keyword=AI&from_source=webtop_search&spm_id_from=333.1387&search_source=5",
  "recommendations": [
    {
      "rank": 1,
      "title": "2024年AI发展趋势全解析",
      "author": "AI科技前沿",
      "bvid": "BV1234567890",
      "duration": "15:30",
      "play_count": 1250000,
      "danmaku_count": 8500,
      "favorites": 45000,
      "description": "深度分析2024年人工智能发展的主要趋势...",
      "url": "https://www.bilibili.com/video/BV1234567890",
      "recommend_reasons": ["百万播放热门视频", "高收藏量", "深度内容"],
      "is_popular": true
    }
  ],
  "summary": {
    "keyword": "AI",
    "total_videos": 15,
    "popular_videos_count": 8,
    "unique_authors": 12,
    "average_play_count": 450000,
    "content_analysis": {
      "high_quality_ratio": "53.3%",
      "content_diversity": "来自 12 位不同UP主",
      "engagement_level": "中"
    },
    "recommendation_summary": "为您推荐了 15 个关于 'AI' 的优质视频，其中 8 个为热门视频。内容涵盖了多个角度和深度，适合不同需求的观众。"
  },
  "total_fetched": 15
}
```

### 2. 获取用户ID (`get_user_id_by_name`)

**功能描述**：通过用户名获取用户ID，支持精确搜索和详细信息返回

**使用场景**：
- "帮我找到用户'IT咖啡馆'的ID"
- "搜索用户并返回详细信息"

**参数**：
- `username` (str): 用户名，如"IT咖啡馆"
- `return_details` (bool, 可选): 是否返回详细信息，默认False

**返回示例**：

**简单模式** (`return_details=False`):
```json
{
  "user_id": 65564239
}
```

**详细模式** (`return_details=True`):
```json
{
  "users": [
    {
      "uname": "IT咖啡馆",
      "mid": 65564239,
      "face": "http://i2.hdslb.com/bfs/face/...",
      "fans": 1267000,
      "videos": 856,
      "level": 6,
      "sign": "分享AI工具和编程技术",
      "official": "知名UP主"
    }
  ],
  "exact_match": true
}
```

### 3. 获取用户动态 (`get_user_dynamics`)

**功能描述**：获取指定用户的最新动态信息

**使用场景**：
- "请你查看和总结最新的10条 IT咖啡馆的动态"
- "帮我看看 某某UP主 最近发了什么动态"

**参数**：
- `username` (str): 用户名，如"IT咖啡馆"
- `count` (int, 可选): 获取动态数量，默认10条

**返回示例**：
```json
{
  "username": "IT咖啡馆",
  "uid": 65564239,
  "dynamics": [
    {
      "id": "1096912399525478421",
      "type": "DYNAMIC_TYPE_FORWARD",
      "timestamp": 0,
      "content": "战车拿下雪如意，CNDOTA太久没有冠军了😭",
      "url": "https://t.bilibili.com/1096912399525478421"
    },
    {
      "id": "1096711373573849144",
      "type": "DYNAMIC_TYPE_AV",
      "timestamp": 0,
      "content": "发布了视频: 「Github一周热点81期」开源模型汇总、Coze的开源版本...",
      "url": "https://t.bilibili.com/1096711373573849144",
      "video_info": {
        "title": "「Github一周热点81期」开源模型汇总、Coze的开源版本...",
        "bvid": "BV12XhPzHEXk",
        "url": "https://www.bilibili.com/video/BV12XhPzHEXk"
      }
    }
  ],
  "total_fetched": 2
}
```

### 2. 获取用户投稿视频 (`get_user_videos`)

**功能描述**：获取指定用户的最新投稿视频

**使用场景**：
- "请你查看和总结最新的5条 IT咖啡馆的投稿"
- "帮我看看 某某UP主 最近上传了什么视频"

**参数**：
- `username` (str): 用户名，如"IT咖啡馆"
- `count` (int, 可选): 获取视频数量，默认10条

**返回示例**：
```json
{
  "username": "IT咖啡馆",
  "uid": 65564239,
  "videos": [
    {
      "title": "「Github一周热点81期」开源模型汇总、Coze的开源版本...",
      "bvid": "BV12XhPzHEXk",
      "aid": 113851234567,
      "description": "本期介绍了多个开源项目...",
      "duration": "08:05",
      "play_count": 18597,
      "comment_count": 156,
      "created": 1735123456,
      "pic": "http://i2.hdslb.com/bfs/archive/...",
      "url": "https://www.bilibili.com/video/BV12XhPzHEXk"
    }
  ],
  "total_count": 3,
  "total_fetched": 1
}
```

### 3. 获取用户合集 (`get_user_collections`)

**功能描述**：获取指定用户的合集信息

**使用场景**：
- "请你查看，有多少 IT咖啡馆的合集"
- "帮我看看 某某UP主 有哪些视频合集"

**参数**：
- `username` (str): 用户名，如"IT咖啡馆"

**返回示例**：
```json
{
  "username": "IT咖啡馆",
  "uid": 65564239,
  "collections": [
    {
      "id": 1982929,
      "title": "Github一周热点系列",
      "description": "每周分享Github上的热门开源项目",
      "cover": "http://i2.hdslb.com/bfs/archive/...",
      "video_count": 81,
      "play_count": 1234567,
      "type": "season",
      "url": "https://space.bilibili.com/65564239/channel/collectiondetail?sid=1982929"
    }
  ],
  "total_count": 8
}
```

### 4. 获取合集视频 (`get_collection_videos`)

**功能描述**：获取指定用户合集中的视频列表

**使用场景**：
- "Github热门项目系列最新10条投稿视频"
- "请获取IT咖啡馆的AI工具合集中的视频"

**参数**：
- `username` (str): 用户名，如"IT咖啡馆"
- `collection_name` (str, 可选): 合集名称，如"Github热门项目系列"
- `collection_id` (int, 可选): 合集ID，如果提供则优先使用
- `count` (int, 可选): 获取视频数量，默认10条

**返回示例**：
```json
{
  "username": "IT咖啡馆",
  "uid": 65564239,
  "collection_title": "Github热门项目系列",
  "collection_id": 1982929,
  "collection_description": "每周分享Github上的热门开源项目",
  "total_videos": 81,
  "videos": [
    {
      "title": "「Github一周热点81期」开源模型汇总、Coze的开源版本...",
      "bvid": "BV12XhPzHEXk",
      "aid": 113851234567,
      "description": "本期介绍了多个开源项目...",
      "duration": "08:05",
      "play_count": 18597,
      "danmaku_count": 156,
      "like_count": 892,
      "coin_count": 234,
      "favorite_count": 445,
      "share_count": 67,
      "reply_count": 89,
      "pubdate": 1735123456,
      "pic": "http://i2.hdslb.com/bfs/archive/...",
      "url": "https://www.bilibili.com/video/BV12XhPzHEXk"
    }
  ],
  "total_fetched": 10
}
```

### 5. 获取视频弹幕 (`get_video_danmaku`)

**功能描述**：获取视频的弹幕数据，支持视频链接或BV号输入

**使用场景**：
- "请你获取此视频的弹幕数据，对应链接：https://www.bilibili.com/video/BV1AnQNYxEsy/?spm_id_from=333.337.search-card.all.click"
- "帮我获取BV1AnQNYxEsy这个视频的弹幕"
- "获取这个视频第2个分P的弹幕"

**参数**：
- `video_input` (str): 视频链接或BV号
- `page` (int, 可选): 分P页码，从0开始，默认为0

**支持的输入格式**：
- BV号：`BV1AnQNYxEsy`
- 完整链接：`https://www.bilibili.com/video/BV1AnQNYxEsy/?spm_id_from=333.337.search-card.all.click`
- 短链接：`bilibili.com/video/BV1AnQNYxEsy`

**返回示例**：
```json
{
  "bv_id": "BV1AnQNYxEsy",
  "video_title": "视频标题",
  "video_author": "UP主名称",
  "page": 0,
  "total_pages": 1,
  "danmaku_content": "[Script Info]\nTitle: Bilibili ASS Danmaku...",
  "danmaku_file_size": 15420,
  "video_url": "https://www.bilibili.com/video/BV1AnQNYxEsy",
  "success": true
}
```

**错误处理示例**：
```json
{
  "error": "无法从输入中提取BV号: invalid_input",
  "success": false,
  "suggestion": "请提供有效的B站视频链接或BV号，例如：https://www.bilibili.com/video/BV1AnQNYxEsy 或 BV1AnQNYxEsy"
}
```

### 6. 搜索合集视频 (`search_collection_by_keyword`)

**功能描述**：在指定用户的所有合集中搜索包含关键词的视频

**使用场景**：
- "在IT咖啡馆的合集中搜索包含Github的视频"
- "查找某UP主所有AI相关的合集内容"

**参数**：
- `username` (str): 用户名，如"IT咖啡馆"
- `keyword` (str): 搜索关键词，如"Github"、"AI"等
- `count` (int, 可选): 每个合集最多返回的视频数量，默认10条

**返回示例**：
```json
{
  "username": "IT咖啡馆",
  "uid": 65564239,
  "search_keyword": "Github",
  "matched_collections": [
    {
      "collection_title": "Github热门项目系列",
      "collection_id": 1982929,
      "match_reason": "合集标题匹配",
      "videos": [
        {
          "title": "「Github一周热点81期」开源模型汇总...",
          "bvid": "BV12XhPzHEXk",
          "aid": 113851234567,
          "duration": "08:05",
          "play_count": 18597,
          "pubdate": 1735123456,
          "url": "https://www.bilibili.com/video/BV12XhPzHEXk"
        }
      ],
      "video_count": 10
    }
  ],
  "total_collections": 1,
  "total_videos": 10
}
```

## 实际使用场景

### 场景1：AI助手搜索和推荐视频
```
用户：请你搜索AI相关的视频，请你总结和推荐

AI助手会调用：search_and_recommend_videos("AI", 15)
然后基于返回的推荐结果和分析数据，为用户提供：
- 15个精选AI相关视频
- 每个视频的推荐理由
- 内容质量分析
- 观看建议和总结
```

### 场景2：AI助手总结UP主动态
```
用户：请你查看和总结最新的10条 IT咖啡馆的动态

AI助手会调用：get_user_dynamics("IT咖啡馆", 10)
然后基于返回的动态内容进行总结和分析
```

### 场景2：AI助手分析UP主投稿
```
用户：请你查看和总结最新的5条 IT咖啡馆的投稿

AI助手会调用：get_user_videos("IT咖啡馆", 5)
然后分析视频标题、播放量、内容等信息
```

### 场景3：AI助手统计UP主合集
```
用户：请你查看，有多少 IT咖啡馆的合集

AI助手会调用：get_user_collections("IT咖啡馆")
然后统计合集数量和基本信息
```

### 场景4：AI助手获取合集视频
```
用户：Github热门项目系列最新10条投稿视频

AI助手会调用：get_collection_videos("IT咖啡馆", "Github热门项目系列", 0, 10)
然后返回该合集中最新的10个视频详细信息
```

### 场景5：AI助手搜索合集内容
```
用户：在IT咖啡馆的合集中搜索包含AI的视频

AI助手会调用：search_collection_by_keyword("IT咖啡馆", "AI", 10)
然后返回所有包含"AI"关键词的合集及其视频
```

## 错误处理

所有函数都包含完善的错误处理机制：

1. **用户不存在**：
```json
{"error": "未找到用户: 不存在的用户名"}
```

2. **无内容**：
```json
{
  "username": "用户名",
  "uid": 12345,
  "dynamics": [],
  "message": "该用户暂无动态"
}
```

3. **API错误**：
```json
{"error": "获取用户动态失败: 具体错误信息"}
```

## 技术实现要点

1. **用户名到UID转换**：通过 `_get_user_id_by_name()` 辅助函数实现
2. **精确匹配优先**：优先返回完全匹配的用户
3. **数据清洗**：只返回关键信息，过滤冗余数据
4. **异常处理**：完善的错误处理和降级策略
5. **URL生成**：自动生成对应的B站链接

## 注意事项

1. 某些功能可能需要登录凭据才能获取完整信息
2. API调用频率可能有限制，建议适当控制调用频次
3. 合集信息获取可能受到权限限制，部分信息可能无法获取
4. 动态内容的解析依赖于B站API的返回格式，格式变化可能影响解析效果
