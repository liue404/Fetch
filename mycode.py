import os
import glob
import csv
import sys
import time
from collections import deque


class Spending:
    def __init__(self, points: int):
        self.spending_points = points
        self.dic_company_transac = {}

    def print_usable_points(self):
        for key in self.dic_company_transac:
            usable_num = 0
            pos_transac = self.dic_company_transac[key][0]
            if len(pos_transac) != 0:
                for transaction in pos_transac:
                    #add all usable points
                    usable_num += transaction[1]
            print(key+":"+str(usable_num))

    def print_transac_his(self):

        for key in self.dic_company_transac:
            print(key)
            t = self.dic_company_transac[key]
            print(t)
            print("Pos:")
            print(t[0])
            print("Neg:")
            print(t[1])

    def merge_negetive(self, transac_his):
        # here we think the payer's point will never be negative at ANY TIME
        pos_transac = transac_his[0]
        neg_transac = transac_his[1]
        # "merge" all the negative transaction
        while neg_transac:
            neg_points = neg_transac[0][1]
            # iterative subtract neg_points from pos_transac
            while neg_points < 0:
                s = neg_points + pos_transac[0][1]
                if s > 0:
                    # the first pos_transac is enough to be subtracted
                    pos_transac[0][1] = s
                    # clear first neg_transac
                    neg_transac.popleft()
                    neg_points = 0
                elif s < 0:
                    # the first pos_transac is not enough, clear the first pos_transac
                    pos_transac.popleft()
                    neg_transac[0][1] = s
                    neg_points = s
                else:
                    # equal, clear both
                    pos_transac.popleft()
                    neg_transac.popleft()
                    neg_points = 0
                neg_points = min(0, s)
# list[deque[list[str, int]]]
    #: tuple[int, str]
    def insert_transac(self, points_time, all_transac_his ):
        points, timestamp = points_time
        insert_t = time.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        pair = [insert_t, points]

        # for all_transac_his, the first list is positive points transaction his, the second is the negative
        if points < 0:
            transac_his = all_transac_his[1]
        else:
            transac_his = all_transac_his[0]

        if len(transac_his) == 0:
            transac_his.append(pair)
            return

        # timestamp format 2020-11-02T14:00:00Z
        for i in range(len(transac_his)):
            t = transac_his[i]
            cur_t = t[0]
            if insert_t < cur_t:
                transac_his.insert(i, pair)
                return
            elif i == len(transac_his) - 1:
                transac_his.append(pair)
                return

    def read_transaction_data(self):
        # read all *.csv files in current directory
        path = os.getcwd()
        csv_files = glob.glob(os.path.join(path, "*.csv"))
        for f in csv_files:
            with open(f, mode='r') as csv_file:
                csv_reader = csv.reader(csv_file)
                i = 0
                for row in csv_reader:
                    if i == 0:
                        i += 1
                        continue
                    company = row[0]
                    points = int(row[1])
                    timestamp = row[2]
                    if company not in self.dic_company_transac:
                        # don't have transac his, create a new data
                        self.dic_company_transac[company] = [deque([]), deque([])]
                    # have the transac his of this company, insert new data
                    transac_his = self.dic_company_transac[company]
                    self.insert_transac((points, timestamp), transac_his)
    def merge_negative_transaction_his(self):
        for key in self.dic_company_transac.keys():
            all_transac_his = self.dic_company_transac[key]
            self.merge_negetive(all_transac_his)

    def find_oldest_points(self):
        init_flag = True
        for company, all_transac_his in self.dic_company_transac.items():
            if len(all_transac_his[0]) == 0:
                # there is no remain points in this payer
                continue
            if init_flag:
                # first, init the res_ variables
                res_key = company
                res_time = all_transac_his[0][0][0]
                init_flag = False
                continue
            cur_time = all_transac_his[0][0][0]
            if cur_time < res_time:
                # this one is older
                res_key = company
                res_time = cur_time
        return res_key
    def comsume_company_points(self, company, neg_points):
        all_transac_his = self.dic_company_transac[company]
        pos_transac = all_transac_his[0]

        # spend the first row points
        s = neg_points + pos_transac[0][1]
        if s > 0:
            # the first pos_transac is enough to be subtracted
            pos_transac[0][1] = s
        else:
            # if all the points are used
            if len(pos_transac) > 0:
                pos_transac.popleft()
        neg_points = min(0, s)
        return neg_points



    def comsume_points(self):
        comsume_num = -self.spending_points

        while comsume_num < 0:
            # first, find the oldest points
            oldest_company = self.find_oldest_points()
            # second, consume the points
            comsume_num = self.comsume_company_points(oldest_company, comsume_num)




def main():

    arg_n = len(sys.argv)
    if arg_n != 2:
        print("Please enter correct spending points!")
        return

    spending_points = int(sys.argv[1])

    if spending_points < 0:
        print("Spending points can not be negetive!")
        return

    S = Spending(spending_points)
    S.read_transaction_data()
    S.merge_negative_transaction_his()
    S.comsume_points()
    S.print_usable_points()

if __name__ == '__main__':
    main()
