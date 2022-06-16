# GroupWife（自用插件）
随机抽取一个群友成为你的老婆

适用 [Nonebot2](https://github.com/nonebot/nonebot2) beta1 及以上

懒得发布插件，要用自己复制代码去用吧，记得装依赖（提示没有啥就 pip install 啥）

代码里这些可以改，当配置用
```python
Cooldown(60, prompt=cooldown_prompt, isolate_level=CooldownIsolateLevel.GROUP_USER) # 60可以改成别的数字，表示冷却时间

cooldown_prompt = ("快醒醒", "你哪来的老婆", "才不到一分钟就要换老婆了嘛？") # 冷却提示语

exclude_user = (
    2854196310, # Q群管家
) # 这里面的人不会成为你的老婆
```


~~Baka，你根本没有老婆~~
