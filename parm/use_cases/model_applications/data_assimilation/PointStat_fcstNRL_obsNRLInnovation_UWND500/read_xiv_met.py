#!/usr/bin/python

"""
Python code to read the innovation file

Usage:
python read_xiv.py [innovar_file_name]

"""

import abc
import bz2
import collections
import gzip
import h5py
import numpy as np
import os.path
import re
import sys

import multiprocessing as mp
import pandas as pd

import time, datetime

# namedtuple:
Observation = collections.namedtuple('Observation', 'n ob bk t_bk xiv err etc lat lon p_ob jvar insty nvp ichk idt c_pf_ob c_db_ob idp lsi rej bkerr cob resid')

# define column constants
xiv_fld = {
                'OB'         :       1   ,  # OB
                'BK'         :       2   ,  # BK
                'T_BK'       :       3   ,  # T_BK
                'XIV'        :       4   ,  # XIV
                'ERR'        :       5   ,  # ERR
                'ETC'        :       6   ,  # ETC
                'LAT'        :       7   ,  # LAT
                'LON'        :       8   ,  # LON
                'P'          :       9   ,  # P
                'JVARTY'     :       10  ,  # JVARTY
                'INSTY'      :       11  ,  # INSTY
                'NVP'        :       12  ,  # NVP
                'ICHK'       :       13  ,  # ICHK
                'IDT'        :       14  ,  # IDT
                'C_PF'       :       15  ,  # C_PF
                'C_DB'       :       16  ,  # C_DB
                'IDP'        :       17  ,  # IDP
                'LSI'        :       18  ,  # LSI
                'REJ'        :       19  ,  # REJ
                'BKERR'      :       20  ,  # BKERR
                'COB'        :       21  ,  # COB
                'RESID'      :       22  ,  # RESID
                'SENS'       :       23  }  # Observation Sensitivity

