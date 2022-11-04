"""MAIN"""
import json
from  fudstop_application.MarketView import LosersView,GainersView,NearHigh,PressRelease,ShortInterest,LosersDropdown,GainersDropdown
import re
from viewsapp.learnviews import LowFloatDropdown
from datetime import datetime, timedelta
from datetime import date
from time import sleep
import requests
import stocksera
import disnake
import webull
from menus import Menu
import finnhub
from bs4 import BeautifulSoup
import pyEX as p
from disnake.ext import commands
from selectmenus.rules import RulesSelect,RulesSelect2
from viewsapp.learnviews import MainView2,MainSelect,MainSelectView,TechDropdown,TechDropdown2, CandleDropdown
from cfg import token, nasdaq,stockserakey,finnhubkey
from docs_dict import docs_dict
from webull_tickers import ticker_list
from autocomp import ticker_autocomp, video_autocomp,document_autocomp,tickerlist_autocomp
from smiles import vids_dict
from webull import webull as weballz
PREFIX = ">>"
client = stocksera.Client(api_key=stockserakey)
intents = disnake.Intents.all()
c = p.Client(version="stable", api_token="pk_541ac5de367242fb8da4a544e4a8397e")


bot = commands.Bot(
    command_prefix=">>",
    intents=intents,
    case_insensitive=True)

