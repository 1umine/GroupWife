import random
import time
from typing import Any, Dict, List, Union, Tuple

from aiocache import cached
from nonebot import on_message, on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message
from nonebot.exception import ActionFailed
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.params import RegexGroup


class Config:
    cooldown_time: int = 60  # 冷却时间
    max_wife_count: int = 10  # 一次最大抽取老婆数量
    cooldown_prompt: tuple = ("快醒醒", "你哪来的老婆", "才不到几分钟就要换老婆了嘛？")
    """换老婆冷却提示"""

    exceed_prompt: tuple = (
        "注意身体哦", 
        "真是花心呢", 
        "你要的太多了哦", 
        f"最多{max_wife_count}个，不能再多了"
    )
    """一次抽取老婆数量超出限额时的提示"""

    change_harem_prompt = ("爬", "冷却中，上次要的越多冷却时间越长", "慢点吃桃，别噎着了")
    """换后宫冷却提示"""

    exclude_user: tuple = (
        2854196310,  #  Q群管家
    )  
    """不包括这里的用户"""


zh_number = {k:v for v,k in enumerate("二三四五六七八九十", 2)}
cooldown_dict: Dict[int, int] = {}
"""
记录冷却中的用户
"""


def node_custom_gocq(uin: int, name: str, content: Union[str, Message]):
    """
    go-cqhttp 的自定义转发消息结点
    uin: 发送者QQ
    name: 发送者昵称
    content: 发送内容
    """
    return MessageSegment("node", {"name": name, "uin": str(uin), "content": content})


@cached(600)
async def get_group_memberlist(bot: Bot, group_id: int):
    return await bot.get_group_member_list(group_id=group_id)


def get_top_n(lst: List[Dict[str, Any]], num: int = 50):
    """
    获取按最近发言时间排序前 num 名群成员的 QQ 和 群名片
    """
    if num > len(lst):
        return [(i["user_id"], i["card"], i["nickname"]) for i in lst]

    lst = sorted(lst, key=lambda x: x.get("last_sent_time", 0), reverse=True)
    return [(i["user_id"], i["card"], i["nickname"]) for i in lst[:num]]


def choose_wife(wife_list: list, exclude: Union[list, tuple], n: int = 1):
    """
    wife_list: 后宫  [(user_id, card, nickname), ...]

    exclude: 不要的

    n: 选几个
    """
    for w in wife_list:
        if w[0] in exclude:
            wife_list.remove(w)
    if len(wife_list) >= n:
        return random.sample(wife_list, n)
    else:
        return wife_list


async def want_wife(bot: Bot, event: GroupMessageEvent):
    msg = event.get_plaintext().strip().lstrip("今天")
    return msg in ("谁是我老婆", "我老婆是谁", "哪个群友是我老婆", "抽老婆")


groupwife = on_message(rule=want_wife, priority=50, block=True)


@groupwife.handle()
async def h1(bot: Bot, event: GroupMessageEvent):
    if cooldown_dict.get(event.user_id, 0) > time.time():
        await groupwife.finish(random.choice(Config.cooldown_prompt))

    user_list = await get_group_memberlist(bot, group_id=event.group_id)
    wife_list = get_top_n(user_list, num=51 + len(Config.exclude_user))

    wife: Tuple[int, str, str] = choose_wife(
        wife_list, Config.exclude_user + (event.user_id,)
    )[0]
 
    avatar = MessageSegment.image(f"https://q1.qlogo.cn/g?b=qq&nk={wife[0]}&s=640?")
    name = wife[1] if wife[1].strip() else wife[2]

    msg = "今天你的群老\u202D婆是：\n" + avatar + f"\n{name} ({wife[0]})"
    try:
        await bot.send(event, message=msg, at_sender=True)
        cooldown_dict[event.user_id] = int(time.time()) + Config.cooldown_time
    except ActionFailed:
        await bot.send(event, message="出错了，你老婆没了，但绝对不是我的错！")


pattern = r"^群?老婆([1-9]\d?|[二三四五六七八九十])[抽连]抽?$"
open_harem = on_regex(pattern, priority=50, block=True)
"""开后宫"""


@open_harem.handle()
async def _(
    bot: Bot, 
    event: GroupMessageEvent, 
    matcher: Matcher, 
    matchgroup: Tuple[str] = RegexGroup()
):
    if cooldown_dict.get(event.user_id, 0) > time.time(): 
        await  open_harem.finish(random.choice(Config.change_harem_prompt))

    num_str = matchgroup[0]
    wife_count = 1  # 老婆数量
    if num_str.isdigit():
        wife_count = int(num_str)
    else:
        wife_count = zh_number.get(num_str, 1)

    if wife_count > Config.max_wife_count:  # 超出后宫老婆数量限制时结束
        await open_harem.finish(random.choice(Config.exceed_prompt))

    user_list = await get_group_memberlist(bot, group_id=event.group_id)
    wife_list = get_top_n(user_list, num=51 + len(Config.exclude_user))

    harem: List[Tuple[int, str, str]] = choose_wife(
        wife_list, 
        Config.exclude_user + (event.user_id,), 
        wife_count
    )  # 开后宫！

    if wife_count <= 3:
        msg = MessageSegment.at(event.user_id) + "你的后宫：\n"
        for w in harem:
            avatar = MessageSegment.image(f"https://q1.qlogo.cn/g?b=qq&nk={w[0]}&s=100?")
            name = w[1] if w[1].strip() else w[2]
            msg += avatar + f"{name} ({w[0]})\n"
        try:
            await bot.send(event, message=msg)
            cooldown_dict[event.user_id] = int(time.time()) + Config.cooldown_time * wife_count
        except ActionFailed:
            await bot.send(event, message="阿巴阿巴。。。出错了，但绝对不是我的错！")
    else:
        sender_name = event.sender.card if event.sender.card.strip() else event.sender.nickname
        forward_msg = [
            node_custom_gocq(bot.self_id, "喵喵喵",  f"【{sender_name}】({event.user_id}) の 后宫")
        ]
        for w in harem:
            avatar = MessageSegment.image(f"https://q1.qlogo.cn/g?b=qq&nk={w[0]}&s=100?")
            name = w[1] if w[1].strip() else w[2]
            msg_content = avatar + f"{name} ({w[0]})"
            forward_msg.append(node_custom_gocq(bot.self_id, "喵喵喵", msg_content))

        try:
            await bot.send_group_forward_msg(
                group_id=event.group_id,
                messages=forward_msg
            )
            cooldown_dict[event.user_id] = int(time.time()) + Config.cooldown_time * wife_count
        except ActionFailed:
            await bot.send(event, message="阿巴阿巴。。。出错了，但绝对不是我的错！")
