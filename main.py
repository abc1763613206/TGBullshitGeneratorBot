import os,re
import random
import time

from data import backsays
from data import frontsays
from data import quotes
from data import text

if not os.path.exists("config.py"):
    print("Error: 配置文件不存在，请检查是否正确配置！")
    exit(0)
import config


xx = ""


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


if config.USE_PROXY:
    apihelper.proxy = config.HTTP_PROXY
#telebot.logger.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.INFO)

@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    bot.reply_to(message,"狗屁不通生成器(https://github.com/menzi11/BullshitGenerator) 的 Telegram 移植版本，如有疑问请 @abc1763613206")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    logging.info(message.text)
    if len(message.text) > 20:
        bot.reply_to(message,'你说的内容太长了！何不切分一下试试？')
        return
    bot.reply_to(message, Process(message.text,1000))

#@bot.inline_handler(lambda query: SetQText(query.query) )
@bot.inline_handler(lambda query: query.query != "" )
def query_text(inline_query):
    qtext = inline_query.query
    if qtext == "":
        pass
    logging.info(qtext)
    try:
        r4 = types.InlineQueryResultArticle('4', '小作文(200字)', types.InputTextMessageContent(Process(qtext,200)))
        r = types.InlineQueryResultArticle('1', '普通玩法(600字)', types.InputTextMessageContent(Process(qtext,600)))
        r2 = types.InlineQueryResultArticle('2', '加强玩法(1000字)', types.InputTextMessageContent(Process(qtext,1000)))
        r3 = types.InlineQueryResultArticle('3', '再多来些(2000字)', types.InputTextMessageContent(Process(qtext,2000)))
        bot.answer_inline_query(inline_query.id, [r, r2, r3, r4], cache_time=1)
    except Exception as e:
        print(e)



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
        logging.info("准备处理信息")
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        exit(0)