@bot.command()
async def dadjoke(ctx):
    url = "https://dad-jokes.p.rapidapi.com/random/joke"

    headers = {
        "X-RapidAPI-Key": "cd36127562msh09bad643a11b69cp16a83cjsnce170739c830",
        "X-RapidAPI-Host": "dad-jokes.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers).json()
    body = response['body']
    setup = body[0]['setup']
    punchline = body[0]['punchline']
    print(f"```py\n{setup}, ||{punchline}||```")

    await ctx.send(f"```py\n{setup}....```")
    sleep(5)
    await ctx.send(f"```py\n{punchline}```")
@bot.command()
async def ta(ctx):
    view = disnake.ui.View()
    view.add_item(TechDropdown())
    view.add_item(TechDropdown2())
    view.add_item(CandleDropdown())
    await ctx.send(view=view)


@bot.slash_command()
async def all_in_one(interaction: disnake.ApplicationCommandInteraction, ticker: str=commands.Param(autocomplete=ticker_autocomp)):
    await interaction.response.defer(with_message=True)
    symbol = ticker
    logor = requests.get(url=f"https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol}&types=logo&token=pk_718bbe8d7a404327b44b4d6bd21b79f0").json()
    logoidx = logor[f"{symbol}"]
    logologo = logoidx['logo']
    logourl = logologo['url']
    embed = disnake.Embed(title=f"The All-In-One-Command for {ticker}", description="```py\nThis command holds datapoints for several categories. Interact with the buttons and dropdown menus below to see the results.```", color=disnake.Colour.dark_gold())
    #embed.set_image(url=f"{logourl}")
    embed2 = disnake.Embed(title=f"The All-In-One-Command for {ticker} | Page 2", description="```py\nThis is page two of the all in one command. View more data below.```", color=disnake.Colour.fuchsia())

    view = disnake.ui.View()
    view2 = disnake.ui.View()
    view.add_item(PressRelease(ticker=ticker))
    view.add_item(ShortInterest())
    switch1 = disnake.ui.Button(style=disnake.ButtonStyle.blurple)
    switch1.callback = lambda interaction: interaction.response.edit_message(view=view2, embed = embed2)
    view.add_item(switch1)
    await interaction.edit_original_message(view=view, embed=embed)
@bot.event
async def on_slash_command_error(ctx, error):
    """ERRORS"""
    if isinstance(
        error,
        (commands.errors.CheckAnyFailure, commands.errors.BadArgument),
    ):
        await ctx.send(error)



@bot.command()
async def losers(ctx):
    await ctx.send(view=LosersView())


@bot.command()
async def gainers(ctx):
    await ctx.send(view=GainersView())




@bot.slash_command(guild_ids=[888488311927242753])
async def finscreen(inter:disnake.ApplicationCommandInteraction, pattern: str = commands.Param(name="pattern", choices=["channeldown", "channelup", "wedgeup", "wedgedown", "wedgeresistance", "wedgesupport", "tlsupport", "tlresistance", "doublebottom", "doubletop", "headandshoulders", "headandshouldersinv"]), direction: str = commands.Param(name="direction", choices=["u", "d"]), rsi: str = commands.Param(name="rsi_type", choices=["os30", "os20", "ob60", "ob70"]), new_20d_high_or_low: str = commands.Param(name="new_20d_high_or_low", choices=["nh", "nl"])):
    """🌟Use the FinViz screener and customize your options."""
    url = f"https://finviz.com/screener.ashx?v=111&f=ta_gap_{direction},ta_highlow20d_{new_20d_high_or_low},ta_pattern_{pattern},ta_rsi_{rsi}&ft=3&ar=180"
    embed = disnake.Embed(title=f"Gaps {direction} with {pattern} with the rsi at {rsi} with a 20-day {new_20d_high_or_low} \n\n (NH = NEW HIGH) \n\n (NL = NEW LOW)", color=disnake.Colour.random(), url=f"{url}")
    embed.set_footer(text="Real time Data Provided by Nasdaq Datalink - Implemented by FUDSTOP Trading")

    await inter.response.send_message(embed=embed, ephemeral=True)
     
@bot.slash_command()
async def everything(inter:disnake.AppCmdInter, ticker:str=commands.Param(autocomplete=ticker_autocomp)):
    """🌟Does NOT work on ETFs and MUST USE CAPS!!!`"""
    await inter.response.defer(with_message=True)
    ids = ticker_list[ticker.upper()]
    wbb = webull.webull()
    wbfin = wbb.get_financials(stock=f"{ticker}")
    remind = wbfin['remind']
    proj = remind['projEps']#good | proj eps
    simple = wbfin['simpleStatement']
    quote= requests.get(url=f"https://quotes-gw.webullfintech.com/api/bgw/quote/realtime?ids={ids}&includeSecu=1&delay=0&more=1")
    quoted = quote.json() or None
    estimateearningsdate=quoted[0]["estimateEarningsDate"]#quote
    earningscrush = requests.get(url=f"https://data.nasdaq.com/api/v3/datasets/QOR/{ticker}/data.json?api_key={nasdaq}")
    earningscrushd = earningscrush.json() or None
    analyst = requests.get(url=f"https://quoteapi.webullfintech.com/api/securities/stock/{ids}/recommendation").json()
    rating = requests.get(url=f"https://securitiesapi.webullfintech.com/api/securities/ticker/v5/analysis/{ids}")#performance
    ratingd = rating.json()#performance
    ratingtotal = ratingd['rating']#performance
    ratingtotals = ratingtotal['ratingAnalysisTotals']#performance
    ratinganalysis = ratingtotal['ratingAnalysis']#performance
    dataset = earningscrushd['dataset_data']
    data = dataset['data']
    ervalues = data[0]
    ercrush = ervalues[1] * 100
    erconv = round(100 - ercrush, ndigits=2)
    percentilereq = requests.get(url=f"https://data.nasdaq.com/api/v3/datasets/QOR/{ticker}/data.json?api_key={nasdaq}")#ivpercentile
    percentiledat = percentilereq.json()
    percentiledata = percentiledat['dataset_data']
    percentile = percentiledata['data']
    values = percentile[0]
    ivper30 = round(values[8] * 100, ndigits=2)#ivpercentile
    ivper60 = round(values[11]* 100, ndigits=2)#ivpercentile
    ivper90 = round(values[14]* 100, ndigits=2)#ivpercentile
    ivper360 = round(values[17]* 100, ndigits=2)#ivpercentile
    ivperavg = round((ivper30 + ivper60 + ivper90 + ivper360) / 4, ndigits=2)#ivpercentile
    rivperavg= round(number=ivperavg, ndigits=2)#ivpercentile
    latestearningsdate=quoted[0]["latestEarningsDate"]#quote
    fiftytwowkhigh=quoted[0]["fiftyTwoWkHigh"]#quote
    fiftytwowklow=quoted[0]["fiftyTwoWkLow"]#quote
    avgvol10= quoted[0]["avgVol10D"]#quote
    high=quoted[0]["high"]#quote
    low=quoted[0]["low"]#quote
    opening=quoted[0]["open"]#quote
    close=quoted[0]["close"]#quote
    float10 = float(avgvol10)#quote
    avg10 = round(float10*0.000001, ndigits=2)#quote
    avg3m=quoted[0]["avgVol3M"]#quote
    float3m = float(avg3m)#quote
    avg3mo = round(float3m*0.000001, ndigits=2)#quote
    analysis = wbfin['analysis']
    industry = analysis['industryName']#good
    #total = analysis['totalCount']# of analysts | good
    datas = analysis['datas']
    eps = datas[0]
    epsname = eps['name']#good
    epsval = eps['value']#good
    epsrank = eps['rank']#good


    bvps = datas[1]
    bvpsname = bvps['name']#good
    bvpsval = bvps['value']#good
    bvpsrank = bvps['rank']#good

    dps = datas[2]
    dpsname = dps['name'] #good
    dpsval = dps['label']#good
    dpsrank = dps['rank']#good

    pe = datas[3]
    pename = pe['name']#good
    peval = pe['value']#good
    perank = pe['rank']#good

    pb = datas[4]
    pbname = pb['name']#good
    pbval = pb['value']#good
    pbrank = pb['rank']#good

    roe = datas[5]
    roename = roe['name']#good
    roeval = roe['label']#good %
    roerank = roe['rank']#good

    debt_to_asset = datas[7]
    debt_to_assetname = debt_to_asset['name']#good
    debt_to_assetval = debt_to_asset['value']#good %
    debt_to_assetrank = debt_to_asset['rank']#good
    incomestatement = simple[0]
    incomestatementtitle = incomestatement['title']
    incomestatementlist = incomestatement['list']#this
    #incomerevenueq3 = round(float(incomestatementlist[0]['revenue'])*0.000000001,ndigits=2)#good
    #incomerevenueq4 = round(float(incomestatementlist[1]['revenue'])*0.000000001,ndigits=2)#good
    #incomerevenueq1 = round(float(incomestatementlist[2]['revenue'])*0.000000001,ndigits=2)#good
    incomerevenueq2 = round(float(incomestatementlist[3]['revenue'])*0.000000001,ndigits=2)#good
    #netincomeq3 = round(float(incomestatementlist[0]['netIncomeAfterTax'])*0.000001,ndigits=2)#good
    #netincomeq4 = round(float(incomestatementlist[1]['netIncomeAfterTax'])*0.000001,ndigits=2)#good
    #netincomeq1 = round(float(incomestatementlist[2]['netIncomeAfterTax'])*0.000001,ndigits=2)#good
    netincomeq2 = round(float(incomestatementlist[3]['netIncomeAfterTax'])*0.000001,ndigits=2)#good
    #netincomerateq3 = round(float(incomestatementlist[0]['netIncomeRate']),ndigits=2)#good
    #netincomerateq4 = round(float(incomestatementlist[1]['netIncomeRate']),ndigits=2)#good
    #netincomerateq1 = round(float(incomestatementlist[2]['netIncomeRate']),ndigits=2)#good
    #netincomerateq2 = round(float(incomestatementlist[3]['netIncomeRate']),ndigits=2)#good
    #incomeq3 = incomestatementlist[0]['reportEndDate']#good
    #incomeq4 = incomestatementlist[1]['reportEndDate']#good
    #incomeq1 = incomestatementlist[2]['reportEndDate']#good
    #incomeq2 = incomestatementlist[3]['reportEndDate']#good



    balancesheet = simple[1]
    balancetitle = balancesheet['title']
    balancelist = balancesheet['list']
    #balanceassetsq3 = round(float(balancelist[0]['totalAsset'])*0.000000001,ndigits=2)
    #balanceassetsq4 = round(float(balancelist[1]['totalAsset'])*0.000000001,ndigits=2)
    #balanceassetsq1 = round(float(balancelist[2]['totalAsset'])*0.000000001,ndigits=2)
    balanceassetsq2 = round(float(balancelist[3]['totalAsset'])*0.000000001,ndigits=2)
    #balanceliabilityq3 = balancelist[0]['liabilityRate']
    #balanceliabilityq4 = balancelist[1]['liabilityRate']
    #balanceliabilityq1 = balancelist[2]['liabilityRate']
    balanceliabilityq2 = balancelist[3]['liabilityRate']
    #totalliabilityq3 = round(float(balancelist[0]['totalLiability'])*0.000000001,ndigits=2)
    #totalliabilityq4 = round(float(balancelist[1]['totalLiability'])*0.000000001,ndigits=2)
    #totalliabilityq1 = round(float(balancelist[2]['totalLiability'])*0.000000001,ndigits=2)
    #totalliabilityq2 = round(float(balancelist[3]['totalLiability'])*0.000000001,ndigits=2)
    #balanceq3 = balancelist[0]['reportEndDate']
    #balanceq4 = balancelist[1]['reportEndDate']
    #balanceq1 = balancelist[2]['reportEndDate']
    #balanceq2 = balancelist[3]['reportEndDate']


    cashflow = simple[2]
    cashflowtitle = cashflow['title']
    cashflowlist = cashflow['list']
   # cashinvestmentbriefq3 = round(float(cashflowlist[0]['netInvestmentCashBrief'])*0.000000001,ndigits=2)
    #cashinvestmentbriefq4 = round(float(cashflowlist[1]['netInvestmentCashBrief'])*0.000000001,ndigits=2)
    #cashinvestmentbriefq2 = round(float(cashflowlist[2]['netInvestmentCashBrief'])*0.000000001,ndigits=2)
    #cashinvestmentbriefq1 = round(float(cashflowlist[3]['netInvestmentCashBrief'])*0.000000001,ndigits=2)
    #cashfinancingbriefq3 = round(float(cashflowlist[0]['netFinancingCashBrief'])*0.000000001,ndigits=2)
    #cashfinancingbriefq4 = round(float(cashflowlist[1]['netFinancingCashBrief'])*0.000000001,ndigits=2)
    cashfinancingbriefq2 = round(float(cashflowlist[2]['netFinancingCashBrief'])*0.000000001,ndigits=2)
    #cashfinancingbriefq1 = round(float(cashflowlist[3]['netFinancingCashBrief'])*0.000000001,ndigits=2)
    #cashoperatingbriefq3 = round(float(cashflowlist[0]['netOperatingCashBrief'])*0.000000001,ndigits=2)
    #cashoperatingbriefq4 = round(float(cashflowlist[1]['netOperatingCashBrief'])*0.000000001,ndigits=2)
    cashoperatingbriefq2 = round(float(cashflowlist[2]['netOperatingCashBrief'])*0.000000001,ndigits=2)
    #cashoperatingbriefq1 = round(float(cashflowlist[3]['netOperatingCashBrief'])*0.000000001,ndigits=2)
    #cashq3 = balancelist[0]['reportEndDate']
    #cashq4 = balancelist[1]['reportEndDate']
    #cashq1 = balancelist[2]['reportEndDate']
    #cashq2 = balancelist[3]['reportEndDate']
    select = disnake.ui.Select(
        placeholder=f"💸 🇫 🇮 🇳 🇦 🇳 🇨 🇮 🇦 🇱 🇸 💸 for {ticker}",
        min_values=1,
        max_values=1,
        custom_id ="financials",
        
        options= [
        disnake.SelectOption(label=f"Next earnings: {estimateearningsdate}🗓️", description=f"Projected EPS: {proj} | Industry: {industry}"),
        disnake.SelectOption(label=f"Earnings Per Share ({epsname})", description=f"Value: {epsval} | Industry Rank: {epsrank}"),
        disnake.SelectOption(label=f"Book Value Per Share ({bvpsname})", description=f"Value: {bvpsval} | Industry Rank: {bvpsrank}"),
        disnake.SelectOption(label=f"{dpsname}", description=f"Value: {dpsval} | Industry Rank: {dpsrank}"),
        disnake.SelectOption(label=f"Price to Earnings: {pename}", description=f"Value: {peval} | Industry Rank: {perank}"),
        disnake.SelectOption(label=f"Price to Book: {pbname}", description=f"Value: {pbval} | Industry Rank: {pbrank}"),
        disnake.SelectOption(label=f"Return on Equity: {roename}", description=f"Value: {roeval}% | Industry Rank: {roerank}"),
        disnake.SelectOption(label=f"Debt to Asset: {debt_to_assetname}", description=f"Value: {debt_to_assetval}% | Industry Rank: {debt_to_assetrank} billion."),
        disnake.SelectOption(label=f"{incomestatementtitle} Q2 2022🗓️", description=f"Revenue: {incomerevenueq2} billion | Net After Tax: {netincomeq2} billion."),
        disnake.SelectOption(label=f"{balancetitle} Q2 2022🗓️", description=f"Assets: {balanceassetsq2} billion | Total Liability: {balanceliabilityq2} billion."),
        disnake.SelectOption(label=f"{cashflowtitle} Q2 2022🗓️", description=f"Financing: {cashfinancingbriefq2} billion | Operating: {cashoperatingbriefq2} billion."),
        ])
    view = disnake.ui.View()
    view.add_item(select)
    danal = wbb.get_analysis(stock=f"{ticker}")
    rating = danal['rating']
    spread = rating['ratingSpread']
    targetprice = danal['targetPrice']
    underr = spread['underPerform']
    currentr = targetprice['current']
    meanr = targetprice['mean']

    analysistotals = str(rating['ratingAnalysisTotals'])#42


    analysis = rating['ratingAnalysis']
    spread = rating['ratingSpread']
    underr = spread['underPerform']
    buyr = spread['buy']
    sellr = spread['sell']
    strongr = spread['strongBuy']
    #holdr = spread['hold']

    target = danal['targetPrice']
    lowr = target['low']
    highr = target['high']
    currentr = target['current']
    meanr = target['mean']
    select2 = disnake.ui.Select(
        placeholder = f"🔎 🇦 🇳 🇦 🇱 🇾 🇸 🇮 🇸  for {ticker}🔍",
        min_values=1,
        max_values=1,
        custom_id ="analysis",
        options= [     
            disnake.SelectOption(label="🕵️ Total Analysts:", description=f"{analysistotals}"),
            disnake.SelectOption(label="🦾 Strong Buy", description=f"{strongr}"),
            disnake.SelectOption(label="🟩 Buy:", description=f"{buyr}"),
            disnake.SelectOption(label="🟧 Underperform:", description=f"{underr}"),
            disnake.SelectOption(label="🟥 Sell:", description=f"{sellr}"),
            disnake.SelectOption(label="🎯 Avg Target:", description=f"{meanr}"),
            disnake.SelectOption(label="🎯 Current:", description=f"{currentr}"),
            disnake.SelectOption(label="🎯 High Target:", description=f"{highr}"),
            disnake.SelectOption(label="🎯 Low Target:", description=f"{lowr}")])
    view.add_item(select2)


    r2r = requests.get(url=f"https://quotes-gw.webullfintech.com/api/stock/capitalflow/ticker?tickerId={ids}&showHis=true")
    d2r = r2r.json()
    latest = d2r['latest']
    #dated = latest['date']
    item = latest['item']
    superlgin=round(float(item["superLargeInflow"]*0.000001), ndigits=2)
    superlgout=round(float(item["superLargeOutflow"]*0.000001), ndigits=2)
    #superlgnet=round(float(item["superLargeNetFlow"]*0.000001), ndigits=2)
    lgin = round(float(item["largeInflow"]*0.000001), ndigits=2)
    lgout =round(float(item["largeOutflow"]*0.000001), ndigits=2)
    #lgnet = round(float(item["largeNetFlow"]*0.000001), ndigits=2)
    newlgin =round(float(item["newLargeInflow"]*0.000001), ndigits=2)
    newlgout = round(float(item["newLargeOutflow"]*0.000001), ndigits=2)
    #newlgnet = round(float(item["newLargeNetFlow"]*0.000001), ndigits=2)
    medin = round(float(item["mediumInflow"]*0.000001), ndigits=2)
    medout = round(float(item["mediumOutflow"]*0.000001), ndigits=2)
    #mednet = round(float(item["mediumNetFlow"]*0.000001), ndigits=2)
    smallin = round(float(item["smallInflow"]*0.000001), ndigits=2)
    smallout = round(float(item["smallOutflow"]*0.000001), ndigits=2)
    #smallnet = round(float(item["smallNetFlow"]*0.000001), ndigits=2)
    majorin = round(float(item["majorInflow"]*0.000001), ndigits=2)
    majorout = round(float(item["majorOutflow"]*0.000001), ndigits=2)
    majornet = round(float(item["majorNetFlow"]*0.000001), ndigits=2)
    retailin = round(float(item["retailInflow"]*0.000001), ndigits=2)
    retailout = round(float(item["retailOutflow"]*0.000001), ndigits=2)
    #retailinratio =round(float(item["retailInflowRatio"]*100), ndigits=2)
    #retailoutratio = round(float(item["retailOutflowRatio"]*100), ndigits=2)
    newlginratio =round(float(item["newLargeInflowRatio"]*100), ndigits=2)
    newlgoutratio = round(float(item["newLargeOutflowRatio"]*100), ndigits=2)
    #mediuminratio =round(float(item["mediumInflowRatio"]*100),ndigits=2)
    #mediumoutratio = round(float(item["mediumOutflowRatio"]*100),ndigits=2)
    #smallinratio =round(float(item["smallInflowRatio"]*100),ndigits=2)
    #smalloutratio = round(float(item["smallOutflowRatio"]*100),ndigits=2)
    #majorinratio =round(float(item["majorInflowRatio"]*100),ndigits=2)
    #majoroutratio = round(float(item["majorOutflowRatio"]*100),ndigits=2)
    orderflow = requests.get(f"https://quotes-gw.webullfintech.com/api/stock/capitalflow/stat?count=10&tickerId={ids}&type=0")
    orderflowd = orderflow.json()
    dateset = orderflowd['dates']
    datelist = [i['date'] for i in dateset]

    date1 = datelist[0]
    sellvol1 = round(float(orderflowd['sellVolume']) * 0.000001, ndigits=2)
    nvol1 = round(float(orderflowd['nVolume']) * 0.000001, ndigits=2)
    buyvol1 = round(float(orderflowd['buyVolume']) * 0.000001, ndigits=2)
    #avg1 = orderflowd['avePrice']
    #max1 = round(float(orderflowd['maxT']) * 0.000001, ndigits=2)
    select4 = disnake.ui.Select( placeholder=f"🇴 🇷 🇩 🇪 🇷 🔥  🇫 🇱 🇴 🇼 for {ticker}", min_values=1, max_values=1, custom_id=f"flowselect",
    options= [
        disnake.SelectOption( label=f"New Ratio % IN: {newlginratio}%", description=f"New Ratio % OUT: {newlgoutratio}%", ),
        disnake.SelectOption( label="Today's Sell Flow", description=f"🔴{sellvol1} million.", ),
        disnake.SelectOption( label="Today's Buy Flow", description=f"🟢{buyvol1} million.", ),
        disnake.SelectOption( label="Today's Neutral Flow", description=f"⚫{nvol1} million.", ),
        disnake.SelectOption( label="Super Large Flow IN:", description=f"{superlgin} million."),
        disnake.SelectOption( label="Super Large Flow OUT:", description=f"{superlgout} million.", ),
        disnake.SelectOption( label="Major Flow IN:", description=f"{majorout} million."),
        disnake.SelectOption( label="Major Flow OUT:", description=f"{majorin} million.", ),
        disnake.SelectOption( label="Large Flow IN:", description=f"{lgin} million."),
        disnake.SelectOption( label="Large Flow OUT:", description=f"{lgout} million.", ),
        disnake.SelectOption( label="Medium Flow IN:", description=f"{medin} million."),
        disnake.SelectOption( label="Medium Flow OUT:", description=f"{medout} million.", ),
        disnake.SelectOption( label="Small Flow IN:", description=f"{smallin} million."),
        disnake.SelectOption( label="Small Flow OUT:", description=f"{smallout} million.", ),
        disnake.SelectOption( label="Retail Flow IN:", description=f"{retailin} million."),
        disnake.SelectOption( label="Retail Flow OUT:", description=f"{retailout} million.", ),
        disnake.SelectOption( label="New Flow IN:", description=f"{newlgin} million."),
        disnake.SelectOption( label="New Flow OUT:", description=f"{newlgout} million.", ),])
    view.add_item(select4)
    holdersr = requests.get(url=f"https://securitiesapi.webullfintech.com/api/securities/stock/{ids}/holdersDetail?tickerId={ids}&type=2&hasNum=0&pageSize=10")
    holdersd = holdersr.json()
    company1 = holdersd[0]
    name1 = company1['ownerName']
    date1 = company1['date']
    shares1 = company1['sharedHeld']
    ff1 = float(shares1)
    holdings1 = round(ff1*0.000001, ndigits=2)
    #change1 = company1['shareChange']
    ratio1 = company1['changeRatio']
    type1 = company1['type']
    #holdingratio1 = company1['holdingRatio']



    company2=holdersd[1]
    name2 = company2['ownerName']
    date2 = company2['date']
    shares2 = company2['sharedHeld']
    ff2 = float(shares2)
    holdings2 = round(ff2*0.000001, ndigits=2)
    #change2 = company2['shareChange']
    ratio2 = company2['changeRatio']
    type2 = company2['type']
    #holdingratio2 = company2['holdingRatio']



    company3=holdersd[2]
    name3 = company3['ownerName']
    date3 = company3['date']
    shares3 = company3['sharedHeld']
    ff3 = float(shares3)
    holdings3 = round(ff3*0.000001, ndigits=2)
    #change3 = company3['shareChange']
    ratio3 = company3['changeRatio']
    type3 = company3['type']
    #holdingratio3 = company3['holdingRatio']

    company4=holdersd[3]
    name4 = company4['ownerName']
    date4 = company4['date']
    shares4 = company4['sharedHeld']
    ff4 = float(shares4)
    holdings4 = round(ff4*0.000001, ndigits=2)
    #change4 = company4['shareChange']
    ratio4 = company4['changeRatio']
    type4 = company4['type']
    #holdingratio4 = company4['holdingRatio']

    company5=holdersd[4]
    name5 = company5['ownerName']
    date5 = company5['date']
    shares5 = company5['sharedHeld']
    ff5 = float(shares5)
    holdings5 = round(ff5*0.000001, ndigits=2)
    #change5 = company5['shareChange']
    ratio5 = company5['changeRatio']
    type5 = company5['type']
    #holdingratio5 = company5['holdingRatio']

    company6=holdersd[5]
    name6 = company6['ownerName']
    date6 = company6['date']
    shares6 = company6['sharedHeld']
    ff6 = float(shares6)
    holdings6 = round(ff6*0.000001, ndigits=2)
    #change6 = company6['shareChange']
    ratio6 = company6['changeRatio']
    type6 = company6['type']
    #holdingratio6 = company6['holdingRatio']

    company7=holdersd[6]
    name7 = company7['ownerName']
    date7 = company7['date']
    shares7 = company7['sharedHeld']
    ff7 = float(shares7)
    holdings7 = round(ff7*0.000001, ndigits=2)
    #change7 = company7['shareChange']
    ratio7 = company7['changeRatio']
    type7 = company7['type']
    #holdingratio7 = company7['holdingRatio']

    company8=holdersd[7]
    name8 = company8['ownerName']
    date8 = company8['date']
    shares8 = company8['sharedHeld']
    ff8 = float(shares8)
    holdings8 = round(ff8*0.000001, ndigits=2)
    #change8 = company8['shareChange']
    ratio8 = company8['changeRatio']
    type8 = company8['type']
    #holdingratio8 = company8['holdingRatio']

    company9=holdersd[8]
    name9 = company9['ownerName']
    date9 = company9['date']
    shares9 = company9['sharedHeld']
    f9 = float(shares9)
    holdings9 = round(f9*0.000001, ndigits=2)
    #change9 = company9['shareChange']
    ratio9 = company9['changeRatio']
    type9 = company9['type']
    #holdingratio9 = company9['holdingRatio']

    company10=holdersd[9]
    name10 = company10['ownerName']
    date10 = company10['date']
    shares10 = company10['sharedHeld']
    f10 = float(shares10)
    holdings10 = round(f10*0.000001, ndigits=2)
    #change10 = company10['shareChange']
    ratio10 = company10['changeRatio']
    type10 = company10['type']
    #holdingratio10 = company10['holdingRatio']
    view2 = disnake.ui.View()
    select5 = disnake.ui.Select( placeholder=f"🏦 🇮 🇳 🇸 🇹 🇮 🇹 🇺 🇹 🇮 🇴 🇳 🇸 🏦 holding {ticker}", min_values=1, max_values=1, custom_id=f"instselect",
    options= [
        disnake.SelectOption( label=f"1️⃣ {name1} holding {holdings1} million.",description=f"Filed: {date1} Type: {type1} Change: {ratio1}", ),
        disnake.SelectOption( label=f"2️⃣ {name2} holding {holdings2} million.",description=f"Filed: {date2} Type: {type2} Change: {ratio2}", ),
        disnake.SelectOption( label=f"3️⃣ {name3} holding {holdings3} million.",description=f"Filed: {date3} Type: {type3} Change: {ratio3}", ),
        disnake.SelectOption( label=f"4️⃣ {name4} holding {holdings4} million.",description=f"Filed: {date4} Type: {type4} Change: {ratio4}", ),
        disnake.SelectOption( label=f"5️⃣ {name5} holding {holdings5} million.",description=f"Filed: {date5} Type: {type5} Change: {ratio5}", ),
        disnake.SelectOption( label=f"6️⃣ {name6} holding {holdings6} million.",description=f"Filed: {date6} Type: {type6} Change: {ratio6}", ),
        disnake.SelectOption( label=f"7️⃣ {name7} holding {holdings7} million.",description=f"Filed: {date7} Type: {type7} Change: {ratio7}", ),
        disnake.SelectOption( label=f"8️⃣ {name8} holding {holdings8} million.",description=f"Filed: {date8} Type: {type8} Change: {ratio8}", ),
        disnake.SelectOption( label=f"9️⃣ {name9} holding {holdings9} million.",description=f"Filed: {date9} Type: {type9} Change: {ratio9}", ),
        disnake.SelectOption( label=f"🔟 {name10} holding {holdings10} million.",description=f"Filed: {date10} Type: {type10} Change: {ratio10}", ),])
            
    view2.add_item(select5)
    select6 = disnake.ui.Select( placeholder=f"🏹 🇩  🇦  🇹  🇦 for {ticker} 🏹", min_values=1, max_values=1, custom_id=f"priceselect",
    options= [
        disnake.SelectOption( label="Todays Price Levels:", description=f"Open: {opening} Current: {close} Low: {low} High: {high}"),
        disnake.SelectOption( label="Latest Earnings",description=f"🗓️ {latestearningsdate}" ),
        disnake.SelectOption( label="52 Week High:", description=f"🎯 {fiftytwowkhigh}"),
        disnake.SelectOption( label="52 Week Low:", description=f"🎯 {fiftytwowklow}", ),
        disnake.SelectOption( label="Expected Earnings Crush:", description=f"🩸 {erconv}% of {ticker}'s IV is expected to crush following next earnings.", ),
        disnake.SelectOption( label="% calculations of IV that have been lower than current:", description=f"{rivperavg}%", ),
        disnake.SelectOption( label="Average Volume, 10 Days:", description=f"{avg10} million.", ),
        disnake.SelectOption( label="Average Volume, 3 Months:", description=f"{avg3mo} million.", ),
        disnake.SelectOption( label="Latest Rating:", description=f"{ratinganalysis} with {ratingtotals} analysts.", ),])

    
    view.add_item(select6)

    prelease = wbb.get_press_releases(stock=f"{ticker}")
    prannouncements = prelease['announcements']
    filingtitle1 = prannouncements[0]['title']
    filingpubdate1 = prannouncements[0]['publishDate']
    filinghtmlurl1 = prannouncements[0]['htmlUrl']
    filingtypename1 = prannouncements[0]['typeName']
    filingtitle2 = prannouncements[1]['title']
    filingpubdate2 = prannouncements[1]['publishDate']
    filinghtmlurl2 = prannouncements[1]['htmlUrl']
    filingtypename2 = prannouncements[1]['typeName']
    filingtitle3 = prannouncements[2]['title']
    filingpubdate3 = prannouncements[2]['publishDate']
    filinghtmlurl3 = prannouncements[2]['htmlUrl']
    filingtypename3 = prannouncements[2]['typeName']
    filingtitle4 = prannouncements[3]['title']
    filingpubdate4 = prannouncements[3]['publishDate']
    filinghtmlurl4 = prannouncements[3]['htmlUrl']
    filingtypename4 = prannouncements[3]['typeName']
    filingtitle5 = prannouncements[4]['title']
    filingpubdate5 = prannouncements[4]['publishDate']
    filinghtmlurl5 = prannouncements[4]['htmlUrl']
    filingtypename5 = prannouncements[4]['typeName']
    filingtitle6 = prannouncements[5]['title']
    filingpubdate6 = prannouncements[5]['publishDate']
    filinghtmlurl6 = prannouncements[5]['htmlUrl']
    filingtypename6 = prannouncements[5]['typeName']
    filingtitle7 = prannouncements[6]['title']
    filingpubdate7 = prannouncements[6]['publishDate']
    filinghtmlurl7 = prannouncements[6]['htmlUrl']
    filingtypename7 = prannouncements[6]['typeName']
    filingtitle8 = prannouncements[7]['title']
    filingpubdate8 = prannouncements[7]['publishDate']
    filinghtmlurl8 = prannouncements[7]['htmlUrl']
    filingtypename8 = prannouncements[7]['typeName']
    filingtitle9 = prannouncements[8]['title']
    filingpubdate9 = prannouncements[8]['publishDate']
    filinghtmlurl9 = prannouncements[8]['htmlUrl']
    filingtypename9 = prannouncements[8]['typeName']
    filingtitle10 = prannouncements[9]['title']
    filingpubdate10 = prannouncements[9]['publishDate']
    filinghtmlurl10 = prannouncements[9]['htmlUrl']
    filingtypename10 = prannouncements[9]['typeName']



    select7 = disnake.ui.Select(
        placeholder ="🇫 ℹ️ 🇱 ℹ️ 🇳 🇬 🇸",
        min_values=1,
        max_values=2,
        custom_id="filifengselect",
        options=[
        disnake.SelectOption(label=f"{filingtitle1}",description=f"{filingpubdate1} | {filingtypename1}"),
        disnake.SelectOption(label=f"{filingtitle2}",description=f"{filingpubdate2} | {filingtypename2}"),
        disnake.SelectOption(label=f"{filingtitle3}",description=f"{filingpubdate3} | {filingtypename3}"),
        disnake.SelectOption(label=f"{filingtitle4}",description=f"{filingpubdate4} | {filingtypename4}"),
        disnake.SelectOption(label=f"{filingtitle5}",description=f"{filingpubdate5} | {filingtypename5}"),
        disnake.SelectOption(label=f"{filingtitle6}",description=f"{filingpubdate6} | {filingtypename6}"),
        disnake.SelectOption(label=f"{filingtitle7}",description=f"{filingpubdate7} | {filingtypename7}"),
        disnake.SelectOption(label=f"{filingtitle8}",description=f"{filingpubdate8} | {filingtypename8}"),
        disnake.SelectOption(label=f"{filingtitle9}",description=f"{filingpubdate9} | {filingtypename9}"),
        disnake.SelectOption(label=f"{filingtitle10}",description=f"{filingpubdate10} | {filingtypename10}"),])
    page1button1 = disnake.ui.Button(style=disnake.ButtonStyle.danger,label=f"52w Low: 🎯{fiftytwowklow}", row=4)
    page1button1.callback = lambda interaction: interaction.response.edit_message(view=view)
    page1button2 = disnake.ui.Button(style=disnake.ButtonStyle.success,label=f"52w High: 🎯{fiftytwowkhigh}", row=4)
    page1button2.callback = lambda interaction: interaction.response.edit_message(view=view)
    page1switch = disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="🍥", row=4)
    page1switch.callback = lambda interaction: interaction.response.edit_message(view=view2)
    page1button3 = disnake.ui.Button(style=disnake.ButtonStyle.grey,label=f"Next ER: {estimateearningsdate}🗓️", row=4)
    page1button3.callback = lambda interaction: interaction.response.edit_message(view=view)
    page1button4 = disnake.ui.Button(style=disnake.ButtonStyle.grey,label=f"Expected ER Crush: {erconv}⚔️", row=4)
    page1button4.callback = lambda interaction: interaction.response.edit_message(view=view)
    emb = disnake.Embed(title="🟢", description="```py\nFUDSTOP Bot Online```")
    #url = "https://webull.p.rapidapi.com/stock/get-cost-distribution-analysis"
    #querystring = {"tickerId":f"{ids.upper()}"}
    #headers = {
        #"X-RapidAPI-Key": "cd36127562msh09bad643a11b69cp16a83cjsnce170739c830",
       # "X-RapidAPI-Host": "webull.p.rapidapi.com"
    #}
    ##%sharesProportioned
    """ costresp = requests.get(url, headers=headers, params=querystring).json()
    costdata = costresp['data']
    costdatas = costdata[0]
    dist = costdatas[0]['distributions']
    avg = costresp[0]['avgCost']
    profitratio = round(float(costresp[0]['closeProfitRatio'])*100, ndigits=2)
    dist1 = dist[0]
    price1 = float(dist1[0])
    cost1 = float(dist1[1])
    avg1 = round(float(dist1[2])*100,ndigits=3)
    co1 = format(int(cost1),",") """

    view.add_item(page1button1)
    view.add_item(page1button2)
    view.add_item(page1switch)
    view.add_item(page1button3)
    view.add_item(page1button4)
    view2.add_item(select7)
    view2.add_item(TechDropdown2())
    view2.add_item(TechDropdown())
    await inter.edit_original_message(embed=emb,view=view)

