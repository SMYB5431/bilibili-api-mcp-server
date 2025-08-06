import os
from typing import Any, Optional, Dict

from bilibili_api import search, sync, ass, video, user
from bilibili_api.search import SearchObjectType, OrderUser
from bilibili_api.channel_series import ChannelOrder
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("bilibili api mcp server")


@mcp.tool()
def search_user(keyword: str, page: int = 1) -> dict[Any, Any]:
    """
    搜索哔哩哔哩用户信息。

    Args:
        keyword: 用户名关键词
        page: 页码，默认为1

    Returns:
        包含用户搜索结果的字典数据
    """
    return sync(
        search.search_by_type(keyword=keyword, search_type=SearchObjectType.USER, order_type=OrderUser.FANS, page=page)
    )


@mcp.tool()
def search_and_recommend_videos(keyword: str, count: int = 15) -> Dict[str, Any]:
    """
    搜索并推荐相关视频，提供详细的推荐理由和总结

    Args:
        keyword: 搜索关键词（如"AI"）
        count: 推荐视频数量，默认15条

    Returns:
        包含推荐视频和总结的字典
    """
    try:
        # 使用视频搜索，按综合排序
        result = sync(
            search.search_by_type(
                keyword=keyword,
                search_type=SearchObjectType.VIDEO,
                page=1,
                page_size=30,  # 获取更多结果以便过滤后还有足够的视频
            )
        )

        if not result or not result.get("result"):
            return {"keyword": keyword, "recommendations": [], "summary": f"未找到关键词 '{keyword}' 相关的视频内容"}

        # 提取并过滤视频信息
        videos = []
        raw_videos = result["result"]

        for video_item in raw_videos:
            # 跳过课堂视频（包含 cheese 链接的）
            video_url = f"https://www.bilibili.com/video/{video_item.get('bvid', '')}"
            if "cheese" in video_item.get("arcurl", "").lower():
                continue

            # 检查是否是课堂视频的其他标识
            if video_item.get("type") == "cheese" or "课程" in video_item.get("title", ""):
                continue

            video_info = {
                "title": video_item.get("title", "").replace('<em class="keyword">', "").replace("</em>", ""),
                "bvid": video_item.get("bvid", ""),
                "aid": video_item.get("aid", 0),
                "author": video_item.get("author", ""),
                "mid": video_item.get("mid", 0),
                "description": video_item.get("description", "")
                .replace('<em class="keyword">', "")
                .replace("</em>", ""),
                "duration": video_item.get("duration", ""),
                "play_count": video_item.get("play", 0),
                "danmaku_count": video_item.get("video_review", 0),
                "favorites": video_item.get("favorites", 0),
                "pubdate": video_item.get("pubdate", 0),
                "pic": video_item.get("pic", ""),
                "url": video_url,
                "tag": video_item.get("tag", ""),
            }

            videos.append(video_info)

            # 限制返回指定数量的视频
            if len(videos) >= count:
                break

        if not videos:
            return {"keyword": keyword, "recommendations": [], "summary": f"未找到关键词 '{keyword}' 相关的视频内容"}

        # 生成搜索URL
        search_url = f"https://search.bilibili.com/all?keyword={keyword}&from_source=webtop_search&spm_id_from=333.1387&search_source=5"

        # 分析视频数据，生成推荐理由
        recommendations = []
        total_play_count = 0
        authors = set()
        popular_videos = []

        for i, video in enumerate(videos, 1):
            play_count = video.get("play_count", 0)
            total_play_count += play_count
            authors.add(video.get("author", ""))

            # 判断是否为热门视频（播放量超过10万）
            is_popular = play_count >= 100000
            if is_popular:
                popular_videos.append(video)

            # 生成推荐理由
            reasons = []
            if play_count >= 1000000:
                reasons.append("百万播放热门视频")
            elif play_count >= 100000:
                reasons.append("高播放量视频")

            if video.get("favorites", 0) >= 10000:
                reasons.append("高收藏量")

            if video.get("duration"):
                duration = video.get("duration", "")
                if ":" in duration:
                    try:
                        parts = duration.split(":")
                        if len(parts) == 2:
                            minutes = int(parts[0])
                            if minutes >= 20:
                                reasons.append("深度内容")
                            elif minutes <= 5:
                                reasons.append("快速了解")
                    except:
                        pass

            if not reasons:
                reasons.append("相关度匹配")

            recommendation = {
                "rank": i,
                "title": video.get("title", ""),
                "author": video.get("author", ""),
                "bvid": video.get("bvid", ""),
                "duration": video.get("duration", ""),
                "play_count": play_count,
                "danmaku_count": video.get("danmaku_count", 0),
                "favorites": video.get("favorites", 0),
                "description": (
                    video.get("description", "")[:100] + "..."
                    if len(video.get("description", "")) > 100
                    else video.get("description", "")
                ),
                "url": video.get("url", ""),
                "pic": video.get("pic", ""),
                "recommend_reasons": reasons,
                "is_popular": is_popular,
            }

            recommendations.append(recommendation)

        # 生成总结
        avg_play_count = total_play_count // len(videos) if videos else 0
        popular_count = len(popular_videos)

        summary = {
            "keyword": keyword,
            "total_videos": len(videos),
            "popular_videos_count": popular_count,
            "unique_authors": len(authors),
            "average_play_count": avg_play_count,
            "content_analysis": {
                "high_quality_ratio": f"{(popular_count/len(videos)*100):.1f}%" if videos else "0%",
                "content_diversity": f"来自 {len(authors)} 位不同UP主",
                "engagement_level": "高" if avg_play_count >= 500000 else "中" if avg_play_count >= 100000 else "一般",
            },
            "recommendation_summary": f"为您推荐了 {len(videos)} 个关于 '{keyword}' 的优质视频，其中 {popular_count} 个为热门视频。内容涵盖了多个角度和深度，适合不同需求的观众。",
        }

        return {
            "keyword": keyword,
            "search_url": search_url,
            "recommendations": recommendations,
            "summary": summary,
            "total_fetched": len(recommendations),
        }

    except Exception as e:
        return {"error": f"搜索视频失败: {str(e)}"}