def create_met_dataframe(df,hdr):

  # Bring in user supplied query info
  # qstr is a string of booleans to apply to non-string fields
  # cpfstr is the substring to search the c_pf_ob column for
  # cpfbeg is the beginning index of the cpf substring
  # cpfend is the ending index of the cpf substring
  # cdbstr is the substring to search the c_db_ob column for
  # cdbbeg is the beginning index of the cdb substring
  # cdbend is the ending index of the cdb substring
  # only supports 1 string for each string column, and only the "&" operator for combining with qstr
  qstr = os.environ.get('NRL_QUERY_STRING','')
  cpfstr = os.environ.get('NRL_CPFOB_SUBSTR','')
  if os.environ['NRL_CPFOB_BEGIND']=='':
    cpfbeg = 0
  else:
    cpfbeg = int(os.environ['NRL_CPFOB_BEGIND'])
  if os.environ['NRL_CPFOB_ENDIND']=='':
    cpfend=16
  else:
    cpfend = int(os.environ['NRL_CPFOB_ENDIND'])
  cdbstr = os.environ.get('NRL_CDBOB_SUBSTR','')
  if os.environ['NRL_CDBOB_BEGIND']=='':
    cdbbeg = 0
  else:
    cdbbeg = int(os.environ.get('NRL_CDBOB_BEGIND',0))
  if os.environ['NRL_CDBOB_ENDIND']=='':
    cdbend = 10
  else:
    cdbend = int(os.environ.get('NRL_CDBOB_ENDIND',10))

  # Filter based on user requested filter strings
  if qstr!='':
    print("\nFILTERING USING: %s" % (qstr))
    print("USING NEW FUNC")
    df.query(qstr,inplace=True)
  if cpfstr!='' and cdbstr!='':
    print("\nFILTERING c_pf_ob USING: %s from %02d to %02d & c_db_ob %s from %02d to %02d" % (cpfstr,cpfbeg,cpfend,cdbstr,cdbbeg,cdbend))
    df = df[df['c_pf_ob'].str.slice(start=cpfbeg,stop=cpfend,step=1).str.contains(cpfstr) & df['c_db_ob'].str.slice(start=cdbbeg,stop=cdbend,step=1).str.contains(cdbstr)]
  if cpfstr!='' and cdbstr=='':
    print("\nFILTERING c_pf_ob USING: %s from %02d to %02d" % (cpfstr,cpfbeg,cpfend))
    df = df[df['c_pf_ob'].str.slice(start=cpfbeg,stop=cpfend,step=1).str.contains(cpfstr)]
  if cpfstr=='' and cdbstr!='':
    print("\nFILTERING c_db_ob USING: %s from %02d to %02d" % (cdbstr,cdbbeg,cdbend))
    df = df[df['c_db_ob'].str.slice(start=cdbbeg,stop=cdbend,step=1).str.contains(cdbstr)]
  if qstr=='' and cpfstr=='' and cdbstr=='':
    print("\nNO FILTER. RETURNING ENTIRE FILE.")

  # Get the column headers and add one for "n" at the beginning
  hdrcols = hdr['column_titles']

  # Double check there are at least some variables set. The minimum required are LAT, LON, and OBS.
  if os.environ['NRL_LAT_STRING'] == '' or os.environ['NRL_LON_STRING'] == '' or os.environ['NRL_OBS_STRING'] == '' or\
     os.environ['NRL_TYP_STRING'] == '' or os.environ['NRL_LVL_STRING'] == '' or os.environ['NRL_VAR_STRING'] == '' or\
     os.environ['NRL_VLD_STRING'] == '':
    print("\nFATAL!\n\
           NRL_LAT_STRING,\n\
           NRL_LON_STRING,\n\
           NRL_OBS STRING,\n\
           NRL_TYP_STRING,\n\
           NRL_LVL_STRING,\n\
           NRL_VAR_STRING,\n\
           or NRL_VLD_STRING\n\
           are not set. All of these must be set.")
    exit(1)

  # Define a dictionary to map values from NRL to MET values
  nrl_met_map = {'typ':[os.environ['NRL_TYP_STRING']],
                 'sid':[os.environ['NRL_SID_STRING']],
                 'vld':[os.environ['NRL_VLD_STRING']],
                 'lat':[os.environ['NRL_LAT_STRING']],
                 'lon':[os.environ['NRL_LON_STRING']],
                 'elv':[os.environ['NRL_ELV_STRING']],
                 'var':[os.environ['NRL_VAR_STRING']],
                 'lvl':[os.environ['NRL_LVL_STRING']],
                 'hgt':[os.environ['NRL_HGT_STRING']],
                 'qc':[os.environ['NRL_QC_STRING']],
                 'obs':[os.environ['NRL_OBS_STRING']]}

  # Set the type of each column
  col_dtypes = {'typ':'str',
                'sid':'str',
                'vld':'int64',
                'lat':'float64',
                'lon':'float64',
                'elv':'float64',
                'var':'str',
                'lvl':'float64',
                'hgt':'float64',
                'qc':'str',
                'obs':'float64'}

  # The list of columns we want from the file is simply the values for each key in the nrl_met_map dict
  requestcols = [''.join(value) for value in nrl_met_map.values()]

  # Identify the index of each column in each line and assign it to the object
  requestinds = [x for x in range(len(hdrcols)) if hdrcols[x] in requestcols]

  # Get a list of the NRL column name strings in the order of requestinds
  nrlcols = [hdrcols[x] for x in requestinds]

  # Rename NRL columns to the names MET expects
  # List to hold MET column names for corresponding NRL names
  metcols = []
  # For each NRL column requested (in nrlcols), loop over it and find out what MET needs to call it
  for col in nrlcols:
    # For each dictionary cross-reference item
    found = False
    for key in nrl_met_map:
      # If the nrl column name is found in the values of this dictionary item, then the key of this dictionary
      # item is the MET column name to use
      if col in nrl_met_map[key]:
        found = True
        print("\nMAPPING %s [NRL] to %s [MET]" % (col,key))
        metcols.append(key)
    if not found:
      print("\nFATAL! Unable to assign [NRL] column name %s to [MET] column name" % (col))
      exit(1)

  # Drop all the columns we don't need anymore
  df.drop(df.columns.difference(nrlcols), 1, inplace=True)

  # Replace the NRL column names with the MET column names
  df.columns = metcols

  # Handle unset options (if any)
  if os.environ['NRL_SID_STRING']=='':
    print("\nUSING DEFAULT VALUE FOR [MET] sid")
    df['sid'] = ['NA'] * len(df)
  if os.environ['NRL_ELV_STRING']=='':
    print("\nUSING DEFAULT VALUE FOR [MET] elv")
    df['elv'] = ['-9999'] * len(df)
  if os.environ['NRL_HGT_STRING']=='':
    print("\nUSING DEFAULT VALUE FOR [MET] hgt")
    df['hgt'] = ['-9999'] * len(df)
  if os.environ['NRL_QC_STRING']=='':
    print("\nUSING DEFAULT VALUE FOR [MET] qc")
    df['qc'] = ['NA'] * len(df)

  # Convert the column dtypes
  df = df.astype(col_dtypes)

  # Handle time. This is computed as cdtg_bk + tau_bk from the header, and then adding the offset (idt) in seconds
  print("\nCOMPUTING [MET] vld from [NRL] cdtg_bk, tau_bk, and idt")
  cdtg_bk = datetime.datetime.strptime(hdr['cdtg_bk'],'%Y%m%d%H')
  df['center'] = [cdtg_bk+datetime.timedelta(seconds=int(hdr['tau_bk'])*3600)] * len(df)
  df['vld'] = pd.to_datetime((df['center']+pd.to_timedelta(df['vld'],unit='S'))).dt.strftime('%Y%m%d_%H%M%S')

  # Convert the time column to a string
  df = df.astype({'vld':'str'})

  # Reorder columns so they are in the order MET expects
  df = df[list(nrl_met_map.keys())]

  # Return the dataframe 
  return df

