# Bilibili API MCP Server

用于哔哩哔哩 API 的 MCP（模型上下文协议）服务器，支持多种操作。

## 环境要求

- [uv](https://docs.astral.sh/uv/) - 一个项目管理工具，可以很方便管理依赖。

## 使用方法

### 方式一：通过 PyPI 使用（推荐）

在任意 MCP client 中配置本 Server，系统会自动下载和启用

```json
{
  "mcpServers": {
    "bilibili": {
      "type": "stdio",
      "isActive": true,
      "command": "uvx",
      "args": [
        "bilibili-api-mcp-server"
      ]
    }
  }
}
```

> 💡 **提示**：您也可以直接使用项目根目录下的 `mcp-config.json` 文件作为配置参考。

### 方式二：本地开发运行

1. clone 本项目

```bash
git clone https://github.com/SMYB5431/bilibili-api-mcp-server.git
cd bilibili-api-mcp-server
```

2. 使用 uv 安装依赖

```bash
uv sync
```

3. 在任意 MCP client 中配置本 Server

```json
{
  "mcpServers": {
    "bilibili": {
      "command": "uv",
      "args": [
        "--directory",
        "/your-project-path/bilibili-api-mcp-server",
        "run",
        "bilibili.py"
      ]
    }
  }
}
```

### 开始使用

## 支持的操作

支持以下操作：

### 基础搜索功能
1. `search_and_recommend_videos`: 智能视频搜索和推荐功能。
   - 按综合排序搜索视频内容
   - 自动过滤课堂视频（cheese链接）
   - 返回前15条视频结果（可自定义数量）
   - 基于搜索结果提供推荐理由
   - 分析视频质量和热度
   - 生成内容总结和推荐报告

2. `search_user`: 专门用于搜索哔哩哔哩用户的功能，可以按照粉丝数排序。

3. `get_user_id_by_name`: 通过用户名获取用户ID，支持精确搜索和详细信息返回。
   - 默认模式：只返回用户ID，用于快速获取用户标识
   - 详细模式：返回完整用户信息和精确匹配状态
   - 精确匹配：优先返回完全匹配用户名的结果
   - 错误处理：提供详细的错误信息和异常处理

### 用户内容获取功能
4. `get_user_dynamics`: 获取指定用户的最新动态。
   - 支持通过用户名直接获取（如"技术爬爬虾"）
   - 可指定获取动态数量（默认10条）
   - 返回动态内容、时间戳、链接等信息

5. `get_user_videos`: 获取指定用户的最新投稿视频。
   - 支持通过用户名直接获取
   - 可指定获取视频数量（默认10条）
   - 返回视频标题、BV号、播放量、时长等详细信息

6. `get_user_collections`: 获取指定用户的合集信息。
   - 支持通过用户名直接获取
   - 返回合集标题、视频数量、播放量等信息
   - 包含合集链接便于访问

7. `get_collection_videos`: 获取指定合集中的视频列表。
   - 支持通过合集名称或合集ID获取
   - 可指定获取视频数量（默认10条）
   - 返回视频详细信息（标题、播放量、点赞数、投币数等）
   - 支持模糊匹配合集名称

8. `search_collection_by_keyword`: 在用户合集中搜索包含关键词的视频。
   - 支持在所有合集中搜索特定关键词
   - 返回匹配的合集及其视频列表
   - 适用于快速定位特定主题的视频内容

### 其他功能
9. `get_video_danmaku`: 获取视频弹幕信息。
   - 支持视频链接或BV号输入
   - 自动从链接中提取BV号
   - 支持多分P视频的弹幕获取
   - 返回详细的视频信息和弹幕数据

## 声明

本项目在开发和测试过程中使用了哔哩哔哩 UP主 [技术爬爬虾](https://space.bilibili.com/316183842) 的公开内容作为示例数据。

本项目仅用于技术学习和研究目的，所有示例数据的使用均遵循哔哩哔哩平台的使用条款。如有任何版权问题，请联系项目维护者。

## License

MIT