@mcp.tool()
def get_user_id_by_name(username: str, return_details: bool = False) -> Dict[str, Any]:
    """
    通过用户名获取用户ID，支持精确搜索和详细信息返回

    Args:
        username: 用户名
        return_details: 是否返回详细信息，默认False只返回用户ID

    Returns:
        如果return_details=False: {"user_id": int} 或 {"error": str}
        如果return_details=True: {"users": list, "exact_match": bool} 或 {"error": str}
    """
    try:
        # 增加页面大小以提高匹配几率
        result = sync(search.search_by_type(keyword=username, search_type=SearchObjectType.USER, page=1, page_size=50))

        if not result or not result.get("result"):
            return {"error": f"未找到用户: {username}"}

        # 提取关键信息，过滤掉不必要的字段
        filtered_result = []
        exact_match_result = []

        for user in result.get("result", []):
            # 只保留关键信息
            filtered_user = {
                "uname": user.get("uname", ""),
                "mid": user.get("mid", 0),
                "face": user.get("upic", ""),
                "fans": user.get("fans", 0),
                "videos": user.get("videos", 0),
                "level": user.get("level", 0),
                "sign": user.get("usign", ""),
                "official": user.get("official_verify", {}).get("desc", ""),
            }

            # 检查是否完全匹配
            if user.get("uname", "").lower() == username.lower():
                exact_match_result.append(filtered_user)
            else:
                filtered_result.append(filtered_user)

        # 如果只需要用户ID
        if not return_details:
            if exact_match_result:
                return {"user_id": exact_match_result[0]["mid"]}
            elif filtered_result:
                return {"user_id": filtered_result[0]["mid"]}
            else:
                return {"error": f"未找到用户: {username}"}

        # 如果需要详细信息
        if exact_match_result:
            return {"users": exact_match_result, "exact_match": True}
        else:
            return {"users": filtered_result, "exact_match": False}

    except Exception as e:
        return {"error": f"搜索用户失败: {str(e)}"}


def _get_user_id_by_name(username: str) -> Optional[int]:
    """
    通过用户名获取用户ID的辅助函数（内部使用）

    Args:
        username: 用户名

    Returns:
        用户ID，如果找不到则返回None
    """
    result = get_user_id_by_name(username, return_details=False)
    if "user_id" in result:
        return result["user_id"]
    return None