@everything.error
async def everythingerror(inter: disnake.AppCmdInter, error):
    if isinstance(error, commands.CheckAnyFailure):
        await inter.send("```py\n Must use caps - and can't be an ETF as ETFs dont have financial data such as earnings metrics.```")    

#base_url = "https://quotes-gw.webullfintech.com/api/quote/option/quotes/queryBatch?derivativeIds="
#ids = derivatives_list[spy_contract]
#r = requests.get(url=f"{base_url} + {ids}")
#d = r.json()
#items = "\n".join(f"VOLUME\n **{i['volume']}**\n\n OPEN INTEREST\n **{i['openInterest']}**\n\n OI CHANGE\n **{i['openIntChange']}**" for i in d)
#items2 = "\n".join(f"IV:\n**{i['impVol']}**\n\n RHO\n **{i['rho']}**\n\n ACTIVE LEVEL:\n {i['activeLevel']}" for i in d)
#em = disnake.Embed(title="Spy Watcher", description="Pick a SPY contract - we will start to observe inbetween for settlement window. Expect more autism.", color=disnake.Colour.random())
#em.add_field(name="Volume, OI, and OI CHANGE", value=f"{items}")
#em.add_field(name="IV, RHO, and ACTIVE LEVELS", value=f"{items2}")
#await inter.response.send_message(embed=em)




