import requests
import os
import json
import logging
from datetime import datetime
from ali_oss import get_temp_url

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

dir = os.environ
key = dir.get('APP_KEY')
loc = dir.get('LOC')
chan = dir.get('CHAN')


location_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}&gzip=y"
live_weather = "https://devapi.qweather.com/v7/weather/now?location={}&key={}&gzip=y"
three_days_weather = "https://devapi.qweather.com/v7/weather/3d?location={}&key={}&gzip=y"
seven_days_weather = "https://devapi.qweather.com/v7/weather/7d?location={}&key={}&gzip=y"
twentyFour_hours_weather = "https://devapi.qweather.com/v7/weather/24h?location={}&key={}&gzip=y"
serverChan_url = "https://sc.ftqq.com/{}.send"



class Weather:
    def __init__(self):
        self.__location_url = location_url.format(loc, key)
        self.__live_weather = live_weather.format(loc, key)
        self.__three_days_weather = three_days_weather.format(loc, key)
        self.__seven_days_weather = seven_days_weather.format(loc, key)
        self.__twentyFour_hours_weather = twentyFour_hours_weather.format(loc, key)
        self.__serverChan_url = serverChan_url.format(chan)
        self.__kind = 's1_color/{}.png'

    def __request_API(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            logging.error("请求API失败，响应吗为：" + str(response.status_code))
        else:
            return json.loads(response.text, encoding='utf-8')

    def __post_to_serverChan(self, title, data):
        post_body = {'text':title, 'desp':data}
        response = requests.post(self.__serverChan_url, data=post_body)
        response_json = json.loads(response.text)
        if response_json.get('errno') != 0:
            logger.error("发送数据到serverChan出错，错误信息：" + response_json.get('errmsg'))
        else:
            logger.info('数据推送成功！')


    def __get_live_weather(self):
        weather = self.__request_API(self.__live_weather)
        if weather.get("code") != '200':
            logging.error("请求实时天气API错误，错误码为：" + weather.get("code"))
        else:
            logging.info("实时天气数据请求成功！更新时间为：" + weather.get("updateTime"))
            return weather
    
    def __get_three_days_weather(self):
        weather = self.__request_API(self.__three_days_weather)
        if weather.get("code") != '200':
            logging.error("请求实时天气API错误，错误码为：" + weather.get("code"))
        else:
            logging.info("3天天气数据请求成功！更新时间为：" + weather.get("updateTime"))
            return weather

    def __get_seven_days_weather(self):
        weather = self.__request_API(self.__seven_days_weather)
        if weather.get("code") != '200':
            logging.error("请求实时天气API错误，错误码为：" + weather.get("code"))
        else:
            logging.info("7天天气数据请求成功！更新时间为：" + weather.get("updateTime"))
            return weather

    def __get_hours_weather(self):
        weather = self.__request_API(self.__twentyFour_hours_weather)
        if weather.get("code") != '200':
            logging.error("请求实时天气API错误，错误码为：" + weather.get("code"))
        else:
            logging.info("24小时天气数据请求成功！更新时间为：" + weather.get("updateTime"))
            return weather

    def _print_seven_days_info(self, data):
        str = "| 日期 | 白天天气 | 气温  | 晚间天气 | 风力 | 湿度 | 紫外线强度 |\n| ---------- | ------------------------------------------------------------ | ----- | ------------------------------------------------------------ | ---- | ---- | ---------- |\n"
        seven_days = data.get("daily")
        cache = {}
        for i in seven_days:
            date = i['fxDate']
            if i['iconDay'] in cache:
                day = cache[i['iconDay']]
            else:
                day = get_temp_url(self.__kind.format(i['iconDay']))
                cache[i['iconDay']] = day
            temp = '{}℃-{}℃'.format(i['tempMin'], i['tempMax'])
            if i['iconNight'] in cache:
                night = cache[i['iconNight']]
            else:
                night = get_temp_url(self.__kind.format(i['iconNight']))
                cache[i['iconNight']] = night
            wind = i['windDirDay']
            sd = '{}%'.format(i['humidity'])
            zwx = i['uvIndex']
            str += '| {date} |![]({day})| {temp} |![]({night})| {wind} | {sd} | {zwx} |\n'.format(date = date, day = day, temp = temp, night = night, wind = wind, sd = sd, zwx = zwx)
        return str


    def _print_daily_info(self, today):
        str = '| 时间 | 天气 | 天气 | 气温 | 降雨概率 |\n| ---- | ---- | ---- | ---- | -------- |\n'
        hours_object = today.get('hourly')
        cache = {}
        for i in hours_object:
            time = i['fxTime'][-11:-6]
            temp = i['temp']
            if i['icon'] in cache:
                weather_icon = cache[i['icon']]
            else:
                weather_icon = get_temp_url(self.__kind.format(i['icon']))
                cache[i['icon']] = weather_icon
            print(weather_icon)
            weather = i['text']
            rain = i['pop']
            str += '| {time} |![]({weather_icon})| {weather} | {temp}℃ | {rain}% |\n'.format(time = time, weather_icon = weather_icon, weather = weather, temp = temp, rain = rain)
        return str 
            
        


    def work(self):
        dayOfWeek = datetime.now().isoweekday()

        if dayOfWeek == 1:
            #周一获取一周天气
            data = self.__get_seven_days_weather()
            result = self._print_seven_days_info(data)
            self.__post_to_serverChan('7天天气预报', result)
        else:
            #平常24小时
            today = self.__get_hours_weather()
            result = self._print_daily_info(today)
            self.__post_to_serverChan('24小时天气预报', result)
