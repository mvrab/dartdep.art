from flask import Flask, render_template, request

import requests
import re
from bs4 import BeautifulSoup
import datetime
import pytz
#import webbrowser
import os
import math
#from threading import Timer

#import logging
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

def get_parameters(selectedtrain):
    ################
    ###   TIME   ###
    ################

    timepattern = r"((1[0-2]|0?[1-9])\:([0-5]?[0-9])\s?(?:AM|PM|am|pm))"
    #currentTime = datetime.datetime.now()
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    currentTimecst = utc_now.astimezone(pytz.timezone("America/Chicago"))
    currentTime = currentTimecst.replace(tzinfo=None)

    x = re.findall(timepattern, selectedtrain[5])
    arrivalTimeM = datetime.datetime.strptime(x[0][0], '%I:%M %p')
    arrivalTime = arrivalTimeM.replace(day=currentTime.day, month=currentTime.month, year=currentTime.year)
    n1t = str(round((arrivalTime - currentTime).total_seconds()/60%1440)-1)
    if (int(n1t) > 1000) or (int(n1t) < 0): n1t = "Now"


    #######################
    ###   DESTINATION   ###
    #######################

    n1d = str(selectedtrain[3])[3:-4].title()
    if (n1d == 'Dfw'):
        n1d = 'DFW Airport'
    if (n1d == 'Unt'):
        n1d = 'UNT Dallas'
    if (n1d == 'N. Carrollton'):
        n1d = 'North Carrollton'
    if (n1d == 'Lbj / Central'):
        n1d = 'LBJ/Central'
    if (n1d == 'T&Amp;P Station'):
        n1d = 'Fort Worth T&P Station'


    #################
    ###   COLOR   ###
    #################

    colorpattern = r'<b>(.+?) LINE'

    n1c_string = str(selectedtrain[1])
    try:
        n1c = re.findall(colorpattern, n1c_string)[0].lower()
        n1c = "w3-safety-" + n1c
    except:
        n1c = "w3-food-grape"

    return (n1d, n1t, n1c)


app = Flask(__name__)
#global refresh_counter
#refresh_counter = 0