@bot.command()
async def school(ctx):
    rsc = requests.get(url="https://u1sact.webullfinance.com/api/edu/v1/l/lesson/getCoursewareDetail?coursewareId=LIprNZ&courseId=nWV8xn")
    dsc = rsc.json()
    content = dsc['content']
    evaluate=dsc['evaluate']
    topic = dsc['topic']
    result = re.sub("<.*?>", "", content)#
    html = content
    bs = BeautifulSoup(content, 'html.parser')
    images = bs.find_all('img', {'src':re.compile('.png')})
    #image1 = images[0]['src']+'\n'
    #image2 = images[1]['src']+'\n'
    emb = disnake.Embed(title="🏫", description="```py\nWelcome to Webull School! This Application will teach you how to use Webull - as well as many different areas of the markets. This is the learning cource provided by Webull - brought to you in Discord.```", url="https://www.webull.com/", color=disnake.Colour.dark_blue())
    emb.set_image(url="https://is2-ssl.mzstatic.com/image/thumb/Purple112/v4/20/f5/a4/20f5a4dd-a8ea-c62b-8362-6cf4a0b6268d/Webull.png/230x0w.webp")
    view = disnake.ui.View()
    view.add_item(MainSelect())
    ri = disnake.ui.Button(style=disnake.ButtonStyle.green, label="Get Started!")
    ri.callback = lambda interaction: interaction.response.edit_message(embed = emb, view=MainSelectView())
    view.add_item(ri)
    await ctx.send(embed=emb, view=view)

@bot.command()
async def webullcountries(ctx):
    r = requests.get(url="https://quotes-gw.webullfintech.com/api/market/region/all")
    d = r.json()
    name = [i['name'] for i in d]
    embed = disnake.Embed(title="Webull Countries:", description=f"```py\n{name}```")
    await ctx.send(embed=embed)
@bot.command()
async def shvol(ctx):
    today = date.today()
    await ctx.send(f"https://cdn.finra.org/equity/regsho/daily/CNMSshvol{today}.txt")


""" @bot.slash_command()
async def webull_quote(interaction: disnake.ApplicationCommandInteraction):
    Pulls the ticker from this url.
    await interaction.response.defer(with_message=True)
    counter = 1
    counter = counter + 1
    r = requests.get(url="https://quotes-gw.webullfintech.com/api/bgw/quote/realtime?ids=913243250&includeSecu=1&delay=0&more=1")
    d = r.json()
    index = d[0]
    #tickerid = index['tickerId']
    #symbol = index['symbol']
    #close = index['close']
    #high = index['high']
    #low = index['low']
    opens = index['open']
    
    em = disnake.Embed(title="Webull Quote")
    await interaction.edit_original_message(embed=em) """


class Quoter(disnake.ui.View):
    def __init__(self):
        quotereq = requests.get(url="https://quotes-gw.webullfintech.com/api/bgw/quote/realtime?ids=913243250&includeSecu=1&delay=0&more=1")
        quotedat = quotereq.json()
        index = quotedat[0]
        self.tickerid = index['tickerId']
        self.symbol = index['symbol']
        self.close = index['close']
        self.high = index['high']
        self.low = index['low']
        self.opens = index['open']


@bot.slash_command()
async def food(inter):
    pass