def _extract_bv_from_url(url_or_bv: str) -> str:
    """
    从B站视频链接中提取BV号，或直接返回BV号

    Args:
        url_or_bv: 视频链接或BV号

    Returns:
        提取出的BV号

    Raises:
        ValueError: 如果无法提取BV号
    """
    import re

    # 如果已经是BV号格式，直接返回
    if url_or_bv.startswith("BV") and len(url_or_bv) == 12:
        return url_or_bv

    # 从URL中提取BV号的正则表达式
    # 支持多种B站链接格式
    patterns = [
        r"BV[a-zA-Z0-9]{10}",  # 通用BV号匹配
        r"/video/(BV[a-zA-Z0-9]{10})",  # 标准视频链接
        r"bilibili\.com/video/(BV[a-zA-Z0-9]{10})",  # 完整域名链接
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_bv)
        if match:
            # 如果匹配到分组，返回分组内容，否则返回整个匹配
            return match.group(1) if match.groups() else match.group(0)

    # 如果都没匹配到，抛出异常
    raise ValueError(f"无法从输入中提取BV号: {url_or_bv}")


@mcp.tool()
def get_video_danmaku(video_input: str, page: int = 0) -> Dict[str, Any]:
    """
    获取视频的弹幕数据。支持视频链接或BV号输入。

    Args:
        video_input: 视频链接或BV号
                    支持格式：
                    - BV号: BV1iv8CzVE2w
                    - 完整链接: https://www.bilibili.com/video/BV1iv8CzVE2w/?spm_id_from=333.1387.homepage.video_card.click
                    - 短链接: bilibili.com/video/BV1iv8CzVE2w
        page: 分P页码，从0开始，默认为0（第一个分P）

    Returns:
        包含弹幕数据和视频信息的字典
    """
    try:
        # 提取BV号
        bv_id = _extract_bv_from_url(video_input)

        # 定义video对象
        v = video.Video(bv_id)

        # 获取视频基本信息
        video_info = sync(v.get_info())

        # 生成弹幕文件
        output_filepath = f"danmaku_{bv_id}_p{page}.ass"
        sync(
            ass.make_ass_file_danmakus_protobuf(
                obj=v, page=page, out=output_filepath  # 生成弹幕文件的对象  # 哪一个分 P (从 0 开始)  # 输出文件地址
            )
        )

        # 读取弹幕文件
        with open(output_filepath, "r", encoding="utf-8") as f:
            danmaku_content = f.read()

        # 删除弹幕文件
        os.remove(output_filepath)

        return {
            "bv_id": bv_id,
            "video_title": video_info.get("title", ""),
            "video_author": video_info.get("owner", {}).get("name", ""),
            "page": page,
            "total_pages": len(video_info.get("pages", [])),
            "danmaku_content": danmaku_content,
            "danmaku_file_size": len(danmaku_content),
            "video_url": f"https://www.bilibili.com/video/{bv_id}",
            "success": True,
        }

    except ValueError as e:
        return {
            "error": str(e),
            "success": False,
            "suggestion": "请提供有效的B站视频链接或BV号，例如：https://www.bilibili.com/video/BV1AnQNYxEsy 或 BV1AnQNYxEsy",
        }
    except Exception as e:
        return {
            "error": f"获取弹幕失败: {str(e)}",
            "success": False,
            "bv_id": video_input if video_input.startswith("BV") else "未知",
        }


