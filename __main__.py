import os
import sys
import time
import logging
import datetime
import requests
import json
import random
import spidev as SPI
from PIL import Image, ImageDraw, ImageFont
import asyncio
from lib import LCD_2inch
from dotenv import load_dotenv
from gpiozero import Button
button = Button(2)

load_dotenv()

selectedStation = 'GC'
rotateStations = True

def get_next_train(api_url, headers, platform):
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        station_name = data.get('Name', 'Unknown Station')
        first_train = None
        second_train = None

        for service in data['services']:
            if service['Destinations']['Front']['TIPLOC'] == selectedStation:
                continue
            if service['Platform'] == platform:
                if first_train is None:
                    first_train = service
                else:
                    second_train = service
                    break
        
        return first_train, second_train, station_name
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None, None, None

def update_display(disp, train, matrixFont, x_position, station_name, matrixFontSmaller, secondTrain):
    destination_text = train['Destinations']['Front']['Name']
    destinationTerminating_text = train['Origins']['Front']['Name']
    platform = train['Platform']
    status_text = train['ArrStatus']
    if status_text == "Exp":
        status_text = train['ETA']
    if secondTrain:
        secondTrainTime = secondTrain['Destinations']['Front']['STA']
        secondTrainDestination = secondTrain['Destinations']['Front']['Name']

    # Scrolling text settings
    calling_at_text = ""
    if 'CallingPoints' in train:
        calling_at_text = "Calling at: " + ", ".join([point['Name'] for point in train['CallingPoints']['Front']])
    elif destination_text == station_name:
        calling_at_text = "Terminating here"
    else:
        calling_at_text = "Calling at: None"
        
    text_bbox = ImageDraw.Draw(Image.new("RGB", (0, 0))).textbbox((0, 0), calling_at_text, font=matrixFont)
    text_width = text_bbox[2] - text_bbox[0]

    # Create blank image for drawing
    image1 = Image.new("RGB", (disp.height, disp.width), "BLACK")
    draw = ImageDraw.Draw(image1)
    draw.text((170, 20), "Platform " + platform, fill="ORANGE", font=matrixFont)
    
    # Get current time
    now = datetime.datetime.now()
    draw.text((10, 20), f"{now.hour:02}:{now.minute:02}:{now.second:02}", fill="ORANGE", font=matrixFont)
    if destination_text == station_name:
        draw.text((10, 70), destinationTerminating_text, fill="ORANGE", font=matrixFont)
    else:
        draw.text((10, 70), destination_text, fill="ORANGE", font=matrixFont)

    status_text_bbox = draw.textbbox((0, 0), status_text, font=matrixFont)
    status_text_text_width = status_text_bbox[2] - status_text_bbox[0]
    status_text_x = 310 - status_text_text_width
    draw.text((status_text_x, 70), status_text, fill="ORANGE", font=matrixFont)
    draw.text((10, 210), station_name, fill="ORANGE", font=matrixFontSmaller)

    draw.text((x_position, 120), calling_at_text, fill="ORANGE", font=matrixFont)

    if secondTrain:
        draw.text((10, 165), secondTrainTime, fill="ORANGE", font=matrixFont)
        second_train_bbox = draw.textbbox((0, 0), secondTrainDestination, font=matrixFont)
        second_train_text_width = second_train_bbox[2] - second_train_bbox[0]
        second_train_x = 310 - second_train_text_width
        draw.text((second_train_x, 165), secondTrainDestination, fill="ORANGE", font=matrixFont)

    x_position -= 10 + (text_width / 50)
    if x_position < -text_width:
        x_position = disp.width
    image1 = image1.rotate(0)
    disp.ShowImage(image1)

    return x_position