@bot.slash_command()
async def recipe(interaction:disnake.AppCmdInter):
    """🥑Generates a random meal with instructions & ingredients."""
    feederr = requests.get(url="https://api.spoonacular.com/recipes/random?apiKey=2843112765cd43bab9166fce4d3843e4")
    feededd = feederr.json()
    recipes = feededd['recipes']
    one = recipes[0]
    vegetarian = one['vegetarian']
    vegan = one['vegan']
    glutenfree = one['glutenFree']
    dairyfree = one['dairyFree']
    health = one['healthScore']
    title= one['title']
    servings = one['servings']
    #source = one['sourceUrl']
    image = one['image']
    summary = one['summary']
    instructions = one['instructions']
    extended = one['extendedIngredients']
    aisle = [i['aisle'] for i in extended]
    #const = [i['consistency'] for i in extended]
    #name = [i['name'] for i in extended]
    #amt = [i['amount'] for i in extended]
    #unit = [i['unit'] for i in extended]
    items2 = "\n".join(f"{i['name']} {i['amount']}{i['unit']}" for i in extended)
    #items = "\n\n".join(f"Name: {i['name']}\nAisle: {i['aisle']}\nConsistency: {i['consistency']}\nAmount: {i['amount']}{i['unit']}\nOriginal: {i['original']}" for i in extended)
    emb = disnake.Embed(title=f"{title}", description=f"```py\n{summary}```", url=f"{source}", color=disnake.Colour.random())
    emb.add_field(name="Vegetarian / Vegan?", value=f"```py\nVegetarian: {vegetarian} | Vegan: {vegan}```")
    emb.add_field(name="Gluten / Dairy Free?", value=f"```py\nGluten: {glutenfree} | Dairy: {dairyfree}```")
    emb.add_field(name="Servings", value=f"```py\n{servings}```")
    emb.add_field(name="Health Score", value=f"```py\n{health}```", inline=False)
    emb.add_field(name="Instructions", value=f"```py\n{instructions}```", inline=False)
    emb.add_field(name="Shopping Aisles:", value=f"```py\n{aisle}```")
    emb.add_field(name="Name & Amount", value=f"```py\n{items2}```")
    emb.set_image(url=f"{image}")
    await interaction.send(embed=emb)




@bot.slash_command()
async def rules(interaction:disnake.ApplicationCommandInteraction):
    """📏Got bekked forgot what goes here"""
    await interaction.response.defer(with_message=True)
    view = disnake.ui.View()
    view.add_item(RulesSelect())
    view2 = disnake.ui.View()
    b = disnake.ui.Button(style=disnake.ButtonStyle.blurple, label="⏭️")
    b.callback = lambda interaction: interaction.response.edit_message(view=view2)
    view2.add_item(RulesSelect())
    view2.add_item(RulesSelect2())
    view.add_item(b)
    await interaction.edit_original_message(view=view)



@bot.slash_command()
async def crypto(inter):
    """PARENT"""


@crypto.sub_command()
async def coin(inter:disnake.AppCmdInter):
    """🪙Simultaneously Stream 20 Cryptocoins in Real-Time"""
    await inter.response.defer(with_message=True)
    counter = 0
    while True:
        counter = counter + 1
        cryptor = requests.get(url="https://quotes-gw.webullfintech.com/api/bgw/crypto/list")
        cryptod = cryptor.json()
        cryptoticker1 = cryptod[0]
        cryptoname1 = cryptoticker1['disSymbol']
        cryptoprice1 = round(float(cryptoticker1['close']),ndigits=2)
        cryptoratio1 = round(float(cryptoticker1['changeRatio'])*100,ndigits=2)
        cryptoticker2 = cryptod[1]
        cryptoname2 = cryptoticker2['disSymbol']
        cryptoprice2 = round(float(cryptoticker2['close']),ndigits=2)
        cryptoratio2 = round(float(cryptoticker2['changeRatio'])*100,ndigits=2)
        cryptoticker3 = cryptod[2]
        cryptoname3 = cryptoticker3['disSymbol']
        cryptoprice3 = round(float(cryptoticker3['close']),ndigits=2)
        cryptoratio3 = round(float(cryptoticker3['changeRatio'])*100,ndigits=2)
        cryptoticker4 = cryptod[3]
        cryptoname4 = cryptoticker4['disSymbol']
        cryptoprice4= round(float(cryptoticker4['close']),ndigits=2)
        cryptoratio4 = round(float(cryptoticker4['changeRatio'])*100,ndigits=2)
        cryptoticker5 = cryptod[4]
        cryptoname5 = cryptoticker5['disSymbol']
        cryptoprice5 = round(float(cryptoticker5['close']),ndigits=2)
        cryptoratio5 = round(float(cryptoticker5['changeRatio'])*100,ndigits=2)
        cryptoticker6 = cryptod[5]
        cryptoname6 = cryptoticker6['disSymbol']
        cryptoprice6 = round(float(cryptoticker6['close']),ndigits=2)
        cryptoratio6 = round(float(cryptoticker6['changeRatio'])*100,ndigits=2)
        cryptoticker7 = cryptod[6]
        cryptoname7 = cryptoticker7['disSymbol']
        cryptoprice7 = round(float(cryptoticker7['close']),ndigits=2)
        cryptoratio7 = round(float(cryptoticker7['changeRatio'])*100,ndigits=2)
        cryptoticker8 = cryptod[7]
        cryptoname8 = cryptoticker8['disSymbol']
        cryptoprice8 = round(float(cryptoticker8['close']),ndigits=2)
        cryptoratio8 = round(float(cryptoticker8['changeRatio'])*100,ndigits=2)
        cryptoticker9 = cryptod[8]
        cryptoname9 = cryptoticker9['disSymbol']
        cryptoprice9 = round(float(cryptoticker9['close']),ndigits=2)
        cryptoratio9 = round(float(cryptoticker9['changeRatio'])*100,ndigits=2)
        cryptoticker10 = cryptod[9]
        cryptoname10 = cryptoticker10['disSymbol']
        cryptoprice10 = round(float(cryptoticker10['close']),ndigits=2)
        cryptoratio10 = round(float(cryptoticker10['changeRatio'])*100,ndigits=2)
        cryptoticker11 = cryptod[10]
        cryptoname11 = cryptoticker11['disSymbol']
        cryptoprice11 = round(float(cryptoticker11['close']),ndigits=2)
        cryptoratio11 = round(float(cryptoticker11['changeRatio'])*100,ndigits=2)
        cryptoticker12 = cryptod[11]
        cryptoname12 = cryptoticker12['disSymbol']
        cryptoprice12 = round(float(cryptoticker12['close']),ndigits=2)
        cryptoratio12 = round(float(cryptoticker12['changeRatio'])*100,ndigits=2)
        cryptoticker13 = cryptod[12]
        cryptoname13 = cryptoticker13['disSymbol']
        cryptoprice13 = round(float(cryptoticker13['close']),ndigits=2)
        cryptoratio13 = round(float(cryptoticker13['changeRatio'])*100,ndigits=2)
        cryptoticker14 = cryptod[13]
        cryptoname14 = cryptoticker14['disSymbol']
        cryptoprice14 = round(float(cryptoticker14['close']),ndigits=2)
        cryptoratio14 = round(float(cryptoticker14['changeRatio'])*100,ndigits=2)
        
        cryptoticker15 = cryptod[14]
        cryptoname15 = cryptoticker15['disSymbol']
        cryptoprice15 = round(float(cryptoticker15['close']),ndigits=2)
        cryptoratio15 = round(float(cryptoticker15['changeRatio'])*100,ndigits=2)

        cryptoticker16 = cryptod[15]
        cryptoname16 = cryptoticker16['disSymbol']
        cryptoprice16 = round(float(cryptoticker16['close']),ndigits=2)
        cryptoratio16 = round(float(cryptoticker15['changeRatio'])*100,ndigits=2)

        cryptoticker17 = cryptod[16]
        cryptoname17 = cryptoticker17['disSymbol']
        cryptoprice17 = round(float(cryptoticker17['close']),ndigits=2)
        cryptoratio17 = round(float(cryptoticker15['changeRatio'])*100,ndigits=2)

        cryptoticker18 = cryptod[17]
        cryptoname18 = cryptoticker18['disSymbol']
        cryptoprice18 = round(float(cryptoticker18['close']),ndigits=2)
        cryptoratio18 = round(float(cryptoticker15['changeRatio'])*100,ndigits=2)

        cryptoticker19 = cryptod[18]
        cryptoname19 = cryptoticker19['disSymbol']
        cryptoprice19 = round(float(cryptoticker19['close']),ndigits=2)
        cryptoratio19 = round(float(cryptoticker15['changeRatio'])*100,ndigits=2)

        cryptoticker20 = cryptod[19]
        cryptoname20 = cryptoticker20['disSymbol']
        cryptoprice20 = round(float(cryptoticker20['close']),ndigits=2)
        cryptoratio20 = round(float(cryptoticker15['changeRatio'])*100,ndigits=2)


        cryptoticker21 = cryptod[20]
        cryptoname21 = cryptoticker21['disSymbol']
        cryptoprice21 = round(float(cryptoticker21['close']),ndigits=2)
        cryptoratio21 = round(float(cryptoticker15['changeRatio'])*100,ndigits=2)

        em = disnake.Embed(title="Crypto Stream", description="```py\n Real Time Crypto```", color=disnake.Colour.random())
        if cryptoratio1 >= 0:
            em.add_field(name=f"{cryptoname1}",value=f"```py\n🟢${cryptoprice1} {cryptoratio1}%```",inline=True)
        if cryptoratio1 <= 0:
            em.remove_field(index=1)
            em.add_field(name=f"{cryptoname1}",value=f"```py\n🔴${cryptoprice1} {cryptoratio1}%```",inline=True)
        
        if cryptoratio2 >= 0:
            em.add_field(name=f"{cryptoname2}",value=f"```py\n🟢${cryptoprice2} {cryptoratio2}%```",inline=True)
        if cryptoratio2 <=0:
            em.remove_field(index=2)
            em.add_field(name=f"{cryptoname2}",value=f"```py\n🔴${cryptoprice2} {cryptoratio2}%```",inline=True)
        
        if cryptoratio3 >= 0:
            em.add_field(name=f"{cryptoname3}",value=f"```py\n🟢${cryptoprice3} {cryptoratio3}%```",inline=True)
        if cryptoratio3 <=0:
            em.remove_field(index=3)
            em.add_field(name=f"{cryptoname3}",value=f"```py\n🔴${cryptoprice3} {cryptoratio3}%```",inline=True)

        if cryptoratio4 >= 0:
            em.add_field(name=f"{cryptoname4}",value=f"```py\n🟢${cryptoprice4} {cryptoratio4}%```",inline=True)
        if cryptoratio4 <=0:
            em.remove_field(index=4)
            em.add_field(name=f"{cryptoname4}",value=f"```py\n🔴${cryptoprice4} {cryptoratio4}%```",inline=True)

        if cryptoratio5 >= 0:
            em.add_field(name=f"{cryptoname5}",value=f"```py\n🟢${cryptoprice5} {cryptoratio5}%```",inline=True)
        if cryptoratio5 <=0:
            em.remove_field(index=5)
            em.add_field(name=f"{cryptoname5}",value=f"```py\n🔴${cryptoprice5} {cryptoratio5}%```",inline=True)

        if cryptoratio6 >= 0:
            em.add_field(name=f"{cryptoname6}",value=f"```py\n🟢${cryptoprice6} {cryptoratio6}%```",inline=True)
        if cryptoratio6 <=0:
            em.remove_field(index=6)
            em.add_field(name=f"{cryptoname6}",value=f"```py\n🔴${cryptoprice6} {cryptoratio6}%```",inline=True)

        if cryptoratio7 >= 0:
            em.add_field(name=f"{cryptoname7}",value=f"```py\n🟢${cryptoprice7} {cryptoratio7}%```",inline=True)
        if cryptoratio7 <=0:
            em.remove_field(index=7)
            em.add_field(name=f"{cryptoname7}",value=f"```py\n🔴${cryptoprice7} {cryptoratio7}%```",inline=True)

        if cryptoratio8 >= 0:
            em.add_field(name=f"{cryptoname8}",value=f"```py\n🟢${cryptoprice8} {cryptoratio8}%```",inline=True)
        if cryptoratio8 <=0:
            em.remove_field(index=8)
            em.add_field(name=f"{cryptoname8}",value=f"```py\n🔴${cryptoprice8} {cryptoratio8}%```",inline=True)

        if cryptoratio9 >= 0:
            em.add_field(name=f"{cryptoname9}",value=f"```py\n🟢${cryptoprice9} {cryptoratio9}%```",inline=True)
        if cryptoratio9 <=0:
            em.remove_field(index=9)
            em.add_field(name=f"{cryptoname9}",value=f"```py\n🔴${cryptoprice9} {cryptoratio9}%```",inline=True)

        if cryptoratio10 >= 0:
            em.add_field(name=f"{cryptoname10}",value=f"```py\n🟢${cryptoprice10} {cryptoratio10}%```",inline=True)
        if cryptoratio10 <=0:
            em.remove_field(index=10)
            em.add_field(name=f"{cryptoname10}",value=f"```py\n🔴${cryptoprice10} {cryptoratio10}%```",inline=True)

        if cryptoratio11 >= 0:
            em.add_field(name=f"{cryptoname11}",value=f"```py\n🟢${cryptoprice11} {cryptoratio11}%```",inline=True)
        if cryptoratio11 <=0:
            em.remove_field(index=11)
            em.add_field(name=f"{cryptoname11}",value=f"```py\n🔴${cryptoprice11} {cryptoratio11}%```",inline=True)

        if cryptoratio12 >= 0:
            em.add_field(name=f"{cryptoname12}",value=f"```py\n🟢${cryptoprice12} {cryptoratio12}%```",inline=True)
        if cryptoratio12 <=0:
            em.remove_field(index=12)
            em.add_field(name=f"{cryptoname12}",value=f"```py\n🔴${cryptoprice12} {cryptoratio12}%```",inline=True)


        if cryptoratio13 >= 0:
            em.add_field(name=f"{cryptoname13}",value=f"```py\n🟢${cryptoprice13} {cryptoratio13}%```",inline=True)
        if cryptoratio13 <=0:
            em.remove_field(index=13)
            em.add_field(name=f"{cryptoname13}",value=f"```py\n🔴${cryptoprice13} {cryptoratio13}%```",inline=True)

        if cryptoratio14 >= 0:
            em.add_field(name=f"{cryptoname14}",value=f"```py\n🟢${cryptoprice14} {cryptoratio14}%```",inline=True)
        if cryptoratio14 <=0:
            em.remove_field(index=14)
            em.add_field(name=f"{cryptoname14}",value=f"```py\n🔴${cryptoprice14} {cryptoratio14}%```",inline=True)

        if cryptoratio15 >= 0:
            em.add_field(name=f"{cryptoname15}",value=f"```py\n🟢${cryptoprice15} {cryptoratio15}%```",inline=True)
        if cryptoratio15 <=0:
            em.remove_field(index=15)
            em.add_field(name=f"{cryptoname15}",value=f"```py\n🔴${cryptoprice15} {cryptoratio15}%```",inline=True)

        if cryptoratio16 >= 0:
            em.add_field(name=f"{cryptoname16}",value=f"```py\n🟢${cryptoprice16} {cryptoratio16}%```",inline=True)
        if cryptoratio16 <=0:
            em.remove_field(index=16)
            em.add_field(name=f"{cryptoname16}",value=f"```py\n🔴${cryptoprice16} {cryptoratio16}%```",inline=True)

        if cryptoratio17 >= 0:
            em.add_field(name=f"{cryptoname17}",value=f"```py\n🟢${cryptoprice17} {cryptoratio17}%```",inline=True)
        if cryptoratio17 <=0:
            em.remove_field(index=17)
            em.add_field(name=f"{cryptoname17}",value=f"```py\n🔴${cryptoprice17} {cryptoratio17}%```",inline=True)

        if cryptoratio18 >= 0:
            em.add_field(name=f"{cryptoname18}",value=f"```py\n🟢${cryptoprice18} {cryptoratio18}%```",inline=True)
        if cryptoratio18 <=0:
            em.remove_field(index=18)
            em.add_field(name=f"{cryptoname18}",value=f"```py\n🔴${cryptoprice18} {cryptoratio18}%```",inline=True)

        if cryptoratio19 >= 0:
            em.add_field(name=f"{cryptoname19}",value=f"```py\n🟢${cryptoprice19} {cryptoratio19}%```",inline=True)
        if cryptoratio19 <=0:
            em.remove_field(index=19)
            em.add_field(name=f"{cryptoname19}",value=f"```py\n🔴${cryptoprice19} {cryptoratio19}%```",inline=True)

        if cryptoratio20 >= 0:
            em.add_field(name=f"{cryptoname20}",value=f"```py\n🟢${cryptoprice20} {cryptoratio20}%```",inline=True)
        if cryptoratio20 <=0:
            em.remove_field(index=20)
            em.add_field(name=f"{cryptoname20}",value=f"```py\n🔴${cryptoprice20} {cryptoratio20}%```",inline=True)

        if cryptoratio21 >= 0:
            em.add_field(name=f"{cryptoname21}",value=f"```py\n🟢${cryptoprice21} {cryptoratio21}%```",inline=True)
        if cryptoratio21 <=0:
            em.remove_field(index=21)
            em.add_field(name=f"{cryptoname21}",value=f"```py\n🔴${cryptoprice21} {cryptoratio21}%```",inline=True)

        master_list = cryptoratio1

        await inter.edit_original_message(embed=em)
        if counter == 75:
            await inter.send("```py\nStream has ended. Use...``` </crypto coin:1036704980100448353> ```py\n...to call the command again.```")
            break

        master_list = [
            cryptoratio1,
            cryptoratio2,
            cryptoratio3,
            cryptoratio4,
            cryptoratio5,
            cryptoratio6
            ,cryptoratio7
            ,cryptoratio8
            ,cryptoratio9
            ,cryptoratio10
            ,cryptoratio11
            ,cryptoratio12
            ,cryptoratio13
            ,cryptoratio14
            ,cryptoratio15
            ,cryptoratio16
            ,cryptoratio17
            ,cryptoratio18
            ,cryptoratio19
            ,cryptoratio20
            ,cryptoratio21]

        alval, alidx = max((alval, alidx) for (alidx, alval) in enumerate(master_list))
        index0 = master_list[alidx]
        print(index0, alval)

















