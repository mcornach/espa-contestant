'''Utility functions to support the make_offer.py code'''import numpy as npimport osimport jsonimport pandas as pdimport datetimeclass NpEncoder(json.JSONEncoder):    def default(self, obj):        if isinstance(obj, np.integer):            return int(obj)        if isinstance(obj, np.floating):            return float(obj)        if isinstance(obj, np.ndarray):            return obj.tolist()        return json.JSONEncoder.default(self, obj)def load_json(filename, filedir='./'):    '''Find the status of your resources and of the next market configuration'''    with open(os.path.join(filedir,f'{filename}.json'), 'r') as f:        json_dict = json.load(f)    return json_dictdef split_mktid(mktid):    """Splits the market_id string into the market type and the time string (YYYYmmddHHMM)"""        split_idx = [i for i, char in enumerate(mktid) if char == '2'][0]    mkt_type = mktid[:split_idx]    start_time = mktid[split_idx:]    return mkt_type, start_time# def get_timeseries(status):#     """Takes the starting time and market config to build the time series"""#     mkt_type, start_time = split_mktid(status['market_id'])#     mkt_spec = load_json('market_specification', '../') #     for key, items in mkt_spec.items():#         if mkt_type in items.keys():#             durations = mkt_spec[key][mkt_type]['interval_durations']#     d0, d1 = durations[0][0], durations[0][1]#     times = np.zeros(d0, dtype=datetime.datetime)#     times[0] = datetime.datetime.strptime(start_time, '%Y%m%d%H%M')#     for i in range(1,d0):#         times[i] = times[i-1] + datetime.timedelta(minutes = d1)#     return timesdef get_latest_forecast():    """Loads either renewables or demand forecast"""    with open('../forecast.json', 'r') as f:        forecast = json.load(f)    demand = forecast['load']#[val for val in forecast['demand'].values()]    wind = forecast['wind']#[val for val in forecast['wind'].values()]    solar =forecast['solar'] #[val for val in forecast['solar'].values()]    renewables = wind + solar    # if ftype == 'demand':    #     df = pd.read_csv('../demand_forecast.')    #     df_times = pd.to_datetime(df['Time'].values.flatten())    #     power = df['MW'].values.flatten()    # elif ftype == 'renewables':    #     dfw = pd.read_csv('../wind_forecast.csv')    #     dfs = pd.read_csv('../solar_forecast.csv')    #     df_times = pd.to_datetime(dfw['Time'].values.flatten())    #     powerw = dfw['MW'].values.flatten()    #     powers = dfs['MW'].values.flatten()    #     power = powerw+powers    # Now check for the proper time subset (may be unnecessary if we update forecast data with    # the market timestamps)    # times = pd.to_datetime(times)    # if check_time:    #     ind_arr = np.zeros(len(times), dtype=int)    #     print(times, df_times)    #     for i in range(len(ind_arr)):    #         ind_arr[i] = np.where(df_times == times[i])[0][0]    #     power = power[ind_arr]    return demand, renewablesdef compute_offers(resources, times, demand, renewables):    """Takes the status and forecast and makes an offer dictionary"""    # Computes the ratio of renewables to demand - higher ratio means more renewables available    # ratio_ren_dem = renewables/demand    # median_ratio_rd = np.median(ratio_ren_dem)    # We will loop through keys to fill our offer out, making updates as needed    status = resources['status']    klist = list(status.keys())    my_soc = status[klist[0]]['soc']    offer_keys = ['cost_rgu', 'cost_rgd', 'cost_spr', 'cost_nsp', 'block_ch_mc', 'block_dc_mc',                   'block_soc_mc', 'block_ch_mq', 'block_dc_mq', 'block_soc_mq', 'soc_end',                   'bid_soc', 'init_en', 'init_status', 'ramp_up', 'ramp_dn', 'socmax', 'socmin',                  'soc_begin', 'eff_ch', 'eff_dc', 'chmax', 'dcmax']    offer_vals = [3, 3, 0, 0, [20, 17], [22, 27], [-20, -10, 0], [75, 50], [75, 50], [250, 50, 333.33], 133.333,                  False, 0, 0, 9999, 9999, 633.333, 133.334, my_soc, 0.9, 1, 125, 125]    # offer_vals = [3, 3, 0, 0, [22, 19.5], [27.6, 35], [36, 20], [75, 50], [75, 50], [400, 233.333], 133.334,    #               True, 0, 0, 9999, 9999, 633.333, 133.334, my_soc, 0.9, 1, 125, 125]    use_time = [True, True, True, True, True, True, True, True, True, True, False, False, False,                False, False, False, False, False, False, False, False, True, True]    offer_out = {}    for rid in status.keys():        resource_offer = {}        for i, key in enumerate(offer_keys):            if use_time[i]:                time_dict = {}                for t in times:                    time_dict[t] = offer_vals[i]            else:                time_dict = offer_vals[i]            resource_offer[key] = time_dict        offer_out[rid] = resource_offer    return offer_outdef save_offer(offer, time_step):    """Saves the offer in json format to the correct resource directory"""    # Write the data dictionary to a JSON file    # json_file = f'{mktid}.json'    if time_step != 4:        json_file = f'offer_{time_step}.json'        with open(json_file, "w") as f:            json.dump(offer, f, cls=NpEncoder, indent=4)