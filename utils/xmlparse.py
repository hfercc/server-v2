import xml.dom.minidom as xmldom

def get(file):
    domobj = xmldom.parse(file)
    elementobj = domobj.documentElement
    r = list(elementobj.getElementsByTagName("Alpha"))
    r.extend(list(elementobj.getElementsByTagName("Operation")))
    return r

def generate(t):
    p1 = '<Config> \
    <SimulationSetting startdate="20170607" enddate="20180607" backdays="2" enable_performance="true" timeit="true" /> \
    <Date id="dates" path="./lib/dates_loader.so" datapath="/opt/data/research_cache/WindData" /> \
    <Ticker id="tickers" path="./lib/tickers_loader.so" datapath="/opt/data/research_cache/WindData"/> \
    <Universe id="universe" type="ALL" path="./lib/redis_universe_loader.so" datapath="/opt/data/research_cache/WindData"/> \
    <DataLoader id="tradable" path="./lib/redis_tradable_loader.so" datapath="/opt/data/research_cache/WindData"/> \
    <DataLoader id="essentials" path="./lib/redis_data_loader.so" datapath="/opt/data/research_cache/WindData" /> \
    <DataLoader id="IndexLoader" path="./lib/index_data_loader.so" datapath="/opt/data/research_cache/WindData" index="IC,IF"/> \
    <DataLoader id="GICS" GICS="GICS_II" path="./lib/GICS_loader.so" datapath="/opt/data/research_cache/WindData" />'

    p2 = '<Performance id="Performance" path="./lib/dummy_performance.so" output_name="output" capital="1000000" save_dir="./output" hedge_inex="IC" plot="false"/> \
</Config>'
    p3 = ' '.join([p.toxml() for p in t])
    return p1 + p3 + p2