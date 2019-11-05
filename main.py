import os
import sys
import string
import random
import time
import subprocess
import traceback
from time import sleep

from data import *

if not os.path.exists("config.py"):
    print("Error: 配置文件不存在，请检查是否正确配置！")
    exit(0)
import config


xx = ""

def getReportID():
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(8):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    return salt


totalcount=0
chatcount=0
inlinecount=0


def getanother():

    xx = " "
    xx += "\r\n"
    xx += "    "
    return xx


samepoint = 2

def shuffle(List):
    global samepoint
    pool = list(List) * samepoint
    while True:
        random.shuffle(pool)
        for element in pool:
            yield element

nextsays = shuffle(text)
nextquote = shuffle(quotes)

def getquotes():
    global nextquote
    xx = next(nextquote)
    xx = xx.replace("a",random.choice(frontsays) )
    xx = xx.replace("b",random.choice(backsays) )
    return xx


def Process(msg,maxlength):
    global nextsays
    xx=msg
    tmp = str()
    while ( len(tmp) < maxlength ) :
        branch = random.randint(0,100)
        if branch < 5:
            while (tmp[-1] == '，'):
                tmp += next(nextsays)
            while (tmp[-1] == '：'):
                tmp += next(nextsays)
            tmp += getanother()
        elif branch < 20 :
            tmp += getquotes()
        else:
            tmp += next(nextsays)
    while (tmp[-1] == '，'):
        tmp += next(nextsays)
    while (tmp[-1] == '：'):
        tmp += next(nextsays)
    tmp = "    " + tmp
    tmp = tmp.replace("x",xx)
    #print(tmp)
    return tmp



import logging
import telebot
bot = telebot.TeleBot(config.TOKEN)
from telebot import apihelper
from telebot import types
from telebot import util

if config.USE_PROXY:
    apihelper.proxy = config.HTTP_PROXY
#telebot.logger.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.INFO)

