# -*- coding: utf-8 -*-
"""
@author: "Dickson Owuor"
@credits: "Thomas Runkler, Edmond Menya, and Anne Laurent,"
@license: "MIT"
@version: "1.0"
@email: "owuordickson@gmail.com"
@created: "16 March 2020"

"""

import numpy as np
import skfuzzy as fuzzy

import numpy as np
import random as rand

import csv
import json
from dateutil.parser import parse
import time

import multiprocessing as mp
import sys


class FuzzyMF:

    @staticmethod
    def init_fuzzy_support(test_members, all_members, minsup):
        boundaries, extremes = FuzzyMF.get_membership_boundaries(all_members)
        value, sup = FuzzyMF.approximate_fuzzy_support(minsup, test_members, boundaries, extremes)
        return value, sup

    @staticmethod
    def get_membership_boundaries(members):
        # 1. Sort the members in ascending order
        members.sort()

        # 2. Get the boundaries of membership function
        min_ = np.min(members)
        q_1 = np.percentile(members, 25)  # Quartile 1
        med = np.percentile(members, 50)
        q_3 = np.percentile(members, 75)
        max_ = np.max(members)
        boundaries = [q_1, med, q_3]
        extremes = [min_, max_]
        return boundaries, extremes

    @staticmethod
    def approximate_fuzzy_support(minsup, timelags, orig_boundaries, extremes):
        slice_gap = (0.1 * int(orig_boundaries[1]))
        sup = sup1 = 0
        slide_left = slide_right = expand = False
        sample = np.percentile(timelags, 50)

        a = orig_boundaries[0]
        b = b1 = orig_boundaries[1]
        c = orig_boundaries[2]
        min_a = extremes[0]
        max_c = extremes[1]
        boundaries = np.array(orig_boundaries)
        time_lags = np.array(timelags)

        while sup <= minsup:
            if sup > sup1:
                sup1 = sup
                b1 = b

            # Calculate membership of frequent path
            memberships = fuzzy.membership.trimf(time_lags, boundaries)

            # Calculate support
            sup = FuzzyMF.calculate_support(memberships)

            if sup >= minsup:
                value = FuzzyMF.get_time_format(b)
                return value, sup
            else:
                if not slide_left:
                    # 7. Slide to the left to change boundaries
                    # if extreme is reached - then slide right
                    if sample <= b:
                        # if min_a >= b:
                        a = a - slice_gap
                        b = b - slice_gap
                        c = c - slice_gap
                        boundaries = np.array([a, b, c])
                    else:
                        slide_left = True
                elif not slide_right:
                    # 8. Slide to the right to change boundaries
                    # if extreme is reached - then slide right
                    if sample >= b:
                        # if max_c <= b:
                        a = a + slice_gap
                        b = b + slice_gap
                        c = c + slice_gap
                        boundaries = np.array([a, b, c])
                    else:
                        slide_right = True
                elif not expand:
                    # 9. Expand quartiles and repeat 5. and 6.
                    a = min_a
                    b = orig_boundaries[1]
                    c = max_c
                    boundaries = np.array([a, b, c])
                    slide_left = slide_right = False
                    expand = True
                else:
                    value = FuzzyMF.get_time_format(b1)
                    return value, False

    @staticmethod
    def calculate_support(memberships):
        support = 0
        if len(memberships) > 0:
            sup_count = 0
            total = len(memberships)
            for member in memberships:
                # if float(member) > 0.5:
                if float(member) > 0:
                    sup_count = sup_count + 1
            support = sup_count / total
        return support

    @staticmethod
    def get_time_format(value):
        if value < 0:
            sign = "-"
        else:
            sign = "+"
        p_value, p_type = FuzzyMF.round_time(abs(value))
        p_format = [sign, p_value, p_type]
        return p_format

    @staticmethod
    def round_time(seconds):
        years = seconds / 3.154e+7
        months = seconds / 2.628e+6
        weeks = seconds / 604800
        days = seconds / 86400
        hours = seconds / 3600
        minutes = seconds / 60
        if int(years) <= 0:
            if int(months) <= 0:
                if int(weeks) <= 0:
                    if int(days) <= 0:
                        if int(hours) <= 0:
                            if int(minutes) <= 0:
                                return seconds, "seconds"
                            else:
                                return minutes, "minutes"
                        else:
                            return hours, "hours"
                    else:
                        return days, "days"
                else:
                    return weeks, "weeks"
            else:
                return months, "months"
        else:
            return years, "years"

    @staticmethod
    def calculate_time_lag(indices, time_diffs, minsup):
        time_lags = FuzzyMF.get_time_lags(indices, time_diffs)
        time_lag, sup = FuzzyMF.init_fuzzy_support(time_lags, time_diffs, minsup)
        if sup >= minsup:
            msg = ("~ " + time_lag[0] + str(time_lag[1]) + " " + str(time_lag[2]) + " : " + str(sup))
            return msg
        else:
            return False

    @staticmethod
    def get_patten_indices(D):
        indices = []
        t_rows = len(D)
        t_columns = len(D[0])
        for r in range(t_rows):
            for c in range(t_columns):
                if D[c][r] == 1:
                    index = [r, c]
                    indices.append(index)
        return indices

    @staticmethod
    def get_time_lags(indices, time_diffs):
        if len(indices) > 0:
            indxs = np.unique(indices[0])
            time_lags = []
            for i in indxs:
                if (i >= 0) and (i < len(time_diffs)):
                    time_lags.append(time_diffs[i])
            return time_lags
        else:
            raise Exception("Error: No pattern found for fetching time-lags")


