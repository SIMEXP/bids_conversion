#!/usr/bin/env python
# encoding: utf-8

import argparse
import glob
import logging
import os
import sys
import tarfile

SIEMENS = ['Prisma_fit', 'TrioTim', 'Prisma', 'Skyra']
GE = ['DISCOVERY MR750','SIGNA Pioneer']
PHILIPS = ['Intera','Achieva','Ingenia']

CONFIG_FOLDER = '/home/bore/p/unf/s/bids_conversion_cimaq/configs'
MAIN_CONFIG = os.path.join(CONFIG_FOLDER, 'config.json')


def get_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="",
        epilog="""
        Convert CIMAQ release to bids format
        Input: Folder with zip files
        """)

    parser.add_argument(
        "iFolder",
        help="Folder to be sorted")

    parser.add_argument(
        "oFolder",
        help="Output folder - if doesn\'t exist it will be created.")

    parser.add_argument(
        '--log_level', default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Log level of the logging class.')

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    else:
        return args


class IRMSession:
    def __init__(self, filename, patient_name, patient_id, patient_date,
                 scan_date, patient_sex, scanner_model, scanner_version,
                 institution):
        #  lineer
        #  (0, '<STUDY>\n')
        #  (L1, '<STUDY_INFO>\n')
        #  (L2, '* Unique Study ID
        #  (L3, '* Patient Name
        #  (L4, '* Patient ID
        #  (L5, '* Patient date of birth
        #  (L6, '* Scan Date
        #  (L7, '* Patient Sex
        #  (L8, '* Scanner Model Name
        #  (L9, '* Scanner Software Version
        #  (L10, '* Institution Name
        #  (L11, '* Modality
        #  (L12, '</STUDY_INFO>\n')
        self.filename = filename.split('.meta')[0]

        self.patient_name = patient_name
        self.patient_id = patient_id
        self.patient_birthdate = patient_date
        self.patient_sex = patient_sex

        self.scan_date = scan_date
        self.scanner_model = scanner_model
        self.scanner_version = scanner_version
        self.institution = institution

        self.pscid = patient_name.split('_')[0]  # participant ID 7 chiffres
        self.candid = patient_name.split('_')[1]  # participant ID loris 6 chiffres
        self.session = patient_name.split('_')[2]  # visit label

        self.scanner_manufacturer = self.getManufacturer()
        self.config = self.getConfig()

    def getManufacturer(self):
        if self.scanner_model in SIEMENS:
            return 'siemens'
        elif self.scanner_model in PHILIPS:
            return 'philips'

    def getConfig(self):
        return 'config_{}_{}.json'.format(self.scanner_manufacturer,
                                     self.institution)

    def show(self):
        print('#############')
        print('# Subject: {}'.format(self.patient_name))
        print('# Input file: {}'.format(self.filename))
        print('#############')


def readMeta(iFolder):
    metas = []
    for iFile in glob.glob(os.path.join(iFolder,'*meta')):
        print('Read {}'.format(iFile))
        fp = open(iFile)
        for i, line in enumerate(fp):
            if '*' == line[0]:
                answer = line.split(':')[1].strip()
                if 'Patient Name' in line:
                    patient_name = answer
                elif 'Patient ID' in line:
                    patient_id = answer
                elif 'Patient date of birth' in line:
                    patient_date = answer
                elif 'Scan Date' in line:
                    scan_date = answer
                elif 'Patient Sex' in line:
                    patient_sex = answer
                elif 'Scanner Model Name' in line:
                    scanner_model = answer
                elif 'Scanner Software Version' in line:
                    scanner_version = answer
                elif 'Institution Name' in line:
                    institution = answer.replace(' ','_')
            elif '<FILES>' in line:
                break
        fp.close()

        metas.append(IRMSession(iFile,
                                patient_name,
                                patient_id,
                                patient_date,
                                scan_date,
                                patient_sex,
                                scanner_model,
                                scanner_version,
                                institution))

    return metas

def extract(sub):
    tarname= sub.filename + '.tar.gz'
    print('-> Extraction {}'.format(tarname))
    iTar = tarfile.open(name=tarname, mode='r|gz')
    iTar.extractall()



def convert(sub, bidsOutput):
    cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(sub.filename,
                                                          sub.pscid,
                                                          sub.session,
                                                          MAIN_CONFIG,
                                                          bidsOutput)
    os.system(cmd)
    print(cmd)

    cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(sub.filename,
                                                          sub.pscid,
                                                          sub.session,
                                                          sub.config,
                                                          bidsOutput)

    print(cmd)

def main():
    args = get_arguments()
    logging.basicConfig(level=args.log_level)
    subjects = readMeta(args.iFolder)

    for sub in subjects:
        sub.show()
        extract(sub)
        convert(sub, args.oFolder)


if __name__ == '__main__':
    sys.exit(main())