def get_githash():
    try:
        ret = str(subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8'))
    except Exception as e:
        ret = str(e)
    return ret

def get_gittime():
    try:
        ret = str(subprocess.check_output(['git', 'log', '--pretty=format:\"%cd\"', '-1']).decode('utf-8'))
    except Exception as e:
        ret = str(e)
    return ret

def getstat(mode):
    global totalcount
    global inlinecount
    global chatcount
    ret = "欢迎使用\"狗屁不通生成器\"的 Telegram 移植版本！\n"
    ret += "源码：https://github.com/abc1763613206/TGBullshitGeneratorBot\n"
    ret += "当前 commit 版本 {}最后更新于 {}\n".format(get_githash(),get_gittime())
    ret += data_stat()
    ret += "\n自上一次重启以来，总调用{}次，其中 inline 模式{}次，私聊模式{}次\n".format(str(totalcount),str(inlinecount),str(chatcount))
    if mode == 0:
        ret += "您正在使用 inline 模式，如有疑问请 @abc1763613206"
    else:
        ret += "您正在使用 私聊 模式，如有疑问请 @abc1763613206"
    return ret


@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    bot.reply_to(message,"狗屁不通生成器(https://github.com/menzi11/BullshitGenerator) 的 Telegram 移植版本，如有疑问请 @abc1763613206")

@bot.message_handler(commands=['stat'])
def send_stat(message):
    try:
        global totalcount
        totalcount += 1
        global chatcount
        chatcount += 1
        bot.reply_to(message,getstat(1))
    except Exception as e:
        traceback.print_exc()
        logging.error(e)




@bot.message_handler(func=lambda m: True)
def echo_all(message):
    try:
        global totalcount
        totalcount += 1
        global chatcount
        chatcount += 1
        if message.content_type != 'text':
            bot.reply_to(message,'抱歉，我还只支持文字！')
        logging.info(str('Chat::@{} ({} {}): {}'.format(message.from_user.username, message.from_user.first_name, message.from_user.last_name, message.text)))
        #print(message.type)

        #print(type(message.from_user))
        #if len(message.text) > 15:
        #    bot.reply_to(message,'你说的内容太长了！何不切分一下试试？')
        #    return
        ret = Process(message.text, 1000)
        if len(ret) >= 4500:
            bot.reply_to(message, '您要说的内容实在太长了，将为您分段处理！')
            splitted_ret = util.split_string(ret, 3000)
            logging.info(str('Too long.Split into '+str(len(splitted_ret))+' parts'))
            for sret in splitted_ret:
                bot.reply_to(message, sret)
                sleep(0.3)
        else:
            bot.reply_to(message,ret)

    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' +str(e)))
        bot.send_message(message.from_user.id,'抱歉，我出现错误，识别ID为 '+rid+'\n\n信息如下：\n'+str(e)+'\n\n请将这条信息 Forward 给 @abc1763613206 中所列的用户 进行处理！')
#@bot.inline_handler(lambda query: SetQText(query.query) )
@bot.inline_handler(lambda query: query.query != "" )
def query_text(inline_query):
    global totalcount
    totalcount += 1
    global inlinecount
    inlinecount += 1
    qtext = inline_query.query
    if qtext == "":
        pass
    logging.info(str('Inline:: @{} ({} {}): {}').format(inline_query.from_user.username, inline_query.from_user.first_name, inline_query.from_user.last_name, inline_query.query))
    
    try:
        if len(qtext) > 15:
            r5 = types.InlineQueryResultArticle('1','你要说的内容太长了！将直接发送原消息(小提示：私聊模式可以发送长消息哦！)',types.InputTextMessageContent(str(qtext)))
            r6 = types.InlineQueryResultArticle('2','查看当前统计(Beta)',types.InputTextMessageContent(getstat(0)))
            bot.answer_inline_query(inline_query.id, [r5, r6], cache_time=1)
        else:
            r4 = types.InlineQueryResultArticle('1', '小作文(200字)', types.InputTextMessageContent(Process(qtext,200)))
            r = types.InlineQueryResultArticle('2', '普通玩法(600字)', types.InputTextMessageContent(Process(qtext,600)))
            r2 = types.InlineQueryResultArticle('3', '加强玩法(1000字)', types.InputTextMessageContent(Process(qtext,1000)))
            r3 = types.InlineQueryResultArticle('4', '再多来些(1500字)', types.InputTextMessageContent(Process(qtext,1500)))
            r6 = types.InlineQueryResultArticle('5', '查看当前统计(Beta)', types.InputTextMessageContent(getstat(0)))
            bot.answer_inline_query(inline_query.id, [r4, r, r2, r3, r6], cache_time=1)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(e)))


@bot.inline_handler(lambda query: query.query == "")
def query_text(inline_query):
    try:
        r1 = types.InlineQueryResultArticle('1', '查看当前统计(Beta)(不会即时更新)', types.InputTextMessageContent(getstat(0)))
        r2 = types.InlineQueryResultArticle('2', '您正在使用 inline 模式，请输入内容以便生成', types.InputTextMessageContent('？'))
        bot.answer_inline_query(inline_query.id, [r1, r2], cache_time=360)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(e)))


#@bot.inline_handler(lambda query: True)
#def query_text(inline_query):
#    try:
#        r = types.InlineQueryResultArticle('1', 'Result', types.InputTextMessageContent('Result message.'))
#        r2 = types.InlineQueryResultArticle('2', 'Result2', types.InputTextMessageContent('Result message2.'))
#        bot.answer_inline_query(inline_query.id, [r, r2])
#    except Exception as e:
#        print(e)

def main_loop():
    bot.polling(True)
    while 1:
        time.sleep(3)


if __name__ == '__main__':
    try:
        logging.info(data_stat())
        logging.info("当前 commit 版本 {}最后更新于 {}\n".format(get_githash(),get_gittime())) # git supported
        logging.info("准备处理信息")
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        exit(0)
    except Exception as e:
        logging.error(e)
        traceback.print_exc()
