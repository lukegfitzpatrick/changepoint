import pandas as pd
import numpy as np
import os
from itertools import chain
import matplotlib.pyplot as plt

class cp2:

    def __init__(self, data, ycol, dcol = None, delta=50, perms = 100):

        self.perms = perms
        self.delta = delta
        self.ycol = ycol
        self.dcol=dcol

        self.y, self.d = self._format_data(data, ycol=self.ycol, dcol=self.dcol)

    def _format_data(self, data, ycol, dcol):

        if dcol is None:
            if isinstance(data.index, pd.DatetimeIndex):
                data = data.sort_index()
                return data[ycol].values, data.index.values

            else:
                print('Need to specify a date column')


        if dcol is not None:
            if data[dcol].values.dtype == np.dtype('datetime64[ns]'):
                data = data.sort_values(by=dcol)
                return data[ycol].values, data[dcol].values

            elif data[dcol].values.dtype != np.dtype('datetime64[ns]'):
                data[dcol] = pd.to_datetime(data[dcol])
                data = data.sort_values(by=dcol)
                return data[ycol].values, pd.to_datetime(data[dcol]).values

    def _make_range(self, starts, ends):
        return [range(s,e) for s, e in zip(starts, ends)]

    def _get_max_qstat(self, values, dates, delta=50):
        qmax = 0
        location = 0
        for i in range(delta, len(values) - delta):
            n = len(values[:i])
            m = len(values[i:])

            A = np.median(values[i-delta:i])
            B = np.median(values[i:i+delta])

            qstat = ((n*m)/(n+m)) * (2*(A*B)**2)

            if qstat>qmax:
                qmax = qstat
                location = i

        return qmax, dates[location]

    def _get_pvals(self, values, dates):
        results = []
        for i in range(self.perms):
            perm = np.random.permutation(values)
            result = self._get_max_qstat(perm, dates)
            results.append(result[0])
        return np.percentile(results, 99)

    def run(self):
        test_index = np.array(range(len(self.d)))
        starts = [test_index.min()]
        ends = [test_index.max()]
        changepoints = []
        while len(test_index)>20:
            if starts == [] and ends ==[]:
                break
            mrange = self._make_range(starts, ends)
            del_range = range(0)
            for mr in mrange:
                fday = mr[0]
                lday = mr[-1]+1
                if 2*self.delta >=len(mr):
                    print('range too small: deleting {} to {}'.format(self.d[fday], self.d[lday]))
                    print
                    test_index = np.delete(test_index, mr)
                    #dates = np.delete(dates, mr)
                    starts.remove(mr[0])
                    ends.remove(mr[-1]+1)

                else:
                    print('testing {} to {}'.format(self.d[fday], self.d[lday]))
                    y_test = self.y[mr]
                    date_test = self.d[mr]
                    pval = self._get_pvals(y_test, date_test)
                    q_test, candidate = self._get_max_qstat(y_test, date_test)

                    if q_test>pval:
                        print('changepoint detected at {}'.format(candidate))
                        print('')
                        changepoints.append(candidate)
                        starts.append(np.where(self.d==candidate)[0][0] + 1)
                        starts.sort()
                        ends.insert(0, np.where(self.d==candidate)[0][0])
                        ends.sort()

                    elif q_test<=pval:
                        print('no changepoint detected ')
                        print('')
                        del_range = chain(del_range, mr)
                        starts.remove(mr[0])
                        ends.remove(mr[-1]+1)

            test_index = np.delete(test_index, [i for i in del_range])
        return changepoints

    def make_plot(self, changepoints):
        data = self.data
        changepoints = pd.to_datetime(changepoints)
        points = [data.index.min(), data.index.max()]
        points.extend(changepoints)
        points.sort()
        #points.sort()
        segments = [pd.date_range(points[i], points[i+1]) for i in range(len(points)-1)]
        fig, ax = plt.subplots(figsize=(25,5))
        for seg in segments:
            plt.plot(data.loc[seg, 'y'])
