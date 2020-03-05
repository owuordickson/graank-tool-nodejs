# -*- coding: utf-8 -*-
"""
@author: "Dickson Owuor"
@credits: "Anne Laurent and Joseph Orero"
@license: "MIT"
@version: "1.0"
@email: "owuordickson@gmail.com"
@created: "09 December 2019"

"""
import csv
import time
import multiprocessing as mp
from dateutil.parser import parse

from datetime import datetime
import numpy as np
import skfuzzy as fuzzy

import sys
from io import StringIO
import json


class DataStream:

    def __init__(self, _id, r_data, allow_char, cores):
        self.id = _id
        self.path = r_data[0]
        self.allow_char = allow_char
        self.cores = cores
        self.raw_data = r_data  # DataStream.read_csv(path)
        if len(self.raw_data) == 0:
            # print("csv file read error")
            raise Exception("Unable to read csv file: " + path)
        else:
            self.data = self.raw_data
            self.titles = self.get_titles()
            self.time_col = False
            self.allowed_cols, self.timestamps = self.init_ds()
            self.fetched_tuples = list()

    def get_titles(self):
        data = self.raw_data
        if data[0][0].replace('.', '', 1).isdigit() or data[0][0].isdigit():
            return False
        else:
            if data[0][1].replace('.', '', 1).isdigit() or data[0][1].isdigit():
                return False
            else:
                titles = []
                for i in range(len(data[0])):
                    # sub = [str(i+1), data[0][i]]
                    sub = str(data[0][i])
                    titles.append(sub)
                del self.data[0]
                return titles

    def init_ds(self):
        data = self.data
        # test for time from any row
        t_index, allowed_cols = self.test_ds_data(data[1])
        if t_index is None:
            raise Exception("No time found in file: " + str(self.path))
            # return False
        else:
            self.time_col = t_index
            if self.cores > 0:
                # fetch timestamp from every row through parallel processors
                size = len(data)
                tasks = range(size)
                pool = mp.Pool(self.cores)
                timestamps = pool.map(self.get_time_stamp, tasks)
            else:
                timestamps = list()
                size = len(data)
                for i in range(size):
                    t_stamp = self.get_time_stamp(i)
                    timestamps.append(t_stamp)
            timestamps.sort()
            allowed_cols.sort()
            # print("Finished fetching timestamps")
        return allowed_cols, timestamps

    def get_time_stamp(self, i):
        # print("fetching time stamp")
        row = self.data[i]
        t_value = row[self.time_col]
        time_ok, t_stamp = DataStream.test_time(t_value)
        if time_ok:
            return t_stamp
        else:
            raise Exception(str(t_value) + ' : time is invalid for ' + str(self.path))

    def test_ds_data(self, row):
        # print("testing data stream data")
        time_index = None
        allowed_cols = list()
        size = len(row)
        for col_index in range(size):
            col_value = row[col_index]
            time_ok, t_stamp = DataStream.test_time(col_value)
            if time_ok:
                # return col_index, t_stamp
                if time_index is None:
                    time_index = col_index
            else:
                # continue
                # test for digits
                if self.allow_char:
                    allowed_cols.append(col_index)
                else:
                    if col_value.replace('.', '', 1).isdigit() or col_value.isdigit():
                        allowed_cols.append(col_index)
        return time_index, allowed_cols

    @staticmethod
    def test_time(date_str):
        # add all the possible formats
        try:
            if type(int(date_str)):
                return False, False
        except ValueError:
            try:
                if type(float(date_str)):
                    return False, False
            except ValueError:
                try:
                    date_time = parse(date_str)
                    t_stamp = time.mktime(date_time.timetuple())
                    return True, t_stamp
                except ValueError:
                    # raise ValueError('Python Error: no valid date-time format found')
                    return False, False

    @staticmethod
    def read_csv(file_str):
        # 1. retrieve data-set from file
        f = StringIO(file_str)
        # with open(file_path, 'r') as f:
        dialect = csv.Sniffer().sniff(f.readline(), delimiters=";,' '\t")
        f.seek(0)
        reader = csv.reader(f, dialect)
        temp = list(reader)
        f.close()
        return temp


#----------------------------------------------


