#!/usr/bin/env python
# encoding: utf-8

import argparse
import glob
import logging
import os
import sys
import tarfile

SIEMENS = ['Prisma_fit', 'TrioTim', 'Prisma', 'Skyra']
GE = ['DISCOVERY MR750', 'SIGNA Pioneer']
PHILIPS = ['Intera', 'Achieva', 'Ingenia', 'Achieva dStream']

CONFIG_FOLDER = '/home/bore/p/unf/s/bids_conversion/configs'

MAIN_CONFIG = os.path.join(CONFIG_FOLDER, 'config.json')
GE_CONFIG = os.path.join(CONFIG_FOLDER, 'config_ge_cimaq.json')
SIEMENS_CONFIG = os.path.join(CONFIG_FOLDER, 'config_siemens_cimaq.json')
PHILIPS_CONFIG = os.path.join(CONFIG_FOLDER, 'config_philips_cimaq.json')
QC_CONFIG = os.path.join(CONFIG_FOLDER, 'config_philips_cimaq_QC.json')

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
        self.config = os.path.join(CONFIG_FOLDER ,self.getConfig())

    def getManufacturer(self):
        if self.scanner_model in SIEMENS:
            return 'siemens'
        elif self.scanner_model in PHILIPS:
            return 'philips'
        elif self.scanner_model in GE:
            return 'ge'
        else:
            print(self.scanner_model)

    def getConfig(self):
        return 'config_{}_ccna_{}.json'.format(self.scanner_manufacturer,
                                                self.institution)

    def show(self):
        print('#############')
        print('# Subject: {}'.format(self.patient_name))
        print('# Input file: {}'.format(self.filename))
        print('# Scanner Model: {}'.format(self.scanner_model))
        print('# Institution: {}'.format(self.institution))
        print('#############')

    def showOneLine(self):
        print('{},{},{},{},{},{}'.format(self.pscid,
                                           self.session,
                                           self.institution,
                                           self.scanner_manufacturer,
                                           self.scanner_model,
                                           self.filename))

def readMeta(iFolder):
    metas = []
    allFiles = glob.glob(os.path.join(iFolder,'*meta'))
    allFiles.sort()
    for iFile in allFiles:
        #print('Read {}'.format(iFile))
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
                    scanner_model = answer.replace(' ','_')
                elif 'Scanner Software Version' in line:
                    scanner_version = answer
                elif 'Institution Name' in line:
                    tmp_institution = answer.replace(' ','_')
                    if not tmp_institution.isspace() or tmp_institution:
                        institution = lower(tmp_institution)
                        print(institution + 'HERE')
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
    if not os.path.exists(sub.filename):
        print('-> Extraction {}'.format(tarname))
        iTar = tarfile.open(name=tarname, mode='r|gz')
        iTar.extractall()
    else:
        print('-> Already extracted {}'.format(tarname))

def deleteArchive(sub):
    cmd = 'rm -rf {}'.format(sub.filename)
    os.system(cmd)


def convert(sub, bidsOutput):
    cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(sub.filename,
                                                          sub.pscid,
                                                          sub.session,
                                                          MAIN_CONFIG,
                                                          bidsOutput)
    os.system(cmd)

    if sub.institution == 'IUGM':
        cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(sub.filename,
                                                              sub.pscid,
                                                              sub.session,
                                                              sub.config,
                                                              bidsOutput)
        os.system(cmd)

    elif sub.institution == 'Hospital_Douglas':
        cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(sub.filename,
                                                              sub.pscid,
                                                              sub.session,
                                                              sub.config,
                                                              bidsOutput)
        os.system(cmd)

    elif sub.institution != 'CINQ' and 'Quebec' not in sub.institution and sub.scanner_manufacturer == 'philips':
        cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(sub.filename,
                                                              sub.pscid,
                                                              sub.session,
                                                              PHILIPS_CONFIG,
                                                              bidsOutput)
        os.system(cmd)


    elif sub.scanner_manufacturer == 'philips':
        cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(sub.filename,
                                                              sub.pscid,
                                                              sub.session,
                                                              QC_CONFIG,
                                                              bidsOutput)
        os.system(cmd)

    elif sub.scanner_manufacturer == 'ge':
        cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(sub.filename,
                                                              sub.pscid,
                                                              sub.session,
                                                              GE_CONFIG,
                                                              bidsOutput)
        os.system(cmd)

    elif sub.institution == 'Mc_Connell_Brain_Imaging_Centre':
        cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(sub.filename,
                                                              sub.pscid,
                                                              sub.session,
                                                              sub.config,
                                                              bidsOutput)
        os.system(cmd)

    elif sub.institution is 'Hospital_Douglas' or 'THE_OTTAWA_HOSPITAL_CIVIC':
        cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(sub.filename,
                                                              sub.pscid,
                                                              sub.session,
                                                              sub.config,
                                                              bidsOutput)
        os.system(cmd)


def main():
    args = get_arguments()
    logging.basicConfig(level=args.log_level)
    subjects = readMeta(args.iFolder)
    subjects.sort(key=lambda x: x.pscid, reverse=False)
    for sub in subjects:
        #if sub.session=='V3':
        #    sub.session = 'V03'
        #sub.showOneLine()
        sub.show()
        #extract(sub)
        #convert(sub, args.oFolder)
        #deleteArchive(sub)



if __name__ == '__main__':
    sys.exit(main())
