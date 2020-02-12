from requests import Session
import json
import datetime
import pandas as pd
import logging

# install by " pip install python-telegram-bot "
import telegram
from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ABOUT_US, LISTED, CM, SNS, TTU, PR = map(chr, range(6))
TOP_MENU, END, GOBACK, START_OVER = map(chr, range(6, 10))

# Top menu (with callbacks)
def top_menu(update, context):

    text = 'Hi! TrustVerse Team here. Glad to see that you are interested. Navigate through our bot and ' \
           'gain access to basic information about us and our token(TRV).'
    buttons = [
        [InlineKeyboardButton(text='About Us', callback_data=str(ABOUT_US))],
        [InlineKeyboardButton(text='Listed Exchanges', callback_data=str(LISTED))],
        [InlineKeyboardButton(text='TRV Communities', callback_data=str(CM))],
        [InlineKeyboardButton(text='SNS Channels', callback_data=str(SNS))],
        [InlineKeyboardButton(text='Talk to us', url="https://t.me/jhj1123"),
         InlineKeyboardButton(text='Price', callback_data=str(PR))]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    if context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False

    return TOP_MENU


def about_us(update, context):

    text = "We are ~~~~ ~~~~ "
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("MAIN", callback_data=str(END))]])
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    context.user_data[START_OVER] = True
    return GOBACK


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

reply_exchange_list = [
    InlineKeyboardButton("BiKi", url = "https://www.biki.com/zh_CN/trade/TRV_USDT"),
    InlineKeyboardButton("Bithumb (TRV/KRW)", url="https://www.bithumb.com/trade/order/TRV_KRW"),
    InlineKeyboardButton("Bithumb Global (TRV/BTC)", url="https://www.bithumb.pro/en-us/spot/trade;symbol=TRV_BTC"),
    InlineKeyboardButton("bitcoin.com", url = "https://exchange.bitcoin.com/exchange/TRV-to-BCH"),
    InlineKeyboardButton("MAIN", callback_data=str(END))
]

def reply_exchange(update, context):
    text = "Here are the links for the exchanges TRV tokens have been enlisted on." \
           "We offer up to 4 trading pairs, including BTC, BCH, USDT, KRW"
    reply_markup = InlineKeyboardMarkup(build_menu(reply_exchange_list,n_cols=2))
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    context.user_data[START_OVER] = True
    return GOBACK

reply_SNS_list = [
    InlineKeyboardButton("Medium", url="https://medium.com/@trustverse_official"),
    InlineKeyboardButton("Twitter", url="https://twitter.com/TrustVerse?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor"),
    InlineKeyboardButton("Telegram", url="https://t.me/trustverse_officialchannel"),
    InlineKeyboardButton("Weibo", url="https://weibo.com/6793468977/IpgaGFWWS"),
    InlineKeyboardButton("Official Website","https://www.trustverse.io")
]

def reply_SNS(update, context):
    text = "Here are the links for our SNS channels. " \
           "Explore the ones that suit your native language to find out more about who we are"
    reply_markup = InlineKeyboardMarkup(build_menu(reply_SNS_list, n_cols=2,
                                                   footer_buttons=InlineKeyboardButton("MAIN", callback_data=str(END))))
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    context.user_data[START_OVER] = True
    return GOBACK

reply_CM_list = [
    InlineKeyboardButton("Telegram (EN)", url="https://t.me/trustverse_officialchannel"),
    InlineKeyboardButton("Telegram (CN)", url="https://t.me/trustverse_officialchina"),
    InlineKeyboardButton("WeChat (CN)", url="https://www.weibo.com"),
    InlineKeyboardButton("Open Kakao (KR)", url="https://open.kakao.com/o/gyiFnGfb"),
    InlineKeyboardButton("Official Website","https://www.trustverse.io")
]

def reply_CM(update, context):
    text = "Here are the links for Communities that we manage. " \
           "Explore the ones that suit your native language to join the discussion with fellow TRV investors"
    reply_markup = InlineKeyboardMarkup(build_menu(reply_CM_list, n_cols=2,
                                                   footer_buttons=InlineKeyboardButton("MAIN", callback_data=str(END))))
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    context.user_data[START_OVER] = True
    return GOBACK

def reply_PR(update, context):
    url = "https://api.coingecko.com/api/v3/coins/trustverse/tickers"

    session = Session()
    response = session.get(url)
    fdata=json.loads(response.text)

    ticker_data = pd.DataFrame.from_dict(fdata['tickers'])
    ticker_data['market'] = ticker_data['market'].apply(lambda x: x['name'])

    prices = ""

    for i in ["Biki", "Bithumb","Bithumb Global", "Bitcoin.com"]:
        time_info = datetime.datetime.fromisoformat(ticker_data[ticker_data['market'] == i]['last_fetch_at'].values[0])
        sl_time_printable = "London (UTC +0), " + time_info.strftime("%y/%m/%d, %H:%M")
        if i == "Bithumb Global":
            for j in ticker_data[ticker_data['market']==i]['last'].values:
                prices += "\N{money bag} *{} ({})* : {:.8f} \n" \
                          "\U0001F570 {} \n".format(i, ticker_data[ticker_data['market']==i]["target"].values[0],j,sl_time_printable)
        else:

            prices += "\N{money bag} *{} ({})* : {:.8f} \n" \
                      "\U0001F570 {} \n".format(i, ticker_data[ticker_data['market']==i]["target"].values[0],
                                                   ticker_data[ticker_data['market']==i]['last'].values[0],sl_time_printable)

    text = "TrustVerse (TRV) - CoinGecko \n" \
           "-------------------------------- \n" \
           + "\n" + prices
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("MAIN", callback_data=str(END))]])
    update.callback_query.edit_message_text(text=text, reply_markup=reply_markup,parse_mode=telegram.ParseMode.MARKDOWN)
    context.user_data[START_OVER] = True
    return GOBACK

# Error handler
def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

TOKEN = "924781641:AAGC-n4kCf6-tKxKQUeihq25LQRfnmYme00"

def unknown_param(update, context):
    text = "For any enquiries please contact us through the link below"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton(text='Talk to us', url="https://t.me/jhj1123"),
                                     InlineKeyboardButton(text="MAIN", callback_data=str(END))]])
    update.message.reply_text(text=text, reply_markup=buttons)
    context.user_data[START_OVER] = True
    return GOBACK

def main():

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher


    top_convo = ConversationHandler(
        entry_points=[CommandHandler('start', top_menu)],

        states={
            GOBACK: [CallbackQueryHandler(top_menu, pattern='^' + str(END) + '$')],
            TOP_MENU: [CallbackQueryHandler(about_us, pattern='^' + str(ABOUT_US) + '$'),
                       CallbackQueryHandler(reply_exchange, pattern='^' + str(LISTED) + '$'),
                       CallbackQueryHandler(reply_CM, pattern='^' + str(CM) + '$'),
                       CallbackQueryHandler(reply_SNS, pattern='^' + str(SNS) + '$'),
                       CallbackQueryHandler(reply_PR, pattern='^' + str(PR) + '$')]
        },

        fallbacks={MessageHandler(Filters.text, unknown_param),
                   MessageHandler(Filters.command, unknown_param)}
    )


    dp.add_handler(top_convo)

    # log errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()