class FuzzTX:
    # allow user to upload multiple csv files

    def __init__(self, file_paths, allow_char, cores, allow_para):
        self.f_paths = FuzzTX.test_paths(file_paths)
        if len(self.f_paths) >= 2:
            if allow_char == 0:
                self.allow_char = False
            else:
                self.allow_char = True

            self.cores = cores

            if allow_para == 0:
                self.allow_parallel = False
            else:
                self.allow_parallel = True

            try:
                self.d_streams = self.get_data_streams()
                self.size = self.get_size()
                self.col_size = 0
                self.boundaries = []
                # self.data_streams, self.time_list = self.get_observations()
                # print("data streams fetched")
            except Exception as error:
                raise Exception("CSV Error: "+str(error))
        else:
            raise Exception("Python Error: less than 2 csv files picked")

    def get_size(self):
        size = len(self.d_streams)
        return size

    def get_data_streams(self):
        list_ds = list()
        size = len(self.f_paths)
        for i in range(size):
            path = self.f_paths[i]
            if self.allow_parallel:
                ds = DataStream(i, path, self.allow_char, self.cores)
            else:
                ds = DataStream(i, path, self.allow_char, 0)
            list_ds.append(ds)
        return list_ds

    def cross_data(self):
        # print("starting crossing")
        d_streams = self.d_streams
        boundaries, extremes = self.get_boundaries()
        self.boundaries = boundaries

        title_tuple = list()
        # add x_data title tuple
        title_tuple.append("timestamp")  # add title for approximated timestamp
        for ds in d_streams:
            titles = ds.titles
            allowed_cols = ds.allowed_cols
            size = len(titles)
            for i in range(size):
                if i in allowed_cols:
                    title_tuple.append(titles[i])

        self.col_size = len(title_tuple)
        arr_slice = list(np.arange(boundaries[1], extremes[1], extremes[2]))
        if np.array(arr_slice).max() < extremes[1]:
            arr_slice.append(extremes[1])

        if self.allow_parallel:
            # fetch value tuples through parallel processors
            pool = mp.Pool(self.cores)
            x_data = pool.map(self.slide_timestamp, arr_slice)
        else:
            x_data = list()
            for _slice in arr_slice:
                temp_tuple = self.slide_timestamp(_slice)
                x_data.append(temp_tuple)
        x_data = list(filter(bool, x_data))
        x_data.sort()
        x_data.insert(0, title_tuple)
        # print("Finished crossing")
        return x_data

    def get_boundaries(self):
        min_time = 0
        max_time = 0
        max_diff = 0
        max_boundary = []
        # list_boundary = list()
        # for item in self.time_list:
        for ds in self.d_streams:
            arr_stamps = ds.timestamps
            min_stamp, max_stamp, min_diff = FuzzTX.get_min_diff(arr_stamps)
            # boundary = [(min_stamp - min_diff), min_stamp, (min_stamp + min_diff)]
            # list_boundary.append(boundary)
            if (max_diff == 0) or (min_diff > max_diff):
                max_diff = min_diff
                max_boundary = [(min_stamp - min_diff), min_stamp, (min_stamp + min_diff)]
            if (min_time == 0) or (min_stamp < min_time):
                min_time = min_stamp
            if (max_time == 0) or (max_stamp > max_time):
                max_time = max_stamp
        extremes = [min_time, max_time, max_diff]
        return max_boundary, extremes

    def slide_timestamp(self, _slice):
        _slice -= self.boundaries[1]  # slice is one step bigger
        new_bounds = [x + _slice for x in self.boundaries]
        boundaries = new_bounds
        arr_index = self.approx_fuzzy_index(boundaries)
        # print(arr_index)
        if arr_index:
            temp_tuple = self.fetch_x_tuples(boundaries[1], arr_index)
            if temp_tuple and len(temp_tuple) == self.col_size:
                return temp_tuple
        return False

    def approx_fuzzy_index(self, boundaries):
        tuple_indices = list()
        # for pop in all_pop:
        for ds in self.d_streams:
            pop = ds.timestamps
            # for each boundary, find times with highest memberships for each dataset
            memberships = fuzzy.membership.trimf(np.array(pop), np.array(boundaries))
            if np.count_nonzero(memberships) > 0:
                index = memberships.argmax()
                var_index = [ds.id, index]
                tuple_indices.append(var_index)
                # tuple_indices.append(index)
                # print(memberships)
            else:
                return False
        return tuple_indices

    def fetch_x_tuples(self, time, arr_index):
        temp_tuple = list()
        temp_tuple.append(str(datetime.fromtimestamp(time)))
        all_ds = self.get_size()
        # for ds in self.d_streams:
        for j in range(all_ds):
            ds = self.d_streams[j]
            for item in arr_index:
                if (ds.id == item[0]) and (item[1] not in ds.fetched_tuples):
                    var_row = ds.data[item[1]]
                    self.d_streams[j].fetched_tuples.append(item[1])
                    size = len(var_row)
                    allowed_cols = ds.allowed_cols
                    for i in range(size):
                        if i in allowed_cols:
                            var_col = var_row[i]
                            temp_tuple.append(var_col)
                    break
        if len(temp_tuple) > 1:
            return temp_tuple
        else:
            return False

    @staticmethod
    def get_min_diff(arr):
        arr_pop = np.array(arr)
        arr_diff = np.abs(np.diff(arr_pop))
        min_stamp = arr_pop.min()
        max_stamp = arr_pop.max()
        min_diff = arr_diff.min()
        return min_stamp, max_stamp, min_diff

    @staticmethod
    def test_paths(path_str):
        # path_list = [x.strip() for x in path_str.split(',')]
        #for path in path_list:
        #    if path == '':
        #        path_list.remove(path)
        #return path_list
        file_list = []
        raw_data = json.loads(path_str)
        for item in raw_data:
            temp_list = []
            temp_list.append(list(item["data"][0].keys()))
            for obj in item["data"]:
                row = []
                for key, value in obj.items():
                    row.append(value)
                temp_list.append(row)
            file_list.append(temp_list)
        return file_list

    @staticmethod
    def write_csv(csv_data, name='x_data'):
        # now = datetime.now()
        # stamp = int(datetime.timestamp(now))
        #path = name + str(stamp) + str('.csv')
        output = StringIO()
        #with open(path, 'w') as f:
        writer = csv.writer(output)
        writer.writerows(csv_data)
        return output.getvalue()
        #f.close()

    @staticmethod
    def write_file(data, path):
        with open(path, 'w') as f:
            f.write(data)
            f.close()


#-------------------------------------------------------

#------ main program -----------------------------------

def init_algorithm(allow_char, f_files, cores, allow_para):
    try:
        obj = FuzzTX(f_files, allow_char, cores, allow_para)
        x_data = obj.cross_data()
        x_file = FuzzTX.write_csv(x_data)
        print(x_file)
        sys.stdout.flush()
        # return wr_line
    except Exception as error:
        wr_line = "Failed: " + str(error)
        print({"success": 0, "pyload": wr_line})
        sys.stdout.flush()
        # return wr_line


req_files = sys.argv[1]
init_algorithm(0, req_files, 2, 0)