class InnovationFileError(Exception): pass

class HeaderParseError(InnovationFileError): pass

class InnovationFile(abc.ABC):
    """The abstract class that defines which methods should be implemented"""
    @abc.abstractmethod
    def read_innov_header(self, filename):
        pass

class ASCIIInnovationFile(InnovationFile):
    def __init__(self, filename=None):
        self.file = open(filename, "rt") 
        self.read_innov_header(self.file)

    def read_innov_header(self, file):
        self.header = {}

        # innovation file start with one blank line
        next(file)

        # innovation file grid parameters read header data (metadata)
        for line in file:
            if not line.strip():
                # last line of section is blank
                break
            # retrieve header element
            #var_name, _, var_value = line.strip().partition("=")
            var_name, var_value =  line.strip().split("=",1)
            self.header[var_name.strip()] = var_value.strip()

        # skip "pranal" line
        next(file)

        # read "pressure" lines
        pressures = []
        for line in file:
            if not line.strip():
                # last line of section is blank
                break
            # retrieve pressure level
            pressures.append(float(line.strip()))


        # "n_boxm" line
        line = next(file)        
        #var_name, _, var_value = line.strip().partition("=")
        var_name, var_value =  line.strip().split("=",1)
        self.header[var_name.strip()] = int(var_value.strip())

        # skip ne_ob and subsequent line
        next(file)
        next(file)


        # General pattern for recognizing an assignment statement
        assign_pattern = lambda key, name, pattern: r'%s\s*=\s*(?P<%s>%s)' % (key, name, pattern)
        line_pattern = r'\s*'.join([assign_pattern(r'number of obs', r'num_obs', r'\d+'),
                                    assign_pattern(r'cdtg_bk', r'cdtg_bk', r'\d{10}'),
                                    assign_pattern(r'tau_bk', r'tau_bk', r'\d+')])  # will not work for fractional taus

        # "number of obs", "cdtg_bk" and "tau_bk" line
        line = next(file)
        match = re.search(line_pattern, line)
        if not match:
            raise HeaderParseError('failed to parse "number of obs" line')
        for group_name in ('num_obs', 'cdtg_bk', 'tau_bk'):
            self.header[group_name] = match.group(group_name)

        self.header['column_titles'] = next(file).strip().split()

        return self.header

    def _parse_innovation_line(self, line):
            temp = list(line)
            temp.insert(43, ' ')                  # separate column "xiv_ob" and "err_ob"
            c_pf = temp[123:139]                  # get column "c_pf_ob"
            c_db = temp[141:151]                  # get column "c_db_ob"
            del temp[123:151]
            temp_line = ''.join(str(t) for t in temp)

            contents = temp_line.split()
            contents.insert(15, "".join(str(p) for p in c_pf))    # insert columns "c_pf_ob" and "c_db_ob"
            contents.insert(16, "".join(str(d) for d in c_db))

            return contents

    def __iter__(self):
        for line in self.file:
            yield self._parse_innovation_line(line)

    def as_dataframe(self):

      # NRL dtypes, based on H5InnovationFile class
      innovdtypes = ['int64','float64','float64','float64','float64','float64','float64','object','object','float64',\
                     'int64','int64','object','int64','int64','object','object','int64','int64','float64','float64',\
                     'float64']
      innovdict = {self.header['column_titles'][i]:innovdtypes[i] for i in range(len(innovdtypes))}
      line_list = [list(self._parse_innovation_line(line)) for line in self.file]
      df = pd.DataFrame(line_list,columns=self.header['column_titles'])
      return df.astype(innovdict)

    def as_met_dataframe(self):

      df = create_met_dataframe(self.as_dataframe(),self.header)
      return df
      
