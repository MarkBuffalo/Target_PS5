import json
import requests
import webbrowser
import time
import sched
import simpleaudio as sa


class ScanTargetApi:
    def __init__(self):
        self.api_key = "ff457966e64d5e877fdbad070f276d18ecec4a01"
        self.prod_id = 81114596
        self.prod_name = "Digital ps5"
        self.result_limit = 1000
        self.search_radius = 1100
        self.num_results = 0
        self.interval = 15
        self.audio_file = "loud_alarm.wav"
        # These zip codes are stragetically placed to cover the entire United States at a radius of 1,100 miles.
        self.zip_codes = [
         94203, # Sacramento, California
         64030, # Kansas City, Missouri
         20001, # Washington D.C.
         33101, # Miami, Florida

        # 77001, # Houston
        # 79835, # El Paso
        # 75501, # Texarkana
        # 73008, # Oklahoma City, Oklahoma
        ]

    def start_search(self, scheduler):
        self.num_results = 0
        for z in self.zip_codes:
            self.query_api(z)
        print(f"Searched {self.num_results} stores for {self.prod_name}... {time.ctime()}")
        s.enter(self.interval, 1, self.start_search, (scheduler,))


    def query_api(self, zip_code):

        r = requests.get(f"https://api.target.com/fulfillment_aggregator/v1/fiats/{self.prod_id}?key={self.api_key}"
                         f"&nearby={zip_code}"
                         f"&limit={self.result_limit}&requested_quantity=1"
                         f"&radius={self.search_radius}")

        if len(r.text) > 0:
            self.print_results(json.loads(r.text))
        else:
            print("Query returned no results")

    def print_results(self, text):
        locations = text.get("products")[0].get("locations")
        for loc in locations:
            if type(loc) == dict:
                store_name = loc.get("store_name")
                store_address = loc.get("store_address")
                distance = loc.get("distance")
                location_id = loc.get("location_id")
                curbside = loc.get("curbside").get("availability_status")
                order_pickup = loc.get("order_pickup").get("availability_status")
                location_available_to_promise_quantity = loc.get("location_available_to_promise_quantity")
                ship_to_store = loc.get("ship_to_store").get("availability_status")
                in_store_only = loc.get("in_store_only").get("availability_status")
                zipcode = store_address.split('-')[0].split(' ')[-1]
                num_found = 0

                if "NOT_SOLD_IN_STORE" not in in_store_only:
                    if "UNAVAILABLE" not in curbside and "UNAVAILABLE" not in ship_to_store:
                        print(f"Found at store in zip code {zipcode}")
                        self.open_site(f"https://www.target.com/p/playstation-5-digital-edition-console/-/A-{self.prod_id}#lnk=sametab")
                        print("\t".join([store_name, store_address, curbside, ship_to_store, in_store_only]))
                        num_found += 1
                    # else:
                        # print(f"Not found at {zipcode}...")
                        # print(f"Nope: {store_name}: {store_address}: {curbside}, {ship_to_store}, {in_store_only}")
            self.num_results += 1

    def open_site(self, url):
        try:
            wave_obj = sa.WaveObject.from_wave_file(self.audio_file)
            play_obj = wave_obj.play()
        except Exception:
            print("Couldn't play a sound. This script hates you. Contact author.")

        try:
            webbrowser.open(url)
        except Exception:
            print("Couldn't open a web browser. This script hates you. Contact author.")


if __name__ == "__main__":
    print("A sound will play and the link will open once there is stock available")
    search = ScanTargetApi()

    # get run options
    # 0: Digital
    # 1: Non-Digital
    # 2: Both
    prod_type = input("Options:\n\t(0) Digital\n\t(1) Non-Digital\n\t(2) Both\n:")
    while prod_type != "0" and prod_type != "1" and prod_type != "2":
        prod_type = input("Invalid option!\nOptions:\n\t(0) Digital\n\t(1) Non-Digital\n\t(2) Both\n:")
    if prod_type == "1":
        # set to non-digital product id
        search.prod_id = 81114595
        search.prod_name = "Non-Digital ps5"

    s = sched.scheduler(time.time, time.sleep)
    s.enter(1, 1, search.start_search, (s,))

    # generate second object to query non-digital
    if prod_type == "2":
        search2 = ScanTargetApi()
        # set to non-digital product id
        search2.prod_id = 81114595
        search2.prod_name = "Non-Digital ps5"
        s.enter(1, 1, search2.start_search, (s,))

    s.run()
