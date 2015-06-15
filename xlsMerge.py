#!/usr/bin/python3

from __future__ import print_function
import glob
import pandas

def get_raw_data(filenames, data):
    """Here it uses pandas.read_excel to get contents from all xls files in
    present directory. Since pandas uses numpy.int64 to store data, it may
    cause a problem to manipulate huge numbers(larger than 2**63).  
    """
    for name in filenames:
        sheet = pandas.read_excel(name)
#drop '.xls' from name
        data[name[:5]] = sheet

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
        A33-11D
    """
#Initiate sample, aka sample_raw_data
    default = {
        'raw':[0,0,0,0,0,0],
        'ref_1':[0,0,0,0,0,0],
        'ref_2':[0,0,0,0,0,0]
    }
    for library in ['A', 'B']:
        for plate in range(56):
            if library == 'B' and plate>25:
                continue
            for idx in 'ABCDEFGH':
                for col in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
                    name = ''.join([
                        library,
                        '{:{fill}2d}'.format(plate+1,fill='0'),
                        '-',
                        col,
                        idx
                    ])
                    sample[name] = default

def get_sample_data(raw_data, sample):
    for sheet_name, sheet in raw_data.items():
        time = int(sheet_name[-1])
        if time > 6:
            continue
        else:
            time = time - 1
        for idx in 'ABCDEFGH':
            for col in ['02', '03', '04', '05', '06', '07', '08', '09', '10', '11']:
                cell = ''.join([
                    sheet_name[0:-1],
                    col,
                    idx
                ])
                ref_1 = sheet[1][idx]
                ref_2 = sheet[12][idx]
                raw = sheet[int(col)][idx]
                print('cell\tcol\tidx\traw\ttime\n')
                print(cell,col,idx,raw,time)
                if sample[cell]['raw'][time] != 0:
                    print('Break')
                    print(sheet_name, cell, time)
                    print(sample[cell])
                    raise ValueError
#found reason, here it edit sample[*]['raw'][time]
                sample[cell]['raw'][time] = raw
                sample[cell]['ref_1'][time] = ref_1
                sample[cell]['ref_2'][time] = ref_2

def test(raw_data,sample_raw_data):
    print('a01-4\n',raw_data['A01-4'])
    print('a01-5\n',raw_data['A01-5'])
    print('a01-01d\n',sample_raw_data['A01-01D'])

def main():
    """It uses glob.glob to get names of all xls files. Hence it should be 
    run in the directory which contains all xls files.
    All xls filename should follow this format:
     A00-0.xls
     01234
    
    Library: A B
       Plate: A 56, B 26
       Times: 6 
            There are A28 and others which have 7 or 10 tables. In order to 
            simplify the program, here it just omit tables from 7 to 10.
    """
    name_list = glob.glob('*.xls')
    raw_data = dict()
    sample_raw_data = dict()
    get_raw_data(name_list, raw_data)
    initiate_sample_data(raw_data, sample_raw_data)
    get_sample_data(raw_data, sample_raw_data)
    test(raw_data,sample_raw_data)

if __name__ == '__main__':
    main()