class BZInnovationFile(ASCIIInnovationFile):
    def __init__(self, filename):
        self.file = bz2.BZ2File(filename, "rt")
        self.read_innov_header(self.file)

class GZInnovationFile(ASCIIInnovationFile):
    def __init__(self, filename):
        self.file = gzip.open(filename, "rt")
        self.read_innov_header(self.file)

class H5InnovationFile(InnovationFile):
    def __init__(self, filename):
        self.file = h5py.File(filename,'r')
        self.read_innov_header(self.file)

    def read_innov_header(self, file):
        self.header = {}
        self.header['igrid'] = file['metadata_integer'][2]
        self.header['iref'] = file['metadata_integer'][3]
        self.header['jref'] = file['metadata_integer'][4]
        self.header['im'] = file['metadata_integer'][5]
        self.header['jm'] = file['metadata_integer'][6]
        self.header['lm'] = file['metadata_integer'][7]
        self.header['reflat'] = file['metadata_real'][100]
        self.header['reflon'] = file['metadata_real'][101]
        self.header['stdlt1'] = file['metadata_real'][102]
        self.header['stdlt2'] = file['metadata_real'][103]
        self.header['stdlon'] = file['metadata_real'][104]
        self.header['delx'] = file['metadata_real'][105]
        self.header['dely'] = file['metadata_real'][106]
        self.header['n_boxm'] = 1 
        self.header['num_obs'] = file['metadata_integer'][0]
        self.header['cdtg_bk'] = '{}{}{}{}'.format(file['metadata_integer'][10],file['metadata_integer'][11],file['metadata_integer'][12],file['metadata_integer'][13])
        self.header['tau_bk'] = file['metadata_integer'][1]
        self.header['column_titles'] = ['ob', 'bk_ob', 't_bk_ob', 'xiv_ob', 'err_ob', 'etc_ob', 'lat_ob', 'lon_ob', \
                                        'p_ob', 'jvar', 'insty', 'nvp', 'ichk', 'idt', 'c_pf_ob', 'c_db_ob', \
                                        'idp', 'lsi', 'rej', 'bkerr', 'cob', 'resid', 'sig_e']
        return self.header

    def __iter__(self):
        n_arr=np.array(self.file['INNOV']['n'])
        ob_arr=np.array(self.file['INNOV']['ob'])
        bk_arr=np.array(self.file['INNOV']['bk'])
        t_bk_arr=np.array(self.file['INNOV']['t_bk'])
        xiv_arr=np.array(self.file['INNOV']['xiv'])
        err_arr=np.array(self.file['INNOV']['err'])
        etc_arr=np.array(self.file['INNOV']['etc'])
        lat_arr=np.array(self.file['INNOV']['lat'])
        lon_arr=np.array(self.file['INNOV']['lon'])
        p_ob_arr=np.array(self.file['INNOV']['p_ob'])
        jvar_arr=np.array(self.file['INNOV']['jvar'])
        insty_arr=np.array(self.file['INNOV']['insty'])
        nvp_arr=np.array(self.file['INNOV']['nvp'])
        ichk_arr=np.array(self.file['INNOV']['ichk'])
        idt_arr=np.array(self.file['INNOV']['idt'])
        c_pf_ob_arr=np.array(self.file['INNOV']['c_pf_ob'])
        c_db_ob_arr=np.array(self.file['INNOV']['c_db_ob'])
        idp_arr=np.array(self.file['INNOV']['idp'])
        lsi_arr=np.array(self.file['INNOV']['lsi'])
        rej_arr=np.array(self.file['INNOV']['rej'])
        bkerr_arr=np.array(self.file['INNOV']['bkerr'])
        cob_arr=np.array(self.file['INNOV']['cob'])
        resid_arr=np.array(self.file['INNOV']['resid'])
        num_innovs=len(n_arr)
        # the following variables are responsible for keeping track of repeated lat and lon values
        # lat,lon,c_pf_ob and c_db_ob were previously read as strings so they need to be cast as strings.
        counter = 0
        nvp = 0
        nvp_idx = 0
        lat = str(lat_arr[nvp_idx])
        lon = str(lon_arr[nvp_idx])
        for i in range(0, num_innovs):
            if counter >= nvp:
                nvp = nvp_arr[nvp_idx]
                lat = str(lat_arr[nvp_idx])
                lon = str(lon_arr[nvp_idx])
                counter = 0
                nvp_idx += 1
            counter += 1
            yarray = [ob_arr[i],bk_arr[i],t_bk_arr[i],xiv_arr[i],err_arr[i],etc_arr[i],lat,lon,p_ob_arr[i],jvar_arr[i],insty_arr[i],str(nvp),ichk_arr[i],idt_arr[i],(c_pf_ob_arr[i]).decode('utf-8'),(c_db_ob_arr[i]).decode('utf-8'),idp_arr[i],lsi_arr[i],rej_arr[i],bkerr_arr[i],cob_arr[i],resid_arr[i],1]
            yield [yarray[x] for x in self.inds]

    def as_dataframe(self):

      # Get the column headers
      hdrcols = self.header['column_titles']

      # Assign the index of each column in each line to the object
      self.inds = list(range(len(hdrcols)))

      # Collect each line and store in a dataframe
      line_list = [list(data) for data in self]
      df = pd.DataFrame(line_list,columns=hdrcols)

      # Return the dataframe
      return df

    def as_met_dataframe(self):

      df = create_met_dataframe(self.as_dataframe(),self.header)
      return df

def from_file(filename):
    """Factory method for instantiating innovation object."""
    basename, extension = os.path.splitext(filename)
    if extension == '.gz':
        return GZInnovationFile(filename)
    elif extension == '.bz2':
        return BZInnovationFile(filename)
    elif extension == '.h5':
        return H5InnovationFile(filename)
    else:
        return ASCIIInnovationFile(filename)

