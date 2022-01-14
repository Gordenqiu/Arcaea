from hoshino.config import SUPERUSERS
from hoshino import Service, priv
from hoshino.typing import CQEvent

from .sql import asql
from .api import *
from .draw import *

help = '''
arcinfo 查询b30，需等待1-2分钟
arcre   使用本地查分器查询最近一次游玩成绩
arcre:  指令结尾带：使用est查分器查询最近一次游玩成绩
arcre: [arcid]  使用好友码查询TA人
arcre: [@]  使用@ 查询好友
arcup   查询用账号添加完好友，使用该指令绑定查询账号，添加成功即可使用arcre指令
arcbind [arcid] [arcname]   绑定用户
arcun   解除绑定
arcrd [定数] [难度] 随机一首该定数的曲目，例如：`arcrd 10.8`，`arcrd 10+`，`arcrd 9+ byd`'''

diffdict = {
    '0' : ['pst', 'past'],
    '1' : ['prs', 'present'],
    '2' : ['ftr', 'future'],
    '3' : ['byd', 'beyond']
}

sv = Service('arcaea', manage_priv=priv.ADMIN, enable_on_default=False, visible=True, help_=help)

@sv.on_prefix(['arcinfo', 'ARCINFO', 'Arcinfo'])
async def arcinfo(bot, ev:CQEvent):
    qqid = ev.user_id
    msg = ev.message.extract_plain_text().strip()
    if ev.message[0].type == 'at':
        qqid = int(ev.message[0].data['qq'])
    result = asql.get_user(qqid)
    if msg:
        if msg.isdigit() and len(msg) == 9:
            arcid = msg
        else:
            await bot.finish(ev, '仅可以使用好友码查询', at_sender=True)
    elif not result:
        await bot.finish(ev, '该账号尚未绑定，请输入 arcbind arcid(好友码) arcname(用户名)', at_sender=True)
    else:
        arcid = result[0]
    await bot.send(ev, '正在查询，请耐心等待...')
    info = await draw_info(arcid)
    await bot.send(ev, info, at_sender=True)

@sv.on_prefix(['arcre', 'Arcre', 'ARCRE'])
async def arcre(bot, ev:CQEvent):
    qqid = ev.user_id
    est = False
    msg = ev.message.extract_plain_text().strip()
    if ev.message[0].type == 'at':
        qqid = int(ev.message[0].data['qq'])
    result = asql.get_user(qqid)
    if msg:
        if msg.isdigit() and len(msg) == 9:
            result = asql.get_user_code(msg)
            if not result:
                await bot.finish(ev, '该账号尚未绑定，请输入 arcbind arcid(好友码) arcname(用户名)', at_sender=True)
            user_id = result[0]
        elif msg == ':' or msg == '：':
            if not result:
                await bot.finish(ev, '该账号尚未绑定，请输入 arcbind arcid(好友码) arcname(用户名)', at_sender=True)
            else:
                est = True
                user_id = result[0]
        elif ':' in msg or '：' in msg:
            user_id = msg[1:]
            if user_id.isdigit() and len(user_id) == 9:
                est = True
            else:
                await bot.finish(ev, '请输入正确的好友码', at_sender=True)
        else:
            await bot.finish(ev, '仅可以使用好友码查询', at_sender=True)
    elif not result:
        await bot.finish(ev, '该账号尚未绑定，请输入 arcbind arcid(好友码) arcname(用户名)', at_sender=True)
    elif result[1] == None:
        await bot.finish(ev, '该账号已绑定但尚未添加为好友，请联系BOT管理员添加好友并执行 arcup 指令', at_sender=True)
    else:
        user_id = result[1]
    info = await draw_score(user_id, est)
    await bot.send(ev, info, at_sender=True)

