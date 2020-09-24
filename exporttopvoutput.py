#!/usr/bin/env python3

from apsystemsecuscraper import APSystemsECUScraper

ap = APSystemsECUScraper('config.ini')
ap.get_data()
if ap.ecudata:
    ap.export_status_data_to_pvoutput()