#-------------------------------------------------------


class HandleData:

    def __init__(self, json_str):
        # self.raw_data = HandleData.read_csv(file_path)
        cols, self.raw_data = HandleData.test_dataset(json_str)
        if len(self.raw_data) == 0:
            self.data = False
            # print("csv file read error")
            raise Exception("Unable to read csv file")
        else:
            # print("Data fetched from csv file")
            self.data = self.raw_data
            self.title = self.get_title()
            self.attr_index = self.get_attributes()
            self.column_size = self.get_attribute_no()
            self.size = self.get_size()
            self.thd_supp = False
            self.equal = False
            self.attr_data = []
            self.lst_bin = []

    def get_size(self):
        size = len(self.raw_data)
        return size

    def get_attribute_no(self):
        count = len(self.raw_data[0])
        return count

    def get_title(self):
        data = self.raw_data
        if data[0][0].replace('.', '', 1).isdigit() or data[0][0].isdigit():
            return False
        else:
            if data[0][1].replace('.', '', 1).isdigit() or data[0][1].isdigit():
                return False
            else:
                title = []
                for i in range(len(data[0])):
                    # sub = (str(i + 1) + ' : ' + data[0][i])
                    # sub = data[0][i]
                    sub = [str(i+1), data[0][i]]
                    title.append(sub)
                del self.data[0]
                return title

    def get_attributes(self):
        attr = []
        time_cols = self.get_time_cols()
        for i in range(len(self.title)):
            temp_attr = self.title[i]
            indx = int(temp_attr[0])
            if len(time_cols) > 0 and ((indx-1) in time_cols):
                # exclude date-time column
                continue
            else:
                attr.append(temp_attr[0])
        return attr

    def get_time_cols(self):
        time_cols = list()
        # for k in range(10, len(self.data[0])):
        #    time_cols.append(k)
        # time_cols.append(0)
        # time_cols.append(1)
        # time_cols.append(2)
        # time_cols.append(3)
        # time_cols.append(4)
        # time_cols.append(5)
        # time_cols.append(6)
        # time_cols.append(7)
        # time_cols.append(8)
        # time_cols.append(9)
        for i in range(len(self.data[0])):  # check every column for time format
            row_data = str(self.data[0][i])
            try:
                time_ok, t_stamp = HandleData.test_time(row_data)
                if time_ok:
                    time_cols.append(i)
            except ValueError:
                continue
        if len(time_cols) > 0:
            return time_cols
        else:
            return []

    def init_attributes(self, eq):
        # (check) implement parallel multiprocessing
        # re-structure csv data into an array
        self.equal = eq
        temp = self.data
        cols = self.column_size
        time_cols = self.get_time_cols()
        for col in range(cols):
            if len(time_cols) > 0 and (col in time_cols):
                # exclude date-time column
                continue
            else:
                # get all tuples of an attribute/column
                raw_tuples = []
                for row in range(len(temp)):
                    raw_tuples.append(float(temp[row][col]))
                attr_data = [self.title[col][0], raw_tuples]
                self.attr_data.append(attr_data)

    def get_bin_rank(self, attr_data, symbol):
        # execute binary rank to calculate support of pattern
        n = len(attr_data[1])
        incr = tuple([attr_data[0], '+'])
        decr = tuple([attr_data[0], '-'])
        temp_pos = np.zeros((n, n), dtype='bool')
        temp_neg = np.zeros((n, n), dtype='bool')
        var_tuple = attr_data[1]
        for j in range(n):
            for k in range(j + 1, n):
                if var_tuple[j] > var_tuple[k]:
                    temp_pos[j][k] = 1
                    temp_neg[k][j] = 1
                else:
                    if var_tuple[j] < var_tuple[k]:
                        temp_neg[j][k] = 1
                        temp_pos[k][j] = 1
                    else:
                        if self.equal:
                            temp_neg[j][k] = 1
                            temp_pos[k][j] = 1
                            temp_pos[j][k] = 1
                            temp_neg[k][j] = 1
        temp_bin = np.array([])
        if symbol == '+':
            temp_bin = temp_pos
        elif symbol == '-':
            temp_bin = temp_neg
        supp = float(np.sum(temp_bin)) / float(n * (n - 1.0) / 2.0)
        self.lst_bin.append([incr, temp_pos, supp])
        self.lst_bin.append([decr, temp_neg, supp])
        return supp, temp_bin

    @staticmethod
    def read_csv(file):
        # 1. retrieve data-set from file
        with open(file, 'r') as f:
            dialect = csv.Sniffer().sniff(f.readline(), delimiters=";,' '\t")
            f.seek(0)
            reader = csv.reader(f, dialect)
            temp = list(reader)
            f.close()
        return temp

    @staticmethod
    def write_file(data, path):
        with open(path, 'w') as f:
            f.write(data)
            f.close()

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
                    raise ValueError('no valid date-time format found')

    @staticmethod
    def get_timestamp(time_data):
        try:
            ok, stamp = HandleData.test_time(time_data)
            if ok:
                return stamp
            else:
                return False
        except ValueError:
            return False

    @staticmethod  # added
    def test_dataset(json_string):
        # NB: test the dataset attributes: time|item_1|item_2|...|item_n
        # return true and (list) dataset if it is ok
        # 1. retrieve dataset from file
        data = json.loads(json_string)
        raw_titles = list(data[0].keys())
        temp = list()
        var_temp = list()
        for t in raw_titles:
            var_temp.append(str(t))
        temp.append(var_temp)
        for item in data:
            var_temp = list()
            for key, value in item.items():
                var_temp.append(str(value))
            temp.append(var_temp)
        # 2. Retrieve time and their columns
        time_cols = list()
        for i in range(len(temp[1])):  # check every column for time format
            row_data = str(temp[1][i])
            try:
                time_ok, t_stamp = HandleData.test_time(row_data)
                if time_ok:
                    time_cols.append(i)
            except ValueError:
                continue
        if time_cols:
            return time_cols, temp
        else:
            return False, temp

    @staticmethod
    def format_gp(obj_gp):
        arr_gp = list(obj_gp)
        new_gp = list()
        for item in arr_gp:
            attr = int(item[0])
            sign = item[1]
            str_gp = str(attr) + sign
            new_gp.append(str_gp)
        return set(new_gp)



