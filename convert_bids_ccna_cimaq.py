#!/usr/bin/env python
# encoding: utf-8

import argparse
import glob
import logging
import os
import sys
import tarfile

SIEMENS = ['Prisma_fit', 'TrioTim', 'Prisma', 'Skyra']
GE = ['DISCOVERY_MR750', 'SIGNA_Pioneer', 'DISCOVERY_MR750w', 'Signa_HDxt']
PHILIPS = ['Intera', 'Achieva', 'Ingenia', 'Achieva_dStream']

CONFIG_FOLDER = '/home/bore/p/unf/s/bids_conversion/configs'

MAIN_CONFIG = os.path.join(CONFIG_FOLDER, 'config.json')
#GE_CONFIG = os.path.join(CONFIG_FOLDER, 'config_ge_cimaq.json')
#SIEMENS_CONFIG = os.path.join(CONFIG_FOLDER, 'config_siemens_cimaq.json')
#PHILIPS_CONFIG = os.path.join(CONFIG_FOLDER, 'config_philips_cimaq.json')
# QUEBEC_CONFIG = os.path.join(CONFIG_FOLDER, 'config_philips_cimaq_QC.json')

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

    parser.add_argument("mode", default='ccna',
                        help="Mode CCNA or CIMAQ")

    parser.add_argument(
        '--log_level', default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Log level of the logging class.')

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    else:
        return parser


class IRMSession:
    def __init__(self, filename, patient_name, patient_id, patient_date,
                 scan_date, patient_sex, scanner_model, scanner_version,
                 institution, mode):
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
        self.mode = mode

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
        self.session = self.get_session(patient_name.split('_')[2])  # visit label

        self.scanner_manufacturer = self.getManufacturer()
        self.config = os.path.join(CONFIG_FOLDER ,self.get_config())

    def get_session(self, session):
        if self.mode == 'ccna':
            if session == 'Initial':
                return 1
            else:
                logging.error('{} - {} session wont be converted.'.format(self.filename,
                                                                          session))
                return 2
        elif self.mode == 'cimaq':
            return session

    def getManufacturer(self):
        if self.scanner_model in SIEMENS:
            return 'siemens'
        elif self.scanner_model in PHILIPS:
            return 'philips'
        elif self.scanner_model in GE:
            return 'ge'
        else:
            print(self.scanner_model)

    def get_config(self):
        if self.mode == 'ccna':
            return 'config_{}_{}.json'.format(self.scanner_manufacturer,
                                                 self.mode)
        elif self.mode == 'cimaq':
            return 'config_{}_{}_{}.json'.format(self.scanner_manufacturer,
                                                 self.mode,
                                                 self.institution)

    def show(self):
        print('#############')
        print('# Subject: {}'.format(self.patient_name))
        print('# Input file: {}'.format(self.filename))
        print('# Scanner Model: {}'.format(self.scanner_model))
        print('# Institution: {}'.format(self.institution))
        print('#############')

    def showOneLine(self, all=False):
        if all:
            print('{},{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(self.filename,
                                             self.patient_name,
                                             self.patient_id,
                                             self.patient_birthdate,
                                             self.patient_sex,
                                             self.scan_date,
                                             self.candid,
                                             self.pscid,
                                             self.session,
                                             self.institution,
                                             self.scanner_manufacturer,
                                             self.scanner_model,
                                             self.mode,
                                             self.config))

        else:
            print('{},{},{},{},{},{}'.format(self.pscid,
                                             self.session,
                                             self.institution,
                                             self.scanner_manufacturer,
                                             self.scanner_model,
                                             self.filename))


    def extract(self):
        tarname= self.filename + '.tar.gz'
        if not os.path.exists(self.filename):
            #print('-> Extraction {}'.format(tarname))
            iTar = tarfile.open(name=tarname, mode='r|gz')
            iTar.extractall(self.filename)
        #else:
        #    print('-> Already extracted {}'.format(tarname))


    def delete_filename(self):
            cmd = 'rm -rf {}'.format(self.filename)
            os.system(cmd)


    def convert(self, bidsOutput):
        cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(self.filename,
                                                              self.pscid,
                                                              self.session,
                                                              MAIN_CONFIG,
                                                              bidsOutput)
        print(cmd)
        #os.system(cmd)

        if self.mode == 'ccna':
            cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(self.filename,
                                                                  self.pscid,
                                                                  self.session,
                                                                  self.config,
                                                                  bidsOutput)
            print(cmd)
            #os.system(cmd)
        elif self.mode == 'cimaq':
            if self.institution == 'IUGM' or\
                'hospital_douglas':
                cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(self.filename,
                                                                      self.candid,
                                                                      self.session,
                                                                      self.config,
                                                                      bidsOutput)
                os.system(cmd)

            elif self.institution != 'CINQ' and\
                'Quebec' not in self.institution and\
                self.scanner_manufacturer == 'philips':
                cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(self.filename,
                                                                      self.candid,
                                                                      self.session,
                                                                      PHILIPS_CONFIG,
                                                                      bidsOutput)
                os.system(cmd)


            elif self.scanner_manufacturer == 'philips':
                cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(self.filename,
                                                                      self.candid,
                                                                      self.session,
                                                                      QUEBEC_CONFIG,
                                                                      bidsOutput)
                os.system(cmd)

            elif self.scanner_manufacturer == 'ge':
                cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(self.filename,
                                                                      self.candid,
                                                                      self.session,
                                                                      GE_CONFIG,
                                                                      bidsOutput)
                os.system(cmd)

            elif self.institution == 'Mc_Connell_Brain_Imaging_Centre':
                cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(self.filename,
                                                                      self.candid,
                                                                      self.session,
                                                                      self.config,
                                                                      bidsOutput)
                os.system(cmd)

            elif self.institution is 'hospital_douglas' or\
                                     'THE_OTTAWA_HOSPITAL_CIVIC' or\
                                     'the_ottawa_hospital_civic_campus' or\
                                     'Mc_Connell_Brain_Imaging_Centre':
                cmd = 'dcm2bids -d {} -p {} -s {} -c {} -o {}'.format(self.filename,
                                                                      self.candid,
                                                                      self.session,
                                                                      self.config,
                                                                      bidsOutput)
                os.system(cmd)

            else:
                print('--> {} not converted, {} - institution'.format(self.filename,
                                                                      self.institution))


