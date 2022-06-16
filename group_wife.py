import random
from aiocache import cached
from typing import Dict, List, Tuple, Any

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot import on_message
from nonebot.exception import ActionFailed
from nonebot.permission import SUPERUSER

from nonebot.adapters.onebot.v11.helpers import Cooldown, CooldownIsolateLevel


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


async def want_wife(bot: Bot, event: GroupMessageEvent):
    msg = event.get_plaintext().strip().lstrip("今天")
    return msg in ("谁是我老婆", "我老婆是谁", "哪个群友是我老婆")


groupwife = on_message(rule=want_wife, priority=50, block=True)
cooldown_prompt = ("快醒醒", "你哪来的老婆", "才不到一分钟就要换老婆了嘛？")
exclude_user = (
    2854196310, # Q群管家
)


@groupwife.handle(
    parameterless=[
        Cooldown(60, prompt=cooldown_prompt, isolate_level=CooldownIsolateLevel.GROUP_USER)
    ]
)
async def h1(bot: Bot, event: GroupMessageEvent):
    user_list = await get_group_memberlist(bot, group_id=event.group_id)
    wife_list = get_top_n(user_list)
    for w in wife_list:
        if w[0] in exclude_user + (event.user_id,):
            wife_list.remove(w)

    wife = random.choice(wife_list)

    avatar = MessageSegment.image(f"https://q1.qlogo.cn/g?b=qq&nk={wife[0]}&s=640?")
    name = wife[1] if wife[1].strip() else wife[2]
    msg = "今天你的群老\u202D婆是：\n" + avatar + f"\n{name} ({wife[0]})"
    try:
        await bot.send(event, message=msg, at_sender=True)
    except ActionFailed:
        await bot.send(event, message="出错了，你老婆没了，但绝对不是我的错！")