#-------------------------------------------------------


class GradACO:

    def __init__(self, d_set):
        self.data = d_set
        self.attr_index = self.data.attr_index
        self.e_factor = 0  # evaporation factor
        self.p_matrix = np.ones((self.data.column_size, 3), dtype=int)
        self.valid_bins = []
        self.invalid_bins = []

    def run_ant_colony(self, min_supp, time_diffs=None):
        all_sols = list()
        win_sols = list()
        win_lag_sols = list()
        loss_sols = list()
        invalid_sols = list()
        # count = 0
        # converging = False
        # while not converging:
        repeated = 0
        while repeated < 5:
            # count += 1
            sol_n = self.generate_rand_pattern()
            # print(sol_n)
            if sol_n:
                if sol_n not in all_sols:
                    lag_sols = []
                    repeated = 0
                    all_sols.append(sol_n)
                    if loss_sols or invalid_sols:
                        # check for super-set anti-monotony
                        is_super = GradACO.check_anti_monotony(loss_sols, sol_n, False)
                        is_invalid = GradACO.check_anti_monotony(invalid_sols, sol_n, False)
                        if is_super or is_invalid:
                            continue
                    if win_sols:
                        # check for sub-set anti-monotony
                        is_sub = GradACO.check_anti_monotony(win_sols, sol_n, True)
                        if is_sub:
                            continue
                    if time_diffs is None:
                        supp, sol_gen = self.evaluate_bin_solution(sol_n, min_supp, time_diffs)
                    else:
                        supp, lag_sols = self.evaluate_bin_solution(sol_n, min_supp, time_diffs)
                        if supp:
                            sol_gen = lag_sols[0]
                        else:
                            sol_gen = False
                    # print(supp)
                    if supp and (supp >= min_supp):  # and ([supp, sol_gen] not in win_sols):
                        if [supp, sol_gen] not in win_sols:
                            win_sols.append([supp, sol_gen])
                            self.update_pheromone(sol_gen)
                            if time_diffs is not None:
                                win_lag_sols.append([supp, lag_sols])
                            # converging = self.check_convergence()
                    elif supp and (supp < min_supp):  # and ([supp, sol_gen] not in loss_sols):
                        if [supp, sol_gen] not in loss_sols:
                            loss_sols.append([supp, sol_gen])
                        # self.update_pheromone(sol_n, False)
                    else:
                        invalid_sols.append([supp, sol_n])
                        if sol_gen:
                            invalid_sols.append([supp, sol_gen])
                        # self.update_pheromone(sol_n, False)
                else:
                    repeated += 1
            # converging = self.check_convergence(repeated)
            # is_member = GradACO.check_convergence(win_sols, sol_n)
        # print("All: "+str(len(all_sols)))
        # print("Winner: "+str(len(win_sols)))
        # print("Losers: "+str(len(loss_sols)))
        # print(count)
        if time_diffs is None:
            return GradACO.remove_subsets(win_sols)
            # return win_sols
        else:
            return GradACO.remove_subsets(win_lag_sols, True)
            # return win_lag_sols

    def generate_rand_pattern(self):
        p = self.p_matrix
        n = len(self.attr_index)
        pattern = list()
        count = 0
        for i in range(n):
            max_extreme = len(self.attr_index)
            x = float(rand.randint(1, max_extreme) / max_extreme)
            pos = float(p[i][0] / (p[i][0] + p[i][1] + p[i][2]))
            neg = float((p[i][0] + p[i][1]) / (p[i][0] + p[i][1] + p[i][2]))
            if x < pos:
                temp = tuple([self.attr_index[i], '+'])
            elif (x >= pos) and (x < neg):
                temp = tuple([self.attr_index[i], '-'])
            else:
                # temp = tuple([self.data.attr_index[i], 'x'])
                continue
            pattern.append(temp)
            count += 1
        if count <= 1:
            pattern = False
        return pattern

    def evaluate_bin_solution(self, pattern, min_supp, time_diffs):
        # pattern = [('2', '+'), ('4', '+')]
        lst_bin = self.data.lst_bin
        gen_pattern = []
        bin_data = []
        count = 0
        for obj_i in pattern:
            if obj_i in self.invalid_bins:
                continue
            elif obj_i in self.valid_bins:
                # fetch pattern
                for obj in lst_bin:
                    if obj[0] == obj_i:
                        gen_pattern.append(obj[0])
                        bin_data.append([obj[1], obj[2], obj[0]])
                        count += 1
                        break
            else:
                attr_data = False
                for obj in self.data.attr_data:
                    if obj[0] == obj_i[0]:
                        attr_data = obj
                        break
                if attr_data:
                    supp, temp_bin = self.data.get_bin_rank(attr_data, obj_i[1])
                    if supp >= min_supp:
                        self.valid_bins.append(tuple([obj_i[0], '+']))
                        self.valid_bins.append(tuple([obj_i[0], '-']))
                        gen_pattern.append(obj_i)
                        bin_data.append([temp_bin, supp, obj_i])
                        count += 1
                    else:
                        self.invalid_bins.append(tuple([obj_i[0], '+']))
                        self.invalid_bins.append(tuple([obj_i[0], '-']))
                else:
                    # binary does not exist
                    return False, False
        if count <= 1:
            return False, False
        else:
            size = len(self.data.attr_data[0][1])
            supp, new_pattern = GradACO.perform_bin_and(bin_data, size, min_supp, gen_pattern, time_diffs)
            return supp, new_pattern

    def update_pheromone(self, pattern):
        lst_attr = []
        for obj in pattern:
            attr = int(obj[0])
            lst_attr.append(attr)
            symbol = obj[1]
            i = attr - 1
            if symbol == '+':
                self.p_matrix[i][0] += 1
            elif symbol == '-':
                self.p_matrix[i][1] += 1
        for index in self.data.attr_index:
            if int(index) not in lst_attr:
                # print(obj)
                i = int(index) - 1
                self.p_matrix[i][2] += 1

    def plot_pheromone_matrix(self):
        x_plot = np.array(self.p_matrix)
        print(x_plot)
        # Figure size (width, height) in inches
        # plt.figure(figsize=(4, 4))
        plt.title("+: increasing; -: decreasing; x: irrelevant")
        # plt.xlabel("+: increasing; -: decreasing; x: irrelevant")
        # plt.ylabel('Attribute')
        plt.xlim(0, 3)
        plt.ylim(0, len(self.p_matrix))
        x = [0, 1, 2]
        y = []
        for i in range(len(self.data.title)):
            y.append(i)
            plt.text(-0.3, (i+0.5), self.data.title[i][1][:3])
        plt.xticks(x, [])
        plt.yticks(y, [])
        plt.text(0.5, -0.4, '+')
        plt.text(1.5, -0.4, '-')
        plt.text(2.5, -0.4, 'x')
        plt.pcolor(-x_plot, cmap='gray')
        plt.gray()
        plt.grid()
        plt.show()

    @staticmethod
    def check_anti_monotony(lst_p, p_arr, ck_sub):
        result = False
        if ck_sub:
            for obj in lst_p:
                result = set(p_arr).issubset(set(obj[1]))
                if result:
                    break
        else:
            for obj in lst_p:
                result = set(p_arr).issuperset(set(obj[1]))
                if result:
                    break
        return result

    @staticmethod
    def perform_bin_and(unsorted_bins, n, thd_supp, gen_p, t_diffs):
        lst_bin = sorted(unsorted_bins, key=lambda x: x[1])
        final_bin = np.array([])
        pattern = []
        count = 0
        for obj in lst_bin:
            temp_bin = final_bin
            if temp_bin.size != 0:
                temp_bin = temp_bin & obj[0]
                supp = float(np.sum(temp_bin)) / float(n * (n - 1.0) / 2.0)
                if supp >= thd_supp:
                    final_bin = temp_bin
                    pattern.append(obj[2])
                    count += 1
            else:
                final_bin = obj[0]
                pattern.append(obj[2])
                count += 1
        supp = float(np.sum(final_bin)) / float(n * (n - 1.0) / 2.0)
        if count >= 2:
            if t_diffs is None:
                return supp, pattern
            else:
                t_lag = FuzzyMF.calculate_time_lag(FuzzyMF.get_patten_indices(final_bin), t_diffs, thd_supp)
                if t_lag:
                    temp_p = [pattern, t_lag]
                    return supp, temp_p
                else:
                    return -1, pattern
        else:
            return -1, gen_p

    @staticmethod
    def remove_subsets(all_sols, temporal=False):
        new_sols = list()
        if not temporal:
            for item in all_sols:
                sol = set(item[1])
                is_sub = GradACO.check_subset(sol, all_sols)
                # print(is_sub)
                if not is_sub:
                    new_sols.append(item)
        else:
            for item in all_sols:
                sol = set(item[1][0])
                is_sub = GradACO.check_subset(sol, all_sols, temporal)
                # print(is_sub)
                if not is_sub:
                    new_sols.append(item)
        # print(new_sols)
        return new_sols

    @staticmethod
    def check_subset(item, items, extra=False):
        if not extra:
            for obj in items:
                if (item != set(obj[1])) and item.issubset(set(obj[1])):
                    return True
            return False
        else:
            for obj in items:
                if (item != set(obj[1][0])) and item.issubset(set(obj[1][0])):
                    return True
            return False