@mcp.tool()
def get_user_dynamics(username: str, count: int = 10) -> Dict[str, Any]:
    """
    获取指定用户的最新动态

    Args:
        username: 用户名（如"技术爬爬虾"）
        count: 要获取的动态数量，默认10条

    Returns:
        包含用户动态信息的字典
    """
    # 先通过用户名获取用户ID
    uid = _get_user_id_by_name(username)
    if not uid:
        return {"error": f"未找到用户: {username}"}

    # 创建用户对象
    u = user.User(uid)

    try:
        # 获取用户动态（使用新接口）
        dynamics_data = sync(u.get_dynamics_new())

        if not dynamics_data or not dynamics_data.get("items"):
            return {"username": username, "uid": uid, "dynamics": [], "message": "该用户暂无动态"}

        # 提取并格式化动态信息
        dynamics = []
        items = dynamics_data["items"][:count]  # 限制数量

        for item in items:
            if not item:
                continue

            dynamic_info = {
                "id": item.get("id_str", ""),
                "type": item.get("type", ""),
                "timestamp": item.get("pub_ts", 0),
                "content": "",
                "url": f"https://t.bilibili.com/{item.get('id_str', '')}",
            }

            # 根据动态类型提取内容
            if "modules" in item and "module_dynamic" in item["modules"]:
                module_dynamic = item["modules"]["module_dynamic"]

                # 提取文本内容
                if "desc" in module_dynamic and module_dynamic["desc"]:
                    dynamic_info["content"] = module_dynamic["desc"].get("text", "")

                # 如果是转发动态
                if "major" in module_dynamic and module_dynamic["major"]:
                    major = module_dynamic["major"]
                    if major.get("type") == "MAJOR_TYPE_OPUS":
                        # 图文动态
                        if "opus" in major and "summary" in major["opus"]:
                            dynamic_info["content"] = major["opus"]["summary"].get("text", "")
                    elif major.get("type") == "MAJOR_TYPE_ARCHIVE":
                        # 视频动态
                        if "archive" in major:
                            archive = major["archive"]
                            dynamic_info["content"] = f"发布了视频: {archive.get('title', '')}"
                            dynamic_info["video_info"] = {
                                "title": archive.get("title", ""),
                                "bvid": archive.get("bvid", ""),
                                "url": f"https://www.bilibili.com/video/{archive.get('bvid', '')}",
                            }

            # 如果没有提取到内容，使用基本信息
            if not dynamic_info["content"]:
                dynamic_info["content"] = f"动态类型: {dynamic_info['type']}"

            dynamics.append(dynamic_info)

        return {"username": username, "uid": uid, "dynamics": dynamics, "total_fetched": len(dynamics)}

    except Exception as e:
        return {"error": f"获取用户动态失败: {str(e)}"}


@mcp.tool()
def get_user_videos(username: str, count: int = 10) -> Dict[str, Any]:
    """
    获取指定用户的最新投稿视频

    Args:
        username: 用户名（如"技术爬爬虾"）
        count: 要获取的视频数量，默认10条

    Returns:
        包含用户投稿视频信息的字典
    """
    # 先通过用户名获取用户ID
    uid = _get_user_id_by_name(username)
    if not uid:
        return {"error": f"未找到用户: {username}"}

    # 创建用户对象
    u = user.User(uid)

    try:
        # 获取用户投稿视频
        videos_data = sync(u.get_videos(ps=count))

        if not videos_data or not videos_data.get("list") or not videos_data["list"].get("vlist"):
            return {"username": username, "uid": uid, "videos": [], "message": "该用户暂无投稿视频"}

        # 提取并格式化视频信息
        videos = []
        vlist = videos_data["list"]["vlist"]

        for video_item in vlist:
            video_info = {
                "title": video_item.get("title", ""),
                "bvid": video_item.get("bvid", ""),
                "aid": video_item.get("aid", 0),
                "description": video_item.get("description", ""),
                "duration": video_item.get("length", ""),
                "play_count": video_item.get("play", 0),
                "comment_count": video_item.get("comment", 0),
                "created": video_item.get("created", 0),
                "pic": video_item.get("pic", ""),
                "url": f"https://www.bilibili.com/video/{video_item.get('bvid', '')}",
            }
            videos.append(video_info)

        return {
            "username": username,
            "uid": uid,
            "videos": videos,
            "total_count": videos_data["list"].get("count", len(videos)),
            "total_fetched": len(videos),
        }

    except Exception as e:
        return {"error": f"获取用户投稿视频失败: {str(e)}"}