@app.route('/')
def index():
    global refresh_counter
    try:
        stop_id = request.args.get('stationID')
        if stop_id == None:
            column1str = ""
            column2str = ""
            column3str = ""
            column4str = ""
            cyclecounter = 0
            quarterlistlen = math.ceil(len(stationIDdict)/4)
            for stationName in stationIDdict:
                station_name_camelcase = stationName.title()
                if station_name_camelcase == "Dfw Airport Station":
                    station_name_camelcase = "DFW Airport Station"
                if station_name_camelcase == "Lbj / Central Station":
                    station_name_camelcase = "LBJ/Central Station"
                if station_name_camelcase == "Lbj / Skillman Station":
                    station_name_camelcase = "LBJ/Skillman Station"
                if station_name_camelcase == "Smu/Mockingbird Station":
                    station_name_camelcase = "SMU/Mockingbird Station"
                if station_name_camelcase == "Va Medical Center Station":
                    station_name_camelcase = "VA Medical Center Station"
                if station_name_camelcase == "Illinois Tc/Station":
                    station_name_camelcase = "Illinois Station"
                if station_name_camelcase == "Ebj Union Station":
                    station_name_camelcase = "EBJ Union Station"
                if station_name_camelcase == "Forest Ln Station":
                    station_name_camelcase = "Forest Lane Station"
                if station_name_camelcase == "Unt Dallas Station":
                    station_name_camelcase = "UNT Dallas Station"
                if station_name_camelcase == "Mlk Station":
                    station_name_camelcase = "MLK, Jr. Station"
                if station_name_camelcase == "St Paul Station":
                    station_name_camelcase = "St. Paul Station"
                if station_name_camelcase == "8Th & Corinth Station":
                    station_name_camelcase = "8th & Corinth Station"
                if station_name_camelcase == "Forest / Jupiter Station":
                    station_name_camelcase = "Forest/Jupiter Station"
                    
                cyclecounter += 1
                
                stationID = stationIDdict[stationName]
                html_insert = f"<div class=\"w3-dark-grey w3-round-xlarge w3-button w3-block w3-container w3-section\" onclick=\"document.location='https://dartdep.art/?stationID={stationID}'\"><h4>{station_name_camelcase}</h4></div>"
                
                if 0 <= cyclecounter <= quarterlistlen:
                    column1str = column1str + html_insert
                if quarterlistlen+1 <= cyclecounter <= 2*quarterlistlen:
                    column2str = column2str + html_insert
                if 2*quarterlistlen+1 <= cyclecounter <= 3*quarterlistlen:
                    column3str = column3str + html_insert
                if 3*quarterlistlen+1 <= cyclecounter:
                    column4str = column4str + html_insert
            
            return render_template('homepage.html', column1str=column1str, column2str=column2str, column3str=column3str, column4str=column4str)
            #return 'pick a station first, e.g. 32041'
        
        
        
        
        response = requests.get('https://m.dart.org/railSchedule.asp?switch=pushRailStops3&ddlRailStopsFrom='+str(stop_id)+'&option=1', timeout=3)
        soup = BeautifulSoup(response.text, 'html.parser')
        allTrains = soup.findAll(['div','img'])
        
        northboundtrains = []
        southboundtrains = []
        platform3trains = []
        platform = 0
        for entry in allTrains:
            if "images/blank.gif" in str(entry):
                platform += 1
            elif "table" in str(entry):
                if platform == 1:
                    northboundtrains.append(entry)
                if platform == 2:
                    southboundtrains.append(entry)
                if platform == 3:
                    platform3trains.append(entry)
        
        entrytemplate ='        <div class="w3-round-xlarge {{ n1c }}">\n          <div class="w3-row w3-display-container">\n            <div class="w3-col w3-dark-grey w3-right w3-text-white w3-center w3-round-xlarge compact" style="width:100px">\n              <div style="line-height:35%;"> <br> </div><h5><b>{{ n1t }}</b></h5>Minutes\n            </div>\n            <div class="w3-rest w3-margin-left w3-display-left">\n              <h3>{{ n1d }}</h3>\n            </div>\n          </div>\n        </div>\n        <div class="w3-margin-bottom"></div>\n'
    
        northentry = ''
        for train in northboundtrains:
            temporaryentrytemplate = entrytemplate
            parameter_list = list(train)
            (n1d, n1t, n1c) = get_parameters(parameter_list)
            #print(n1d, n1t, n1c)
    
            temporaryentrytemplate=temporaryentrytemplate.replace("{{ n1d }}", n1d)
            temporaryentrytemplate=temporaryentrytemplate.replace("{{ n1c }}", n1c)
            temporaryentrytemplate=temporaryentrytemplate.replace("{{ n1t }}", n1t)
            northentry += temporaryentrytemplate
    
        southentry = ''
        for train in southboundtrains:
            temporaryentrytemplate = entrytemplate
            parameter_list = list(train)
            (n1d, n1t, n1c) = get_parameters(parameter_list)
            #print(n1d, n1t, n1c)
    
            temporaryentrytemplate=temporaryentrytemplate.replace("{{ n1d }}", n1d)
            temporaryentrytemplate=temporaryentrytemplate.replace("{{ n1c }}", n1c)
            temporaryentrytemplate=temporaryentrytemplate.replace("{{ n1t }}", n1t)
            southentry += temporaryentrytemplate
    
        platform3entry = ''
        for train in platform3trains:
            temporaryentrytemplate = entrytemplate
            parameter_list = list(train)
            (n1d, n1t, n1c) = get_parameters(parameter_list)
            #print(n1d, n1t, n1c)
    
            temporaryentrytemplate=temporaryentrytemplate.replace("{{ n1d }}", n1d)
            temporaryentrytemplate=temporaryentrytemplate.replace("{{ n1c }}", n1c)
            temporaryentrytemplate=temporaryentrytemplate.replace("{{ n1t }}", n1t)
            platform3entry += temporaryentrytemplate
            
        northtext = northentry.split('\n')
        southtext = southentry.split('\n')
        platform3text = platform3entry.split('\n')
        
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        currentTimecst = utc_now.astimezone(pytz.timezone("America/Chicago"))
        clock_time_obj = currentTimecst.replace(tzinfo=None)
        clockstr = clock_time_obj.strftime("%I:%M %p")
        clockstr = clock_time_obj.strftime("%I:%M %p")
        if clockstr[0] == "0":
            clockstr = clockstr[1:]
        refresh_counter = 0
        
        station_name_camelcase = stationNAMEdict[stop_id].title()
        if station_name_camelcase == "Dfw Airport Station":
            station_name_camelcase = "DFW Airport Station"
        if station_name_camelcase == "Lbj / Central Station":
            station_name_camelcase = "LBJ/Central Station"
        if station_name_camelcase == "Lbj / Skillman Station":
            station_name_camelcase = "LBJ/Skillman Station"
        if station_name_camelcase == "Smu/Mockingbird Station":
            station_name_camelcase = "SMU/Mockingbird Station"
        if station_name_camelcase == "Va Medical Center Station":
            station_name_camelcase = "VA Medical Center Station"
        if station_name_camelcase == "Illinois Tc/Station":
            station_name_camelcase = "Illinois Station"
        if station_name_camelcase == "Ebj Union Station":
            station_name_camelcase = "EBJ Union Station"
        if station_name_camelcase == "Forest Ln Station":
            station_name_camelcase = "Forest Lane Station"
        if station_name_camelcase == "Unt Dallas Station":
            station_name_camelcase = "UNT Dallas Station"
        if station_name_camelcase == "Mlk Station":
            station_name_camelcase = "MLK, Jr. Station"
        if station_name_camelcase == "St Paul Station":
            station_name_camelcase = "St. Paul Station"
        if station_name_camelcase == "8Th & Corinth Station":
            station_name_camelcase = "8th & Corinth Station"
        if station_name_camelcase == "Forest / Jupiter Station":
            station_name_camelcase = "Forest/Jupiter Station"
            
        if (len(platform3trains) == 0 and len(northboundtrains) == 0 and len(southboundtrains) == 0):
            return render_template('index-nodepartures.html', station_name=station_name_camelcase, clockstr=clockstr)
        if len(platform3trains)>0:
            return render_template('index-thirds.html', station_name=station_name_camelcase, clockstr=clockstr, southtext=southtext, northtext=northtext, platform3text=platform3text)
        return render_template('index.html', station_name=station_name_camelcase, clockstr=clockstr, southtext=southtext, northtext=northtext)
        
    except Exception as error:
        #print(error)
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        currentTimecst = utc_now.astimezone(pytz.timezone("America/Chicago"))
        clock_time_obj = currentTimecst.replace(tzinfo=None)
        clockstr = clock_time_obj.strftime("%I:%M %p")
        if clockstr[0] == "0":
            clockstr = clockstr[1:]
        #return str(error)
        return render_template('reload.html', clockstr=clockstr, attemptstr=str(error))