#-------------------------------------------------------


class TgradACO:

    def __init__(self, d_set, ref_item, min_sup, min_rep, cores):
        # For tgraank
        self.d_set = d_set
        cols = d_set.get_time_cols()
        if len(cols) > 0:
            # print("Dataset Ok")
            self.time_ok = True
            self.time_cols = cols
            self.min_sup = min_sup
            self.ref_item = ref_item
            self.max_step = self.get_max_step(min_rep)
            self.orig_attr_data = d_set.attr_data
            self.cores = cores
            # self.multi_data = self.split_dataset()
        else:
            # print("Dataset Error")
            self.time_ok = False
            self.time_cols = []
            raise Exception('No date-time data found')

    def run_tgraank(self, parallel=False):
        if parallel:
            # implement parallel multi-processing
            if self.cores > 1:
                num_cores = self.cores
            # else:
            #    num_cores = InitParallel.get_num_cores()
            # print("No. of cpu cores found: " + str(num_cores))
            # print("No. of parallel tasks: " + str(self.max_step))
            self.cores = num_cores
            steps = range(self.max_step)
            pool = mp.Pool(num_cores)
            patterns = pool.map(self.fetch_patterns, steps)
            # patterns = Parallel(n_jobs=num_cores)(delayed(self.fetch_patterns)(s+1) for s in steps)
            # print("Finished extracting patterns")
            return patterns
        else:
            patterns = list()
            for step in range(self.max_step):
                t_pattern = self.fetch_patterns(step)
                if t_pattern:
                    patterns.append(t_pattern)
            return patterns

    def fetch_patterns(self, step):
        step += 1  # because for-loop is not inclusive from range: 0 - max_step
        # 1. Calculate representativity
        chk_rep, rep_info = self.get_representativity(step)
        # print(rep_info)
        if chk_rep:
            # 2. Transform data
            self.d_set.attr_data = self.orig_attr_data
            data, time_diffs = self.transform_data(step)
            self.d_set.attr_data = data
            self.d_set.lst_bin = []
            # d_set = HandleData("", attr_data=[self.d_set.column_size, data])
            # 3. Execute aco-graank for each transformation
            ac = GradACO(self.d_set)
            list_gp = ac.run_ant_colony(self.min_sup, time_diffs)
            # print("\nPheromone Matrix")
            # print(ac.p_matrix)
            if len(list_gp) > 0:
                return list_gp
        return False

    def transform_data(self, step):
        # NB: Restructure dataset based on reference item
        data = self.d_set.data
        if self.time_ok:
            # 1. Calculate time difference using step
            ok, time_diffs = self.get_time_diffs(step)
            if not ok:
                msg = "Error: Time in row " + str(time_diffs[0]) + " or row " + str(time_diffs[1]) + " is not valid."
                raise Exception(msg)
            else:
                ref_col = self.ref_item
                if ref_col in self.time_cols:
                    msg = "Reference column is a 'date-time' attribute"
                    raise Exception(msg)
                elif (ref_col < 0) or (ref_col >= len(self.d_set.title)):
                    msg = "Reference column does not exist\nselect column between: " \
                          "0 and "+str(len(self.d_set.title) - 1)
                    raise Exception(msg)
                else:
                    # 1. Split the original data-set into column-tuples
                    attr_cols = self.d_set.attr_data

                    # 2. Transform the data using (row) n+step
                    new_data = list()
                    size = len(data)
                    for obj in attr_cols:
                        col_index = int(obj[0])
                        tuples = obj[1]
                        temp_tuples = list()
                        if (col_index - 1) == ref_col:
                            # reference attribute
                            for i in range(size-step):
                                temp_tuples.append(tuples[i])
                        else:
                            for i in range(step, size):
                                temp_tuples.append(tuples[i])
                        var_attr = [str(col_index), temp_tuples]
                        new_data.append(var_attr)
                    return new_data, time_diffs
        else:
            msg = "Fatal Error: Time format in column could not be processed"
            raise Exception(msg)

    def get_representativity(self, step):
        # 1. Get all rows minus the title row (already removed)
        all_rows = len(self.d_set.data)

        # 2. Get selected rows
        incl_rows = (all_rows - step)

        # 3. Calculate representativity
        if incl_rows > 0:
            rep = (incl_rows / float(all_rows))
            info = {"Transformation": "n+"+str(step), "Representativity": rep, "Included Rows": incl_rows,
                    "Total Rows": all_rows}
            return True, info
        else:
            return False, "Representativity is 0%"

    def get_max_step(self, minrep):
        # 1. count the number of steps each time comparing the
        # calculated representativity with minimum representativity
        size = len(self.d_set.data)
        for i in range(size):
            check, info = self.get_representativity(i + 1)
            if check:
                rep = info['Representativity']
                if rep < minrep:
                    return i
            else:
                return 0

    def get_time_diffs(self, step):
        data = self.d_set.data
        size = len(data)
        time_diffs = []
        for i in range(size):
            if i < (size - step):
                # temp_1 = self.data[i][0]
                # temp_2 = self.data[i + step][0]
                temp_1 = temp_2 = ""
                for col in self.time_cols:
                    temp_1 = " "+str(data[i][int(col)])
                    temp_2 = " "+str(data[i + step][int(col)])
                    break
                stamp_1 = HandleData.get_timestamp(temp_1)
                stamp_2 = HandleData.get_timestamp(temp_2)
                if (not stamp_1) or (not stamp_2):
                    return False, [i + 1, i + step + 1]
                time_diff = (stamp_2 - stamp_1)
                time_diffs.append(time_diff)
        # print("Time Diff: " + str(time_diff))
        return True, time_diffs


