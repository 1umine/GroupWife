# GroupWife（自用为主，不保证稳定性）

随机抽取 一个/n个 群友成为你的老婆

## 更新内容 2022/7/3
> 可以开后宫了，不过最多10个，发 `老婆n连` 或 `老婆n抽` 就行


适用 [Nonebot2](https://github.com/nonebot/nonebot2) beta1

懒得发布插件，要用就复制代码用吧，记得装依赖（提示没有啥 module 就 pip install 啥）

配置
```python
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
```


~~Baka,你可少做点梦吧~~
