# bids_conversion
Script to help convert dicom to bids from CCNA or CIMAQ using dcm2bids

Requirements
* requirements.txt (pip install -r requirements.txt)
* dcm2bids (https://github.com/UNFmontreal/Dcm2Bids)
* dcm2niix (https://github.com/rordenlab/dcm2niix)

Run (two steps)
* python3 convert_bids_ccna_cimaq.py /dicom_directory /output_directory mode (ccna or cimaq) > file
* bash ./file

Tips
* dicom_directory must contain the tarchive files (usually found in /data/$PROJECT/data/tarchive)
* the output file will contain the untar tarchive files, the bids files (sub-PSCID/CandID) and a sub-folder containing the log and failed conversion
* tweaking of the config files will be required
*  If you're splitting your bundle into smaller ones, make sure all of a participant's files are grouped together. If not, you will have to reorganize the tree manually 
