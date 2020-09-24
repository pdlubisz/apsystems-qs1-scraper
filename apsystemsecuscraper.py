from bs4 import BeautifulSoup
from urllib import request, error
from pvoutput import PVOutput
from time import sleep
from astral import LocationInfo, sun
import datetime
from configparser import ConfigParser


def download(url):
    try:
        page = request.urlopen(url).read()
        return page
    except:
        return None


def download_retry(url):
    retries = 5
    while retries > 0:
        page = download(url)
        if page is None:
            retries -= 1
            sleep(30)
        else:
            return page


class APSystemsECUScraper:
    def __init__(self, config=None):
        cp = ConfigParser()
        if config is not None:
            cp.read(config)
        self.ecuip = cp["ecu"].get("ecuip") or "192.168.1.2"
        self.url = 'http://{}/index.php/home'.format(self.ecuip)
        self.bs = None
        self.ecudata = {}
        self.lastexportresult = None
        self.installpoint = LocationInfo("Żuków", "Poland", timezone=cp["ecu"].get("timezone") or "Europe/Warsaw",
                                         latitude=cp["ecu"].get("latitude") or 51.145811,
                                         longitude=cp["ecu"].get("longitude") or 00.644786)

        self.pvoutputkey = cp["pvoutput"].get("apikey") or None
        self.pvoutputsystemid = cp["pvoutput"].get("systemid") or None

    def get_data(self):
        self.bs = BeautifulSoup(download_retry(self.url), 'html.parser')
        home_table = self.bs.find("table").find_all("tr")
        for row in home_table:
            value = row.find("td").text.strip()
            if value.endswith("kWh"):
                value = int(float(value[:-3]) * 1000)
            elif value.endswith("kW"):
                value = int(float(value[:-2]) * 1000)
            elif value.endswith("W"):
                value = int(value[:-1])
            elif value.endswith("Wh"):
                value = int(value[:-2])
            self.ecudata[row.find("th").text.replace(" ", "_").lower()] = value
        # {'ecu_id': '1111111', 'lifetime_generation': 11010, 'last_system_power': 15, 'generation_of_current_day': 8610, 'last_connection_to_website': '2020-01-15 18:50:17', 'number_of_inverters': '2', 'last_number_of_inverters_online': '2', 'current_software_version': 'C2.1', 'current_time_zone': 'Europe/Warsaw', 'ecu_eth0_mac_address': '10:97:1B:01:00:00', 'ecu_wlan0_mac_address': '10:12:48:76:56:A5'}

    def export_status_data_to_pvoutput(self, whenlight=True):
        if whenlight:
            rightnow = datetime.datetime.utcnow()
            dusk = sun.dusk(self.installpoint.observer, date=datetime.datetime.utcnow())
            dawn = sun.dawn(self.installpoint.observer, date=datetime.datetime.utcnow())
            if not (rightnow > dawn.replace(tzinfo=None) and rightnow < dusk.replace(tzinfo=None) + datetime.timedelta(hours=1)) :
                return False
        self.pv = PVOutput(apikey=self.pvoutputkey, systemid=int(self.pvoutputsystemid))
        data_to_send = {
            "c1": 1,
            "v1": self.ecudata["generation_of_current_day"],
            "v2": self.ecudata["last_system_power"]
        }
        result = self.pv.addstatus(data=data_to_send)
        return result
