#!/usr/bin/env python3
''' 
format file for gcta, append freq and n if need and bfile
'''
from  subprocess import CalledProcessError
import subprocess
import os
import argparse
import numpy as np
import pandas as pd
import sys

EOL = chr(10)
#SNP A1 A2 freq b se p N 
def parseArguments():
    parser = argparse.ArgumentParser(description='format file for gcta, append N and frequencie if not present using bed file')
    parser.add_argument('--inp_asso',type=str,required=True, help="association files")
    parser.add_argument('--out', type=str,help="out of tex file",default="test.tex")
    parser.add_argument('--rs_header',type=str,required=True,help="rs header in inp files")
    parser.add_argument('--pval_header',type=str,required=True,help="pvalue header in inp files")
    parser.add_argument('--freq_header',type=str,required=False,help="freq header in inp files",default=None)
    parser.add_argument('--a1_header',type=str,required=True,help="a1 header in inp files")
    parser.add_argument('--a2_header',type=str,required=True,help="a2 header in inp files")
    parser.add_argument('--se_header',type=str,required=True,help="se header in inp files")
    parser.add_argument('--n_header',type=str,help="n header in inp files", default=None)
    parser.add_argument('--chr',type=str,help="n header in inp files", default=None)
    parser.add_argument('--chro_header',type=str,help="n header in inp files", default="")
    parser.add_argument('--beta_header',type=str,required=True,help="beta header in inp files")
    parser.add_argument('--bin_plk',type=str,required=False,help="plink binary", default="plink")
    parser.add_argument('--bfile',type=str,required=False,help="bfile if need to compute frequency or N", default=None)
    parser.add_argument('--keep',type=str,required=False,help="file of data used for if need to compute frequency or N", default=None)
    parser.add_argument('--threads',type=int,required=False,help="", default=1)
    args = parser.parse_args()
    return args

args = parseArguments()
inp     = args.inp_asso

rs_head=args.rs_header
beta_head=args.beta_header
freq_head=args.freq_header
pval_head=args.pval_header
se_head=args.se_header
a1_head=args.a1_header
a2_head=args.a2_header
se_head=args.se_header
n_head=args.n_header

## first step : if
result = pd.read_csv(inp,delim_whitespace=True)
result[args.chro_header] = result[args.chro_header].astype(str)
if args.n_header==None or args.freq_header==None :
   plkfreqfil=os.path.basename(args.bfile)
   if args.bfile==None :
     print("no header for n or freq and bfile")
     sys.exit()
   Cmd=args.bin_plk+" -bfile "+args.bfile+" --freq --keep-allele-order "
   if args.chr :
     Cmd+=" --chr "+args.chr
     plkfreqfil=plkfreqfil+"_"+args.chr
   if args.keep :
     Cmd+=" --keep "+args.keep
   Cmd+=" --threads "+str(args.threads)
   Cmd+=" --out "+plkfreqfil
   os.system(Cmd)
   data_n=pd.read_csv(plkfreqfil+".frq",delim_whitespace=True)
   # CHR            SNP   A1   A2          MAF  NCHROBS
   #SNP A1 A2 freq b se p N
   data_n['N']=data_n['NCHROBS']/2
   if args.n_header==None and args.freq_header : 
      data_n=data_n[["SNP","MAF","N"]]
      freq_head="MAF"
      n_head="N"
   elif args.n_header==None :
      data_n=data_n[["SNP","N"]]
      n_head="N"
   elif args.freq_header==None :
      data_n=data_n[["SNP","MAF"]]
      freq_head="MAF"
   result=result.merge(data_n,how="left", on=rs_head)


if args.chr :
   result=result[result[args.chro_header]==args.chr]


result=result[[rs_head, a1_head,a2_head,freq_head,beta_head, se_head,pval_head, n_head]]
result.columns=["SNP","A1","A2","freq","b","se","p","N"]

result.to_csv(args.out,sep=" ",header=True,index=False,na_rep="NA")