def read_metas(iFolder, mode):
    metas = []
    allFiles = glob.glob(os.path.join(iFolder,'**/*.meta'), recursive=True)
    allFiles.sort()
    for iFile in allFiles:

        patient_name=None
        patient_id=None
        patient_date=None
        scan_date=None
        patient_sex=None
        scanner_model=None
        scanner_version=None
        institution=None

        fp = open(iFile)
        for i, line in enumerate(fp):
            if '*' == line[0]:
                answer = line.split(':')[1].strip()
                answer = answer.replace(' ','_')
                if answer.isspace() or answer=='':
                    continue

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
                    institution = str(answer).lower()
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
                                institution,
                                mode))

    return metas


def extract_main_tar(i_tar_filename, oFolder):
    i_basename, i_extension = os.path.splitext(i_tar_filename)
    o_folder_name = os.path.join(oFolder, i_basename)

    if not os.path.exists(o_folder_name):
        print('-> Extraction {}'.format(i_tar_filename))
        iTar = tarfile.open(name=i_tar_filename, mode='r')
        iTar.extractall(o_folder_name)
    else:
        print('{} already exists' .format(o_folder_name))


def extract_unique_dataset(metas):
    """
    Input:

    metas: List

    """
    list_of_metas = []
    for nMeta in metas:
            list_of_metas.append((nMeta.institution,
                                  nMeta.scanner_model,
                                  nMeta.scanner_manufacturer,
                                  nMeta.scanner_version))
    indexes = []
    uniqueMetas = list(set(list_of_metas))
    for uniqueMeta in uniqueMetas:
        for curr_index, meta in enumerate(list_of_metas):
            if uniqueMeta == meta:
                indexes.append(curr_index)
                break

    for curr_index in indexes:
        metas[curr_index].showOneLine()


def check_mode(parser, mode):
    if not mode in ['ccna','cimaq']:
        parser.error('{} mode is not valid (ccna or cimaq).'.format(mode))


def main():
    parser = get_arguments()
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)

    check_mode(parser, args.mode)

    all_tar_files = glob.glob(os.path.join(args.iFolder,'*tar'))
    all_tar_files.sort()
    for curr_tar_file in all_tar_files:
        extract_main_tar(curr_tar_file, args.oFolder)

    subjects = read_metas(args.iFolder, args.mode)

    for sub in subjects:
        #sub.showOneLine()
        if sub.scanner_manufacturer == 'philips':
            #print(sub.candid, sub.pscid)
            sub.extract()
            sub.convert('/home/bore/p/o_ccna')
            #sub.delete_filename()


if __name__ == '__main__':
    sys.exit(main())