async def main():
    global selectedStation
    api_url = "https://tiger-api-portal.worldline.global/services/" + selectedStation
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "x-api-key": "JsfAqhmRuO88ndFxs6VG47Z5dXRB8YZB7Dy4xWXN",
        "x-amz-date": "20240312T191852+0000",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Access-Control-Allow-Origin,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
    }

    consecutive_failures = 0

    stations = {
        "AD": {"name": "Adelaide", "totalPlatforms": 2},
        "AN": {"name": "Antrim", "totalPlatforms": 3},
        "BC": {"name": "Ballycarry", "totalPlatforms": 1},
        "BA": {"name": "Ballymena", "totalPlatforms": 2},
        "BY": {"name": "Ballymoney", "totalPlatforms": 2},
        "BL": {"name": "Balmoral", "totalPlatforms": 2},
        "BR": {"name": "Bangor", "totalPlatforms": 3},
        "BW": {"name": "Bangor West", "totalPlatforms": 2},
        "BN": {"name": "Bellarena", "totalPlatforms": 2},
        "BT": {"name": "Botanic", "totalPlatforms": 2},
        "CA": {"name": "Carnalea", "totalPlatforms": 2},
        "CS": {"name": "Carrickfergus", "totalPlatforms": 3},
        "CK": {"name": "Castlerock", "totalPlatforms": 1},
        "CH": {"name": "City Hospital", "totalPlatforms": 2},
        "CP": {"name": "Clipperstown", "totalPlatforms": 2},
        "CE": {"name": "Coleraine", "totalPlatforms": 3},
        "CY": {"name": "Cullybackey", "totalPlatforms": 1},
        "CT": {"name": "Cultra", "totalPlatforms": 2},
        "DH": {"name": "Derriaghy", "totalPlatforms": 2},
        "DV": {"name": "Dhu Varren", "totalPlatforms": 1},
        "DP": {"name": "Downshire", "totalPlatforms": 2},
        "DG": {"name": "Drogheda", "totalPlatforms": 3},
        "DN": {"name": "Dublin Connolly", "totalPlatforms": 5},
        "DK": {"name": "Dundalk", "totalPlatforms": 2},
        "DM": {"name": "Dunmurry", "totalPlatforms": 2},
        "FY": {"name": "Finaghy", "totalPlatforms": 2},
        "GC": {"name": "Belfast Grand Central", "totalPlatforms": 8, "showNext": True},
        "GN": {"name": "Glynn", "totalPlatforms": 1},
        "GV": {"name": "Great Victoria St", "totalPlatforms": 4},
        "GD": {"name": "Greenisland", "totalPlatforms": 2},
        "HB": {"name": "Helen's Bay", "totalPlatforms": 2},
        "HD": {"name": "Hilden", "totalPlatforms": 2},
        "HW": {"name": "Holywood", "totalPlatforms": 2},
        "JN": {"name": "Jordanstown", "totalPlatforms": 2},
        "LG": {"name": "Lambeg", "totalPlatforms": 2},
        "CL": {"name": "Lanyon Place", "totalPlatforms": 4, "showNext": True},
        "LR": {"name": "Larne Harbour", "totalPlatforms": 2},
        "LN": {"name": "Larne Town", "totalPlatforms": 1},
        "LB": {"name": "Lisburn", "totalPlatforms": 3},
        "LY": {"name": "Londonderry", "totalPlatforms": 2},
        "LU": {"name": "Lurgan", "totalPlatforms": 2},
        "MM": {"name": "Magheramorne", "totalPlatforms": 1},
        "MO": {"name": "Marino", "totalPlatforms": 2},
        "MR": {"name": "Moira", "totalPlatforms": 2},
        "MW": {"name": "Mossley West", "totalPlatforms": 1},
        "NY": {"name": "Newry", "totalPlatforms": 3},
        "PD": {"name": "Portadown", "totalPlatforms": 3},
        "PH": {"name": "Portrush", "totalPlatforms": 3},
        "PS": {"name": "Poyntzpass", "totalPlatforms": 2},
        "SA": {"name": "Scarva", "totalPlatforms": 2},
        "SL": {"name": "Seahill", "totalPlatforms": 2},
        "SY": {"name": "Sydenham", "totalPlatforms": 2},
        "BE": {"name": "Titanic Quarter", "totalPlatforms": 2},
        "TE": {"name": "Trooperslane", "totalPlatforms": 2},
        "UV": {"name": "University", "totalPlatforms": 1},
        "WY": {"name": "Whiteabbey", "totalPlatforms": 2},
        "WT": {"name": "Whitehead", "totalPlatforms": 2},
        "YG": {"name": "York Street", "totalPlatforms": 2}
    }

    logging.basicConfig(level=logging.DEBUG)
    currentPlatform = 1

    try:
        disp = LCD_2inch.LCD_2inch()
        disp.Init()
        disp.clear()
        disp.bl_DutyCycle(100) # Set the backlight to 100
        matrixFont = ImageFont.truetype("font/DotMatrixRegular.ttf", 32)
        matrixFontSmaller = ImageFont.truetype("font/DotMatrixRegular.ttf", 24)

        splashScreen = Image.new("RGB", (disp.height, disp.width), "BLACK")
        draw = ImageDraw.Draw(splashScreen)
        draw.text((10, 100), "Fetching train data...", fill="ORANGE", font=matrixFont)
        splashScreen = splashScreen.rotate(0)
        disp.ShowImage(splashScreen)
        x_position = disp.width

        last_credential_time = datetime.datetime.now()
        last_random_station = datetime.datetime.now()

        train, secondTrain, currentStation = get_next_train(api_url, headers, str(currentPlatform))
        last_fetch_time = datetime.datetime.now()

        while True:
            current_time = datetime.datetime.now()

            if ((current_time - last_random_station).seconds >= 830 and rotateStations) or button.is_pressed:
                random_station_code = random.choice(list(stations.keys()))
                selectedStation = random_station_code
                last_random_station = current_time
                currentPlatform = 1
                api_url = "https://tiger-api-portal.worldline.global/services/" + selectedStation
                
                consecutive_failures = 0
                last_fetch_time = current_time
                train, secondTrain, currentStation = get_next_train(api_url, headers, str(currentPlatform))
                if train:
                    x_position = update_display(disp, train, matrixFont, x_position, currentStation, matrixFontSmaller, secondTrain)
                print("Selecting random station:", selectedStation, random_station_code)

            if (current_time - last_fetch_time).seconds >= 60 or not train:
                if not train:
                    consecutive_failures += 1
                    station_info = stations.get(selectedStation, {})
                    total_platforms = station_info.get("totalPlatforms", 0)
                    print(f"No trains at platform {currentPlatform} currently.")
                    if consecutive_failures >= total_platforms + 1:
                        image2 = Image.new("RGB", (disp.height, disp.width), "BLACK")
                        draw = ImageDraw.Draw(image2)
                        station_name = station_info.get("name", "Unknown Station")
                        draw.text((10, 100), "No trains at current station:", fill="ORANGE", font=matrixFontSmaller)
                        draw.text((10, 120), station_name, fill="ORANGE", font=matrixFontSmaller)
                        image2 = image2.rotate(0)
                        disp.ShowImage(image2)
                        time.sleep(5)
                else:
                    consecutive_failures = 0
                currentPlatform += 1
                station_info = stations.get(selectedStation, {})
                total_platforms = station_info.get("totalPlatforms", 0)
                if currentPlatform > total_platforms:
                    currentPlatform = 1
                train, secondTrain, currentStation = get_next_train(api_url, headers, str(currentPlatform))
                last_fetch_time = current_time

            if train:
                x_position = update_display(disp, train, matrixFont, x_position, currentStation, matrixFontSmaller, secondTrain)

            logging.info("Display updated")
            
    except IOError as e:
        logging.info(e)
    except KeyboardInterrupt:
        disp.module_exit()
        logging.info("quit:")
        exit()

if __name__ == "__main__":
    asyncio.run(main())