@mcp.tool()
def get_user_collections(username: str) -> Dict[str, Any]:
    """
    获取指定用户的合集信息

    Args:
        username: 用户名（如"技术爬爬虾"）

    Returns:
        包含用户合集信息的字典
    """
    # 先通过用户名获取用户ID
    uid = _get_user_id_by_name(username)
    if not uid:
        return {"error": f"未找到用户: {username}"}

    # 创建用户对象
    u = user.User(uid)

    try:
        # 获取用户合集
        channels = sync(u.get_channels())

        if not channels:
            return {"username": username, "uid": uid, "collections": [], "message": "该用户暂无合集"}

        # 提取并格式化合集信息
        collections = []

        for channel in channels:
            # 获取合集的基本信息
            try:
                channel_info = sync(channel.get_meta())
                if not channel_info:
                    continue

                collection_info = {
                    "id": channel_info.get("season_id") or channel_info.get("series_id", 0),
                    "title": channel_info.get("title", "未知标题"),
                    "description": channel_info.get("description", ""),
                    "cover": channel_info.get("cover", ""),
                    "video_count": channel_info.get("ep_count", 0),
                    "play_count": channel_info.get("stat", {}).get("view", 0) if channel_info.get("stat") else 0,
                    "type": "season" if channel_info.get("season_id") else "series",
                    "url": f"https://space.bilibili.com/{uid}/channel/collectiondetail?sid={channel_info.get('season_id') or channel_info.get('series_id', 0)}",
                }
                collections.append(collection_info)
            except Exception as e:
                # 如果获取单个合集信息失败，添加基本信息
                try:
                    basic_info = {
                        "id": getattr(channel, "id", 0),
                        "title": f"合集 {getattr(channel, 'id', 'Unknown')}",
                        "description": "",
                        "cover": "",
                        "video_count": 0,
                        "play_count": 0,
                        "type": getattr(channel, "type", "unknown"),
                        "url": f"https://space.bilibili.com/{uid}/lists",
                    }
                    collections.append(basic_info)
                except:
                    continue

        return {"username": username, "uid": uid, "collections": collections, "total_count": len(collections)}

    except Exception as e:
        return {"error": f"获取用户合集失败: {str(e)}"}


@mcp.tool()
def get_collection_videos(
    username: str, collection_name: str = "", collection_id: int = 0, count: int = 10
) -> Dict[str, Any]:
    """
    获取指定用户合集中的视频列表

    Args:
        username: 用户名（如"技术爬爬虾"）
        collection_name: 合集名称，可选
        collection_id: 合集ID，可选
        count: 要获取的视频数量，默认10条

    Returns:
        包含合集视频信息的字典
    """
    # 先通过用户名获取用户ID
    uid = _get_user_id_by_name(username)
    if not uid:
        return {"error": f"未找到用户: {username}"}

    # 创建用户对象
    u = user.User(uid)

    try:
        # 获取用户所有合集
        channels = sync(u.get_channels())

        if not channels:
            return {"error": f"用户 {username} 暂无合集"}

        # 查找目标合集
        target_channel = None

        if collection_id > 0:
            # 如果提供了合集ID，直接查找
            for channel in channels:
                try:
                    channel_info = sync(channel.get_meta())
                    if channel_info and (
                        channel_info.get("season_id") == collection_id or channel_info.get("series_id") == collection_id
                    ):
                        target_channel = channel
                        break
                except:
                    continue
        elif collection_name:
            # 如果提供了合集名称，模糊匹配
            for channel in channels:
                try:
                    channel_info = sync(channel.get_meta())
                    if channel_info and collection_name.lower() in channel_info.get("title", "").lower():
                        target_channel = channel
                        break
                except:
                    continue
        else:
            # 如果都没提供，返回第一个合集
            target_channel = channels[0] if channels else None

        if not target_channel:
            available_collections = []
            for channel in channels[:5]:  # 只显示前5个作为提示
                try:
                    channel_info = sync(channel.get_meta())
                    if channel_info:
                        available_collections.append(
                            {
                                "id": channel_info.get("season_id") or channel_info.get("series_id", 0),
                                "title": channel_info.get("title", "未知标题"),
                            }
                        )
                except:
                    continue

            return {
                "error": f"未找到指定合集: {collection_name or collection_id}",
                "available_collections": available_collections,
                "suggestion": "请使用准确的合集名称或ID",
            }

        # 获取合集信息
        collection_meta = sync(target_channel.get_meta())

        # 获取合集中的视频
        videos_data = sync(target_channel.get_videos(sort=ChannelOrder.DEFAULT, pn=1, ps=count))

        if not videos_data or not videos_data.get("archives"):
            return {
                "username": username,
                "collection_title": collection_meta.get("title", "未知合集"),
                "collection_id": collection_meta.get("season_id") or collection_meta.get("series_id", 0),
                "videos": [],
                "message": "该合集暂无视频",
            }

        # 提取并格式化视频信息
        videos = []
        archives = videos_data["archives"][:count]  # 限制数量

        for video_item in archives:
            video_info = {
                "title": video_item.get("title", ""),
                "bvid": video_item.get("bvid", ""),
                "aid": video_item.get("aid", 0),
                "description": video_item.get("desc", ""),
                "duration": video_item.get("duration_text", ""),
                "play_count": video_item.get("stat", {}).get("view", 0),
                "danmaku_count": video_item.get("stat", {}).get("danmaku", 0),
                "like_count": video_item.get("stat", {}).get("like", 0),
                "coin_count": video_item.get("stat", {}).get("coin", 0),
                "favorite_count": video_item.get("stat", {}).get("favorite", 0),
                "share_count": video_item.get("stat", {}).get("share", 0),
                "reply_count": video_item.get("stat", {}).get("reply", 0),
                "pubdate": video_item.get("pubdate", 0),
                "pic": video_item.get("pic", ""),
                "url": f"https://www.bilibili.com/video/{video_item.get('bvid', '')}",
            }
            videos.append(video_info)

        return {
            "username": username,
            "uid": uid,
            "collection_title": collection_meta.get("title", "未知合集"),
            "collection_id": collection_meta.get("season_id") or collection_meta.get("series_id", 0),
            "collection_description": collection_meta.get("description", ""),
            "total_videos": videos_data.get("page", {}).get("total", len(videos)),
            "videos": videos,
            "total_fetched": len(videos),
        }

    except Exception as e:
        return {"error": f"获取合集视频失败: {str(e)}"}


