#!/usr/bin/python3

from __future__ import print_function
import glob
import pandas
from scipy.stats import linregress


def get_raw_data(filenames, data):
    """It can accept xls format.
    """
    for name in filenames:
        sheet = pandas.read_excel(name)
        data[name] = sheet


def initiate_sample_data(raw, sample):
    """This function will get every sample's data and its two references 
    data.
    table:
        >>> a.index
        Index(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'], dtype='object')
        >>> a.columns
        Index([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 'Unnamed: 12'],
              dtype='object')
    sample name then will looks like:
        P1-11D
    """
    for plate in '1234567':
        for idx in 'ABCDEFGH':
            for col in ['01', '12']:
                name = ''.join([
                    'P',
                    plate,
                    '-',
                    col,
                    idx
                ])
                sample[name] = { 
                    '50uM': [0, 0, 0, 0, 0, 0, 0],
                    '20uM': [0, 0, 0, 0, 0, 0, 0],
                    '10uM': [0, 0, 0, 0, 0, 0, 0],
                    'ref1': [0, 0, 0, 0, 0, 0, 0],
                    'ref2': [0, 0, 0, 0, 0, 0, 0],
                    'ref3': [0, 0, 0, 0, 0, 0, 0],
                    'ref4': [0, 0, 0, 0, 0, 0, 0],
                    'ref5': [0, 0, 0, 0, 0, 0, 0],
                    'ref6': [0, 0, 0, 0, 0, 0, 0]
                }


def get_sample_data(raw_data, sample):
    """In round 2, data in left plate and right plate are in different order:
            ref1 50uM 20uM 10uM ref2 ref3 50uM 20uM 10uM ref1 ref2 ref3
    But in Plate 1 and 2, there are some data does not follow this rule.
    """
    for sheet_name, sheet in raw_data.items():
        print(sheet_name, sheet)
        time = int(sheet_name[-1])
        plate = int(sheet_name[1])
        time = time - 1
        for idx in 'ABCDEFGH':
            for col in ['01', '12']:
                cell = ''.join([
                    sheet_name[0:-1],
                    col,
                    idx
                ])
                ref1 = sheet[1][idx]
                ref2 = sheet[12][idx]
                ref3 = None
                ref4 = None
                ref5 = None
                ref6 = None
                if plate >= 3:
                    ref3 = sheet[6][idx]
                    ref4 = sheet[11][idx]
                if plate >= 5:
                    ref5 = sheet[5][idx]
                    ref6 = sheet[10][idx]
                raw = sheet[int(col)][idx]
                if col == '01':
                    fifty = sheet[2][idx]
                    twenty = sheet[3][idx]
                    ten = sheet[4][idx]
                else:
                    fifty = sheet[7][idx]
                    twenty = sheet[8][idx]
                    ten = sheet[9][idx]
                sample[cell]['50uM'][time] = fifty
                sample[cell]['20uM'][time] = twenty
                sample[cell]['10uM'][time] = ten
                sample[cell]['ref1'][time] = ref1
                sample[cell]['ref2'][time] = ref2
                sample[cell]['ref3'][time] = ref3
                sample[cell]['ref4'][time] = ref4
                sample[cell]['ref5'][time] = ref5
                sample[cell]['ref6'][time] = ref6

def analyse(sample_raw_data, analysis):
    """This function only use the first five points.
    """
    x = [0, 60, 120, 180, 240]
    for name, data in sample_raw_data.items():
        id = name
        item = [id, 0, 0]
        raw = data['raw'][:5]
        ref_1 = data['ref_1'][:5]
        ref_2 = data['ref_2'][:5]
        if 'OVRFLW' in raw:
            continue
        slope, intercept, r_value, _, _ = linregress(x, raw)
        r_square = r_value ** 2
        item.extend([
            slope,
            intercept,
            r_square
        ])
        slope, intercept, r_value, _, _ = linregress(x, ref_1)
        r_square = r_value ** 2
        item.extend([
            slope,
            intercept,
            r_square
        ])
        slope, intercept, r_value, _, _ = linregress(x, ref_2)
        r_square = r_value ** 2
        item.extend([
            slope,
            intercept,
            r_square
        ])
        item.extend(raw)
        item.extend(ref_1)
        item.extend(ref_2)
        item[1] = item[3] / item[6]
        item[2] = item[3] / item[9]
        analysis.append(item)


def output(analysis):
    """Output csv format.
    """
    with open('result.csv', 'w') as out:
        for line in analysis:
            line_out = [str(i) for i in line]
            out.write(','.join(line_out))
            out.write('\n')


def main():
    """It uses glob.glob to get names of all xls files. Hence it should be 
    run in the directory which contains all xls files.
    All xls filename should follow this format:
     P0-0.xls
    """
    name_list = glob.glob('*-*')
    raw_data = dict()
    sample_raw_data = dict()
    sample = dict()
    analysis = list()
    analysis = [[
        'id', 
        'cell',
        'slope_of_slope',
        'fold_1', 'fold_2', 'fold_3',
        'slope_50uM', 'slope_20uM', 'slope_10uM', 'slope_ref'
        'intercept_50uM', 'intercept_20uM', 'intercept_10uM', 'intercept_ref',
        'r^2_50uM', 'r^2_20uM', 'r^2_10uM', 'r^2_ref'
        'raw_1', 'raw_2', 'raw_3', 'raw_4', 'raw_5', 'raw_6', 'raw_7',
        'ref1_1', 'ref1_2', 'ref1_3', 'ref1_4', 'ref1_5', 'ref1_6', 'ref1_7', 
        'ref2_1', 'ref2_2', 'ref2_3', 'ref2_4', 'ref2_5', 'ref2_6', 'ref2_7', 
        'ref3_1', 'ref3_2', 'ref3_3', 'ref3_4', 'ref3_5', 'ref3_6', 'ref3_7', 
        'ref4_1', 'ref4_2', 'ref4_3', 'ref4_4', 'ref4_5', 'ref4_6', 'ref4_7', 
        'ref5_1', 'ref5_2', 'ref5_3', 'ref5_4', 'ref5_5', 'ref5_6', 'ref5_7', 
        'ref6_1', 'ref6_2', 'ref6_3', 'ref6_4', 'ref6_5', 'ref6_6', 'ref6_7', 
    ]]
    get_raw_data(name_list, raw_data)
    initiate_sample_data(raw_data, sample_raw_data)
    get_sample_data(raw_data, sample_raw_data)
    for i in sample_raw_data:
        print(i)
    analyse(sample_raw_data, analysis)
    output(analysis)

if __name__ == '__main__':
    main()