""" @bot.command()
async def lowfloat(ctx):
    data = client.low_float()[0:20]
    rank = [i['Rank'] for i in data]
    items = "\n".join(f"```py\n#{i['Rank']} {i['ticker']} {i['company_name']} 1Day Change:${i['one_day_change']}``` ```py\n Float Shares: {i['floating_shares']}\nOutstanding Shares:{i['outstanding_shares']}``` ```py\n shortInterest: {i['short_int']} Mkt Cap:{i['market_cap']} Industry:{i['industry']}```" for i in data)
    em = disnake.Embed(title="Low Float Tickers and Short Interest", description=f"{items}",color=disnake.Colour.dark_orange())
    await ctx.send(embed = em) """










@bot.command()
async def q(inter:disnake.AppCmdInter, query):
    API_KEY = "AIzaSyC19KUFd0vh6rRdMygGSwwXjyRKVJAPLDw"
    # get your Search Engine ID on your CSE control panel
    SEARCH_ENGINE_ID = "c0ae864ace74c490c"
  #  query = {query}
    page = 1
    # constructing the URL
    # doc: https://developers.google.com/custom-search/v1/using_rest
    start = (page - 1) * 1 + 1
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}"
    data = requests.get(url).json()
    search_items = data.get("items")
    for i, search_item in enumerate(search_items, start=1):
        try:
            long_description = search_item["pagemap"]["metatags"][0]["og:description"]
        except KeyError:
            long_description = "N/A"
        # get the page title
        title = search_item.get("title")
        # page snippet#
        snippet = search_item.get("snippet")
        # alternatively, you can get the HTML snippet (bolded keywords)
        #html_snippet = search_item.get("htmlSnippet")
        # extract the page url
        link = search_item.get("link")
        # print the results
        em = disnake.Embed(title=f"{title}", description=f"{snippet}", color=disnake.Colour.random(),url=f"{link}")
        print("="*1, f"Result #{i+start-1}", "="*1)
        print("Title:", title)
        print("Description:", snippet)
        print("Long description:", long_description)
        with open('documents.txt', 'a') as outfile:
            json.dump(f"''{title} |'':''{snippet} | {link},", outfile, indent=2)
            outfile.close()
        sleep(5)
        await inter.send(embed=em)


@bot.slash_command()
async def rsi(inter:disnake.AppCmdInter, symbol: str=commands.Param(autocomplete=ticker_autocomp)):
    """Returns the 1 minute RSI."""
    await inter.response.defer(with_message=True)
    dtime = datetime.now() - timedelta(minutes=60)
    dtime2 = datetime.now()

    
    dtimestamp = int(round(dtime.timestamp()))
    dtimestamp2 = int(round(dtime2.timestamp()))
    finnhub_client = finnhub.Client(api_key=finnhubkey)
    r = finnhub_client.technical_indicator(symbol=f"{symbol}", resolution='1', _from=dtimestamp, to=dtimestamp2, indicator='rsi', indicator_fields={"timeperiod": 14})
    rsi = r['rsi']
    currentrsi = rsi[15]
    em = disnake.Embed(title=f"RSI Stream for {symbol}", description=f"```py\nOne Minute Rsi - Updates every 60 seconds.``````py\n The RSI for {symbol} is currently {currentrsi}```", color=disnake.Colour.random())
    view = disnake.ui.View()
    await inter.edit_original_message(embed=em, view=view)








@bot.slash_command()
async def source(inter:disnake.AppCmdInter, document: str=commands.Param(autocomplete=document_autocomp)):
    doc = docs_dict[document]
    await inter.send(f"```py\n{document}``` {doc}")










@bot.slash_command()
async def core(inter:disnake.AppCmdInter):
    await inter.send("```py\nUse /fudstop. Many results on the screener.```")