#---------- main programs -------------------------------


def init_acograd(json_str, min_supp, cores=1, eq=False):
    try:
        d_set = HandleData(json_str)
        if d_set.data:
            titles = d_set.title
            d_set.init_attributes(eq)
            ac = GradACO(d_set)
            list_gp = ac.run_ant_colony(min_supp)

            for txt in titles:
                print(str(txt[0]) + '. ' + str(txt[1]) + '<br>')
                # print(str(line) + "<br>")
            print('<h5>Pattern : Support</h5>')
            
            list_gp.sort(key=lambda k: k[0], reverse=True)
            for gp in list_gp:
                supp = "%.3f" % gp[0]
                print(str(HandleData.format_gp(gp[1])) + ' : ' + str(supp) + '<br>')
                # print(str(tuple(D1[i])) + ' : ' + str(supp) + "<br>")
            sys.stdout.flush()
        else:
            print("<h5>Oops! no gradual patterns found</h5>")
            sys.stdout.flush()
    except Exception as error:
        msg = "<h5>Failed: " + str(error) + "</h5>"
        print(msg)
        sys.stdout.flush()

def init_acotgrad(json_str, refItem, minSup, minRep, allowPara=0, eq=False):
    try:
        d_set = HandleData(json_str)
        if d_set.data:
            titles = d_set.title
            d_set.init_attributes(eq)
            tgp = TgradACO(d_set, refItem, minSup, minRep, allowPara)

            if allowPara >= 1:
                msg_para = "True"
                list_tgp = tgp.run_tgraank(parallel=True)
            else:
                msg_para = "False"
                list_tgp = tgp.run_tgraank()
                
            list_tgp = list(filter(bool, list_tgp))
            # if len(list_tgp) > 10:
            list_tgp.sort(key=lambda k: (k[0][0], k[0][1]), reverse=True)

            for txt in titles:
                col = (int(txt[0]) - 1)
                if col == refItem:
                    print(str(col) + '. ' + str(txt[1]) + '**' + '<br>')
                else:
                    print(str(col) + '. ' + str(txt[1]) + '<br>')
            print('<h5>Pattern : Support</h5>')

            for obj in list_tgp:
                if obj:
                    #tgp = obj[0]
                    for tgp in obj:
                        supp = "%.3f" % tgp[0]
                        print(str(HandleData.format_gp(tgp[1][0])) + ' : ' + str(supp) + ' | ' + str(tgp[1][1]) + '<br>')
            sys.stdout.flush()
        else:
            print("<h5>Oops! no gradual patterns found</h5>")
            sys.stdout.flush()
    except Exception as error:
        msg = "<h5>Failed: " + str(error) + "</h5>"
        print(msg)
        sys.stdout.flush()