stationIDdict = {
  "8TH & CORINTH STATION": "15262",
  "AKARD STATION": "22750",
  "ARAPAHO CENTER STATION": "26673",
  "BACHMAN STATION": "29821",
  "BAYLOR STATION": "32042",
  "BELL STATION": "28180",
  "BELT LINE STATION": "31089",
  "BUCKNER STATION": "29834",
  "BURBANK STATION": "29822",
  "CAMP WISDOM STATION": "33086",
  "CEDARS STATION": "22729",
  "CENTREPORT STATION": "28178",
  "CITYLINE/BUSH STATION": "26895",
  "CITYPLACE/UPTOWN STATION": "26420",
  "CONVENTION CENTER STATION": "22747",
  "DEEP ELLUM STATION": "32043",
  "DFW AIRPORT STATION": "32553",
  "DOWNTOWN CARROLLTON STATION": "29817",
  "DOWNTOWN GARLAND STATION": "26691",
  "DOWNTOWN IRVING/HERITAGE CROSSING STATION": "28174",
  "DOWNTOWN PLANO STATION": "26896",
  "DOWNTOWN ROWLETT STATION": "32562",
  "EBJ UNION STATION": "22748",
  "FAIR PARK STATION": "29829,32041",
  "FARMERS BRANCH STATION": "29818",
  "FOREST / JUPITER STATION": "26690",
  "FOREST LN STATION": "26671",
  "FORT WORTH INTERMODAL TRANSIT CENTER": "28251",
  "GALATYN PARK STATION": "26674",
  "HAMPTON STATION": "21210",
  "HATCHER STATION": "29831",
  "HIDDEN RIDGE STATION": "33566",
  "ILLINOIS TC/STATION": "21030",
  "INWOOD/LOVE FIELD STATION": "29824",
  "IRVING CONVENTION CENTER STATION": "32338",
  "KIEST STATION": "23390",
  "LAKE HIGHLANDS STATION": "32049",
  "LAKE JUNE STATION": "29833",
  "LAS COLINAS URBAN CENTER STATION": "32337",
  "LAWNVIEW STATION": "29832",
  "LBJ / CENTRAL STATION": "26670",
  "LBJ / SKILLMAN STATION": "26668",
  "LEDBETTER STATION": "23320",
  "LOVERS LANE STATION": "22984",
  "MARKET CENTER STATION": "29825",
  "MEDICAL/MARKET CTR STATION": "28172",
  "MLK STATION": "32040",
  "MORRELL STATION": "16083",
  "NORTH CARROLLTON/FRANKFORD STATION": "29815",
  "NORTHLAKE COLLEGE STATION": "31088",
  "PARK LANE SPUR": "33609",
  "PARK LANE STATION": "28755",
  "PARKER ROAD STATION": "26897",
  "PEARL/ARTS DISTRICT STATION": "22752",
  "RICHLAND HILLS STATION": "28182",
  "ROYAL LANE STATION": "29819",
  "SMU/MOCKINGBIRD STATION": "22938",
  "SOUTHWEST MEDICAL DISTRICT/PARKLAND": "29826",
  "SPRING VALLEY STATION": "26672",
  "ST PAUL STATION": "22751",
  "T&P STATION": "28252",
  "TRINITY MILLS RAIL STATION": "29816",
  "TYLER VERNON STATION": "22730",
  "UNIVERSITY OF DALLAS STATION": "31084",
  "UNT DALLAS STATION": "33087",
  "VA MEDICAL CENTER STATION": "23391",
  "VICTORY STATION": "28264",
  "WALNUT HILL STATION": "26669",
  "WALNUT HILL/DENTON STATION": "29820",
  "WEST END STATION": "22749",
  "WEST IRVING STATION": "28176",
  "WESTMORELAND STATION": "15913",
  "WHITE ROCK STATION": "26652",
  "ZOO STATION": "13659"
}
stationNAMEdict = dict((v,k) for k,v in stationIDdict.items())


if __name__ == '__main__':
        app.run()