@bot.slash_command()
async def lowfloats(inter: disnake.AppCmdInter):
    """Returns tickers with the lowest floats."""
    await inter.response.defer(with_message=True)
    data = client.low_float()
    ticker = [i['ticker'] for i in data]
    shotint = [i['short_int'] for i in data]
    float = [i['floating_shares'] for i in data]
    rank = [i['Rank'] for i in data]
    items = "\n".join(f"TICKER: {i['ticker']} | SHORT INTEREST % OF FLOAT: {i['short_int']}" for i in data)
    for tickers, shotints, floats, ranks in zip(ticker, shotint, float, rank):
        embed = disnake.Embed(title="Top 50 Lowest Float Stocks with Short Interest % of Float", description=f"**{tickers}** has **{shotints}%** of its float short and ranks **{ranks}** with a float of **{floats}** shares.", color=disnake.Colour.random())
        embed.set_footer(text="Implemented by FUDSTOP Trading.", icon_url="https://uploads-ssl.webflow.com/62661f74776abb77ef7621a8/6272ac0a541297826e1a5209_963244979063517184.gif")

        await inter.edit_original_message(embed=embed, view=MainView2())
        sleep(2)


















@bot.slash_command()
async def charlies_vids(inter:disnake.AppCmdInter, video: str=commands.Param(autocomplete=video_autocomp)):
    """Start typing and learn what your heart desires"""
    await inter.response.defer(with_message=True)
    base_url = "https://youtu.be/"
    link = base_url + vids_dict[video]
    embed = disnake.Embed(title="Shilly's Videos", description=f"When you start typing - it will predict what you are looking for. The following topics are currently imported:")
    embed.add_field(name="TOPICS TO SEARCH", value="\n\n"
"**Discord  Core Logic  Commands, Macro Economics, Options, Trading, Market Mechanics, The Market, Research, Filings, SFT, NSCC, Gaps, Psychology, China, ETFs, Core Logic**")
    embed.set_footer(text="Implemented by FUDSTOP Trading")

    await inter.edit_original_message(embed=embed)
    await inter.channel.send(link)



@bot.slash_command()
async def etf(inter):
    """PARENT"""



@etf.sub_command()
async def assets(inter: disnake.AppCmdInter,
symbol: str=commands.Param(autocomplete=tickerlist_autocomp)):
    """Analyze assets of an ETF. ONLY WORKS ON ETFS"""
    await inter.response.defer(with_message=True)
    ids = ticker_list[symbol]
    r = requests.get(url=f"https://quoteapi.webullfintech.com/api/securities/fund/{ids}/assetsMore")
    d = r.json()
    assetsv2 = d['assetsAnalysisV2'] or None
    indexv2 = assetsv2[0]
    datev2 = indexv2['reporDate']
    #assetsfv2 = float(indexv2['assets']) or 0
    cashassetsfv2 = float(indexv2['cashAssets']) or 0
    cashassetsv2 = round(cashassetsfv2*0.000000001,ndigits=2) or 0
    bondassetsfv2 = float(indexv2['bondAssets']) or 0
    bondassetsv2 = round(bondassetsfv2*0.000000001, ndigits=2) or 0
    stockassetsfv2 = float(indexv2['stockAssets']) or 0
    stockassetsv2 = round(stockassetsfv2*0.000000001, ndigits=2) or 0
    otherassetsfv2 = float(indexv2['otherAssets']) or 0
    otherassetsv2 = round(otherassetsfv2*0.000000001, ndigits=2) or 0
    stockratiov2 = indexv2['stockRatio']
    bondratiov2 = indexv2['bondRatio']
    cashratiov2 = indexv2['cashRatio']
    otherratiov2 = indexv2['otherRatio']
    quarterv2 = indexv2['quarter']

    emb = disnake.Embed(title=f"Assets Analysis for {symbol}", description=f"```py\nReported: {datev2} during Quarter: {quarterv2}``` ```py\nCash Assets: {cashassetsv2} billion.\nBond Assets: {bondassetsv2} billion.\nStock Assets: {stockassetsv2} billion.\nOther Assets: {otherassetsv2}```", color=disnake.Colour.dark_red())
    emb.add_field(name="Ratios:", value=f"```py\nStock: {stockratiov2}%``` ```py\nBonds: {bondratiov2}%``` ```py\nCash: {cashratiov2}%``` ```py\nOther: {otherratiov2}%```")
    await inter.edit_original_message(embed=emb)


@assets.error
async def assetserror(inter: disnake.AppCmdInter, error):
    if isinstance(error, commands.CheckAnyFailure):
        await inter.send("```py\n Make sure you're using an ETF and that youre using all CAPS.```")


class Search(disnake.ui.Select):
    def __init__(self, query:str):
        """SEARCH CLASS"""
        self.query = query
        API_KEY = "AIzaSyC19KUFd0vh6rRdMygGSwwXjyRKVJAPLDw"
        # get your Search Engine ID on your CSE control panel
        SEARCH_ENGINE_ID = "c0ae864ace74c490c"
        num = 10
        # constructing the URL
        # doc: https://developers.google.com/custom-search/v1/using_rest
        start = 1
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}&num={num}&sort=date"
        data = requests.get(url).json()
        #kind = data['kind']
        url = data['url']
        #querys = data['queries']
        #info = data['searchInformation']
        items = data['items']
        item1 = items[0]
        title1 = item1['title']
        #link1 = item1['link']
        #snip1 = item1['htmlSnippet']




        item2 = items[1]
        title2 = item2['title']
        #link2 = item2['link']
        #snip2 = item2['htmlSnippet']





        item3 = items[2]
        title3 = item3['title']
        #link3 = item3['link']
        #snip3 = item3['htmlSnippet']

        



        item4 = items[3]
        title4 = item4['title']
        #link4 = item4['link']
        #snip4 = item4['htmlSnippet']





        item5 = items[4]
        title5 = item5['title']
        #link5 = item5['link']
        #snip5 = item5['htmlSnippet']




        item6 = items[5]
        title6 = item6['title']
        #link6 = item6['link']
        #snip6 = item6['htmlSnippet']




        item7 = items[6]
        title7 = item7['title']
        #link7 = item7['link']
        #snip7 = item7['htmlSnippet']





        item8 = items[7]
        title8 = item8['title']
        #link8 = item8['link']
        #snip8 = item8['htmlSnippet']

     


        item9 = items[8]
        title9 = item9['title']
        #link9 = item9['link']
        #snip9 = item9['htmlSnippet']

     



        item10 = items[9]
        title10 = item10['title']
        #link10 = item10['link']
        #snip10 = item10['htmlSnippet']


        options = [
            disnake.SelectOption(label=f"{title1}"or "N/A"),
            disnake.SelectOption(label=f"{title2}"or "N/A"),
            disnake.SelectOption(label=f"{title3}"or "N/A"),
            disnake.SelectOption(label=f"{title4}"or "N/A"),
            disnake.SelectOption(label=f"{title5}"or "N/A"),
            disnake.SelectOption(label=f"{title6}"or "N/A"),
            disnake.SelectOption(label=f"{title7}"or "N/A"),
            disnake.SelectOption(label=f"{title8}"or "N/A"),
            disnake.SelectOption(label=f"{title9}"or "N/A"),
            disnake.SelectOption(label=f"{title10}"or "N/A"),
        ]

        super().__init__(
            placeholder = f"🔎  🇷  🇪  🇸  🇺 🇱  🇹  🇸 🔍",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: disnake.MessageCommandInteraction, query):
        API_KEY = "AIzaSyC19KUFd0vh6rRdMygGSwwXjyRKVJAPLDw"
        # get your Search Engine ID on your CSE control panel
        SEARCH_ENGINE_ID = "c0ae864ace74c490c"
        num = 10
        # constructing the URL
        # doc: https://developers.google.com/custom-search/v1/using_rest
        start = 1
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={self.query}&start={start}&num={num}&sort=date"
        data = requests.get(url).json()
        #kind = data['kind']
        url = data['url']
        #querys = data['queries']
        #info = data['searchInformation']
        items = data['items']
        item1 = items[0]
        #title1 = item1['title']
        link1 = item1['link']
        snip1 = item1['htmlSnippet']





        item2 = items[1]
        #title2 = item2['title']
        link2 = item2['link']
        snip2 = item2['htmlSnippet']


        item3 = items[2]
        #title3 = item3['title']
        link3 = item3['link']
        snip3 = item3['htmlSnippet']

        



        item4 = items[3]
        #title4 = item4['title']
        link4 = item4['link']
        snip4 = item4['htmlSnippet']




        item5 = items[4]
        #title5 = item5['title']
        link5 = item5['link']
        snip5 = item5['htmlSnippet']





        item6 = items[5]
        #title6 = item6['title']
        link6 = item6['link']
        snip6 = item6['htmlSnippet']

    



        item7 = items[6]
        #title7 = item7['title']
        link7 = item7['link']
        snip7 = item7['htmlSnippet']





        item8 = items[7]
        #title8 = item8['title']
        link8 = item8['link']
        snip8 = item8['htmlSnippet']





        item9 = items[8]
        #title9 = item9['title']
        link9 = item9['link']
        snip9 = item9['htmlSnippet']





        item10 = items[9]
        #title10 = item10['title']
        link10 = item10['link']
        snip10 = item10['htmlSnippet']
        view = disnake.ui.View()
        view.add_item(Search(query))

        if self.values[0] == self.values[0]:
            em = disnake.Embed(title=self.values[0], description=f"```py\n{snip1}```", color=disnake.Colour.random(), url=f"{link1}")
            await interaction.response.edit_message(embed=em)

        elif self.values[0] == self.values[0]:
            em = disnake.Embed(title=self.values[0], description=f"```py\n{snip2}```", color=disnake.Colour.random(), url=f"{link2}")
            await interaction.response.edit_message(embed=em)

        elif self.values[0] == self.values[0]:
            em = disnake.Embed(title=self.values[0], description=f"```py\n{snip3}```", color=disnake.Colour.random(), url=f"{link3}")
            await interaction.response.edit_message(embed=em)

        elif self.values[0] == self.values[0]:
            em = disnake.Embed(title=self.values[0], description=f"```py\n{snip4}```", color=disnake.Colour.random(), url=f"{link4}")
            await interaction.response.edit_message(embed=em)

        elif self.values[0] == self.values[0]:
            em = disnake.Embed(title=self.values[0], description=f"```py\n{snip5}```", color=disnake.Colour.random(), url=f"{link5}")
            await interaction.response.edit_message(embed=em)

        elif self.values[0] == self.values[0]:
            em = disnake.Embed(title=self.values[0], description=f"```py\n{snip6}```", color=disnake.Colour.random(), url=f"{link6}")
            await interaction.response.edit_message(embed=em)
        elif self.values[0] == self.values[0]:
            em = disnake.Embed(title=self.values[0], description=f"```py\n{snip7}```", color=disnake.Colour.random(), url=f"{link7}")
            await interaction.response.edit_message(embed=em)

        elif self.values[0] == self.values[0]:
            em = disnake.Embed(title=self.values[0], description=f"```py\n{snip8}```", color=disnake.Colour.random(), url=f"{link8}")
            await interaction.response.edit_message(embed=em)

        elif self.values[0] == self.values[0]:
            em = disnake.Embed(title=self.values[0], description=f"```py\n{snip9}```", color=disnake.Colour.random(), url=f"{link9}")
            await interaction.response.edit_message(embed=em)

        elif self.values[0] == self.values[0]:
            em = disnake.Embed(title=self.values[0], description=f"```py\n{snip10}```", color=disnake.Colour.random(), url=f"{link10}")
            await interaction.response.edit_message(embed=em)