@sv.on_prefix(['arcrd', 'Arcrd', 'ARCRD'])
async def arcrd(bot, ev:CQEvent):
    args: list[str] = ev.message.extract_plain_text().strip().split()
    diff = None
    if not args:
        await bot.finish(ev, '请输入定数')
    elif len(args) == 1:
        try:
            rating = float(args[0]) * 10
            if not 10 <= rating < 116:
                await bot.finish(ev, '请输入定数：1-11.5 | 9+ | 10+')
            plus = False
        except ValueError:
            if '+' in args[0] and args[0][-1] == '+':
                rating = float(args[0][:-1]) * 10
                if rating % 10 != 0:
                    await bot.finish(ev, '仅允许定数为：9+ | 10+')
                if not 90 <= rating < 110:
                    await bot.finish(ev, '仅允许定数为：9 | 10')
                plus = True
            else:
                await bot.finish(ev, '请输入定数：1-11.5 | 9+ | 10+')
    elif len(args) == 2:
        try:
            rating = float(args[0]) * 10
            plus = False
            if not 10 <= rating < 116:
                await bot.finish(ev, '请输入定数：1-11.5 | 9+ | 10+')
            if args[1].isdigit():
                if args[1] not in diffdict:
                    await bot.finish(ev, '请输入正确的难度：3 | byd | beyond')
                else:
                    diff = int(args[1])
            else:
                for d in diffdict:
                    if args[1].lower() in diffdict[d]:
                        diff = int(d)
                        break
        except ValueError:
            if '+' in args[0] and args[0][-1] == '+':
                rating = float(args[0][:-1]) * 10
                if rating % 10 != 0:
                    await bot.finish(ev, '仅允许定数为：9+ | 10+')
                if not 90 <= rating < 110:
                    await bot.finish(ev, '仅允许定数为：9 | 10')
                plus = True
                if args[1].isdigit():
                    if args[1] not in diffdict:
                        await bot.finish(ev, '请输入正确的难度：3 | byd | beyond')
                    else:
                        diff = int(args[1])
                else:
                    for d in diffdict:
                        if args[1].lower() in diffdict[d]:
                            diff = int(d)
                            break
            else:
                await bot.finish(ev, '请输入定数：1-11.5 | 9+ | 10+')
    else:
        await bot.finish(ev, '请输入正确参数')
    if not rating >= 70 and (diff == '2' or diff == '3'):
        await bot.finish(ev, 'ftr | byd 难度没有定数小于7的曲目')
    msg = random_music(rating, plus, diff)
    await bot.send(ev, msg)

@sv.on_fullmatch(['arcup', 'arcupdate', 'Arcup'])
async def arcup(bot, ev:CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '请联系BOT管理员更新')
    await newbind(bot)

@sv.on_prefix(['arcbind', 'ARCBIND', 'Arcbind'])
async def bind(bot, ev:CQEvent):
    qqid = ev.user_id
    gid = ev.group_id
    arcid = ev.message.extract_plain_text().strip().split()
    try:
        if not arcid[0].isdigit() and len(arcid[0]) != 9:
            await bot.finish(ev, '请重新输入好友码和用户名\n例如：arcbind 114514810 sb616', at_sender=True)
        elif not arcid[1]:
            await bot.finish(ev, '请重新输入好友码和用户名\n例如：arcbind 114514810 sb616', at_sender=True)
    except IndexError:
        await bot.finish(ev, '请重新输入好友码和用户名\n例如：arcbind 114514810 sb616', at_sender=True)
    result = asql.get_user(qqid)
    if result:
        await bot.finish(ev, '您已绑定，如需要解绑请输入arcun', at_sender=True)
    msg = bindinfo(qqid, arcid[0], arcid[1], gid)
    await bot.send(ev, msg, at_sender=True)
    await bot.send_private_msg(user_id=SUPERUSERS[0], message=f'Code:{arcid[0]}\nName:{arcid[1]}\n申请加为好友')

@sv.on_fullmatch(['arcun', 'Arcun', 'ARCUN'])
async def unbind(bot, ev:CQEvent):
    qqid = ev.user_id
    result = asql.get_user(qqid)
    if result:
        if asql.delete_user(qqid):
            msg = '解绑成功'
        else:
            msg = '数据库错误'
    else:
        msg = '您未绑定，无需解绑'
    await bot.send(ev, msg, at_sender=True)