request = int(sys.argv[1])

if request == 1:
    # gradual patterns
    file_data = sys.argv[2]
    min_sup = float(sys.argv[3])
    init_acograd(file_data, min_sup)
elif request == 2:
    # fuzzy-temporal patterns
    file_name = str(sys.argv[2])
    ref_col = int(sys.argv[3])
    min_sup = float(sys.argv[4])
    min_rep = float(sys.argv[5])
    init_acotgrad(file_name, ref_col, min_sup, min_rep)
elif request == 11:
    # emerging gradual Patterns
    file_data1 = str(sys.argv[2])
    file_data2 = str(sys.argv[3])
    min_sup = float(sys.argv[4])
    # algorithm_ep_gradual(file_data1, file_data2, min_sup)
elif request == 12:
    # emerging fuzzy-temporal Patterns
    file_name = str(sys.argv[2])
    ref_col = int(sys.argv[3])
    min_sup = float(sys.argv[4])
    min_rep = float(sys.argv[5])
    # algorithm_ep_fuzzy(file_name, ref_col, min_sup, min_rep)
elif request == 21:
    # check data-set for time
    file_name = str(sys.argv[2])
    cols, data = HandleData.test_dataset(file_name)
    if cols:
        print("true")
    else:
        print("false")
    sys.stdout.flush()
else:
    print("<h5>Request not found!</h5>")
    sys.stdout.flush()