@bot.slash_command()
async def search(self,interaction:disnake.ApplicationCommandInteraction, query: str, number_of_results:str):
    """Search for government and relevant market documents."""
    await interaction.response.defer(with_message=True)
    
    API_KEY = "AIzaSyC19KUFd0vh6rRdMygGSwwXjyRKVJAPLDw"
    # get your Search Engine ID on your CSE control panel
    SEARCH_ENGINE_ID = "c0ae864ace74c490c"

    # constructing the URL
    # doc: https://developers.google.com/custom-search/v1/using_rest
    start = 1
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}&num={number_of_results}&sort=date"
    data = requests.get(url).json()
    url = data['url']
    items = data[0]
    item1 = items[0]
    title1 = item1['title']
    link1 = item1['link']
    snip1 = item1['htmlSnippet']


    item2 = items[1]
    item2 = None

    title2 = item2['title']
    link2 = item2['link']
    snip2 = item2['htmlSnippet']


    item3 = items[2]


    title3 = item3['title']
    link3 = item3['link']
    snip3 = item3['htmlSnippet']


            



    item4 = items[3]
    title4 = item4['title']
    link4 = item4['link']
    snip4 = item4['htmlSnippet']




    item5 = items[4]
    title5 = item5['title']
    link5 = item5['link']
    snip5 = item5['htmlSnippet']





    item6 = items[5]
    title6 = item6['title']
    link6 = item6['link']
    snip6 = item6['htmlSnippet']





    item7 = items[6]
    title7 = item7['title']
    link7 = item7['link']
    snip7 = item7['htmlSnippet']





    item8 = items[7]
    title8 = item8['title']
    link8 = item8['link']
    snip8 = item8['htmlSnippet']





    item9 = items[8]
    title9 = item9['title']
    link9 = item9['link']
    snip9 = item9['htmlSnippet']





    item10 = items[9]
    title10 = item10['title']
    link10 = item10['link']
    snip10 = item10['htmlSnippet']




    embeds = [
        disnake.Embed(title=f"{title1}-", description=f"```py\n{snip1}-```", color=disnake.Colour.random(), url=f"{link1}" or None),
        disnake.Embed(title=f"{title2}-", description=f"```py\n{snip2}-```",color=disnake.Colour.random(), url=f"{link2}" or None),
        disnake.Embed(title=f"{title3}-", description=f"```py\n{snip3}-```", color=disnake.Colour.random(), url=f"{link3}" or None),
        disnake.Embed(title=f"{title4}-", description=f"```py\n{snip4}-```", color=disnake.Colour.random(), url=f"{link4}" or None),
        disnake.Embed(title=f"{title5}-", description=f"```py\n{snip5}-```", color=disnake.Colour.random(), url=f"{link5}" or None),
        disnake.Embed(title=f"{title6}-", description=f"```py\n{snip6}```",color=disnake.Colour.random(), url=f"{link6}" or None),
        disnake.Embed(title=f"{title7}-", description=f"```py\n{snip7}-```", color=disnake.Colour.random(), url=f"{link7}" or None),
        disnake.Embed(title=f"{title8}-", description=f"```py\n{snip8}-```", color=disnake.Colour.random(), url=f"{link8}" or None),
        disnake.Embed(title=f"{title9}--", description=f"```py\n{snip9}-```", color=disnake.Colour.random(), url=f"{link9}" or None),
        disnake.Embed(title=f"{title10}-", description=f"```py\n{snip10}-```", color=disnake.Colour.random(), url=f"{link10}" or None),
    ]



    await interaction.edit_original_response(embed=embeds[0], view=Menu(embeds))

@search.error
async def searcherror(self,inter: disnake.AppCmdInter, error):
    """HANDLER"""
    if isinstance(error, commands.CheckAnyFailure):
        await inter.send("```py\n Must use caps - and can't be an ETF as ETFs dont have financial data such as earnings metrics.```")

@bot.command()
async def harvest(ctx):
    base_url = "https://quotes-gw.webullfintech.com/api/quote/option/quotes/queryBatch?derivativeIds="

    c1=1034976458
    c2=1034986458
    c3=1034996458
    c4=1035006458
    c5=1035016458
    c6=1035026458
    c7=1022082087
    c8=1022182087
    c9=1022282087
    c10=1022382087
    c11=1022482087
    c12=1022582087
    c13=1022682087
    c14=1022782087
    c15=1022882087
    c16=1022982087
    c17=1023082087
    c18=1023182087
    c19=1023282087
    c20=1023382087
    c21=1023482087
    c22=1023582087
    c23=1023682087
    c24=1023782087
    c25=1023882087
    c26=1023982087
    c27=1024082087
    c28=1024182087
    c29=1024282087
    c30=1024382087
    c31=1024482087
    c32=1035016458
    c33=1035026458
    c34=1035036458
    c35=1035046458
    c36=1035056458
    c37=1035066458
    c38=1035076458
    c39=1035086458
    c40=1035096458
    c41=1035106458
    c42=1035116458
    c43=1035126458
    c44=1035136458
    c45=1035146458
    c46=1035156458
    c47=1035166458
    c48=1035176458
    c49=1035186458
    c50=1035196458
    c51=1035206458
    c52=1035216458
    c53=1035226458
    c54=1035236458
    while True:
        r2 = requests.get(f"https://quotes-gw.webullfintech.com/api/quote/option/quotes/queryBatch?derivativeIds={c1},{c2},{c3},{c4},{c5},{c6},{c7},{c8},{c9},{c10},{c11},{c12},{c13},{c14},{c15},{c16},{c17},{c18},{c19},{c20},{c21},{c22},{c23},{c24},{c25},{c26},{c27},{c28},{c29},{c30},{c31},{c32},{c33},{c34},{c35},{c36},{c37},{c38},{c39},{c40},{c41},{c42},{c43},{c44},{c45},{c46},{c47},{c48},{c49},{c50},{c51},{c52},{c53},{c54}")
        d2 = r2.json()
        c1=c1+1
        c2=c2+1
        c3=c3+1
        c4=c4+1
        c5=c5+1
        c6=c6+1
        c7=c7+1
        c8=c8+1
        c9=c9+1
        c10=c10+1
        c11=c11+1
        c12=c12+1
        c13=c13+1
        c14=c14+1
        c15=c15+1
        c16=c16+1
        c17=c17+1
        c18=c18+1
        c19=c19+1
        c20=c20+1
        c21=c21+1
        c22=c22+1
        c23=c23+1
        c24=c24+1
        c25=c25+1
        c26=c26+1
        c27=c27+1
        c28=c28+1
        c29=c29+1
        c30=c30+1
        c31=c31+1
        c32=c32+1
        c33=c33+1
        c34=c34+1
        c35=c35+1
        c36=c36+1
        c37=c37+1
        c38=c38+1
        c39=c39+1
        c40=c40+1
        c41=c41+1
        c42=c42+1
        c43=c43+1
        c44=c44+1
        c45=c45+1
        c46=c46+1
        c47=c47+1
        c48=c48+1
        c49=c49+1
        c50=c50+1
        c51=c51+1
        c52=c52+1
        c53=c53+1
        for i in d2:
            tickerid2 = i.get('tickerId')
            symbol2 = i.get('unSymbol')
            ivh = i.get('impVol')
            ivc = float(str(ivh or 0))
            iv2 = round(ivc*100,ndigits=2)
            vol2 = int(i.get('volume'))
            ch=i.get('changeRatio')
            fch = float(ch) or 0
            cch = round(fch*100,ndigits=2)
            direct2 = i.get('direction')
            strike2 = i.get('strikePrice')
            ac2 = i.get('activeLevel')
            exp2 = i.get('expireDate')
            try:
                oichange = float(i.get('openIntChange') or 0)
            except ValueError:
                oichange = 0
            v2 = i.get('vega')
            ticker = i.get('disSym')
            d2f = i.get('delta')
            df2 = float(str(d2f or 0))
            d2 = round(df2*100, ndigits=2)

            g2 = i.get('gamma')
            oichng = i.get('openIntChange')
            oi = i.get('openInterest')
            if oichange >= 2000 and vol2 >= 10000 and bidprice <= 0.50 and d2 > 65:
                await ctx.send(f"```py\nContract with Open Interest Change of 2,000 or more - Volume of 10,000 or more, and Bid Price <= 0.50  with a > than 65% chance to close ITM Detected!\n\n{symbol2} {direct2} {strike2} {exp2}':'{tickerid2}', Oi Change: {oichange} Vol: {vol2} Delta: {d2} Bid: {bidprice}```")
                with open('oichange.txt', 'a') as outfile:
                    json.dump(f"{symbol2} {direct2} {strike2} {exp2}':'{tickerid2}', {oichange}", outfile, indent=2)
                    outfile.close()
            elif vol2 >= 10000:
                with open('vol.txt', 'a') as outfile:
                    json.dump(f"{symbol2} {direct2} {strike2} {exp2}':'{tickerid2}', {vol2}", outfile, indent=2)
                    outfile.close()
            bidlist = i.get('bidList') or 0
            asklist = i.get('askList') or 0
            if bidlist and asklist is not None:
                try: 
                    for i in bidlist:
                        bidvol = i.get('volume')
                        bidprice = int(float(i.get('price')))
                        bidex = i.get('quoteEx')
                        if bidprice >= 0.22:
                            if bidprice <= 0.30:
                                await ctx.send(f"```py\nCheapies found!!!\n\n${bidprice} {symbol2} {direct2} {strike2} {exp2}':'{tickerid2}', {oichange}```")
                                with open('cheapies.txt', 'a') as outfile:
                                    json.dump(f"${bidprice} {symbol2} {direct2} {strike2} {exp2}':'{tickerid2}', {oichange}", outfile, indent=2)
                                    outfile.close()
                except KeyError:
                    if bidlist and asklist is None:
                        bidlist = [0,0,0]
                        asklist = [0,0,0]

                    for i in asklist:
                        askvol = i.get('volume')
                        askprice = i.get('price')
                        askex = i.get('quoteEx')
                    if symbol2 is None:
                        continue
                    if bidlist is None:
                        continue
                    if asklist is None:
                        continue
                    if askprice is None:
                        continue
                    if bidprice is None:
                        continue
                    if bidex is None:
                        continue
                    if askex is None:
                        continue
                    if iv2 is None:
                        continue
                    if fch is None:
                        continue
                    if oichange is None:
                        continue
                    if oi is None:
                        continue
                    if d2 is None:
                        continue
                    if d2f is None:
                        continue
                    if df2 is None:
                        continue
                    if iv2 is None:
                        continue
                    if ivc is None:
                        continue


bot.load_extensions("cogs")
bot.load_extensions("cogs2")
bot.load_extensions("cogs3")
bot.run(token)