@mcp.tool()
def search_collection_by_keyword(username: str, keyword: str, count: int = 10) -> Dict[str, Any]:
    """
    在指定用户的所有合集中搜索包含关键词的视频

    Args:
        username: 用户名（如"技术爬爬虾"）
        keyword: 搜索关键词（如"MCP"、"AI与大模型"等）
        count: 每个合集最多返回的视频数量，默认10条

    Returns:
        包含搜索结果的字典
    """
    # 先通过用户名获取用户ID
    uid = _get_user_id_by_name(username)
    if not uid:
        return {"error": f"未找到用户: {username}"}

    # 创建用户对象
    u = user.User(uid)

    try:
        # 获取用户所有合集
        channels = sync(u.get_channels())

        if not channels:
            return {"error": f"用户 {username} 暂无合集"}

        search_results = []

        # 遍历所有合集
        for channel in channels:
            try:
                # 获取合集信息
                collection_meta = sync(channel.get_meta())
                if not collection_meta:
                    continue

                collection_title = collection_meta.get("title", "")

                # 检查合集标题是否包含关键词
                if keyword.lower() in collection_title.lower():
                    # 获取合集中的视频
                    videos_data = sync(channel.get_videos(sort=ChannelOrder.DEFAULT, pn=1, ps=count))

                    if videos_data and videos_data.get("archives"):
                        collection_videos = []
                        for video_item in videos_data["archives"][:count]:
                            video_info = {
                                "title": video_item.get("title", ""),
                                "bvid": video_item.get("bvid", ""),
                                "aid": video_item.get("aid", 0),
                                "duration": video_item.get("duration_text", ""),
                                "play_count": video_item.get("stat", {}).get("view", 0),
                                "pubdate": video_item.get("pubdate", 0),
                                "url": f"https://www.bilibili.com/video/{video_item.get('bvid', '')}",
                            }
                            collection_videos.append(video_info)

                        search_results.append(
                            {
                                "collection_title": collection_title,
                                "collection_id": collection_meta.get("season_id")
                                or collection_meta.get("series_id", 0),
                                "match_reason": "合集标题匹配",
                                "videos": collection_videos,
                                "video_count": len(collection_videos),
                            }
                        )

            except Exception as e:
                # 如果某个合集处理失败，跳过继续处理其他合集
                continue

        return {
            "username": username,
            "uid": uid,
            "search_keyword": keyword,
            "matched_collections": search_results,
            "total_collections": len(search_results),
            "total_videos": sum(result["video_count"] for result in search_results),
        }

    except Exception as e:
        return {"error": f"搜索合集视频失败: {str(e)}"}


def main():
    """MCP 服务器入口点"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    print("Hello from bilibili-tool-mcp-server!")
    main()
