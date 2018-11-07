import xml.dom.minidom as xmldom

def get(file, report):
    domobj = xmldom.parse(file)
    elementobj = domobj.documentElement
    r = list(elementobj.getElementsByTagName("Alpha"))
    p = list(elementobj.getElementsByTagName("DataLoader"))
    if report.alpha_type == 0:
      r[0].attributes['path'].value = './alpha/' + report.alpha_name + '.so'
    return r, p

def generate(r, p, report):
    universe_ = ['ALL', 'zz500', 'hs300']
    type_     = ['longshort', 'longonly', 'IC', 'IF']
    p1 = '<Config><SimulationSetting startdate="20090101" enddate="20180501" backdays="20" enable_performance="true" timeit="true"/> \
  <Date id="dates" path="dates_loader.so" datapath="/home/data/research_cache/JYData"/> \
  <Ticker id= "tickers" path="tickers_loader.so" datapath="/home/data/research_cache/JYData"/> \
  <Universe id="universe" type="' + universe_[report.universe] + '" path="universe_loader.so" datapath="/home/data/research_cache/JYData"/>' 
    

    if report.type_code > 1:
        p2 = '<Performance id="Performance" path="./lib/core/dummy_performance.so" output_name="output" capital="1000000" ' + 'hedge_index="{}" '.format(type_[report.type_code]) + 'save_dir="./output" plot="false"/> \
</Config>'
    else:
        p2 = '<Performance id="Performance" path="./lib/core/dummy_performance.so" output_name="output" capital="1000000" save_dir="./output" plot="false"/> </Config>'
    p3 = ' '.join([a.toxml() for a in r])
    p4 = ' '.join([b.toxml() for b in p])
    return p1 + p4 + p3 + p2
