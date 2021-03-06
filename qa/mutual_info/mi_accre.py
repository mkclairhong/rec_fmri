from __future__ import division
import numpy as np
import mi
import os
from tabulate import tabulate


def avg_mi_coreg(subjID, type='rtf', saveText=True, verbose=False, nScans=187, resDir='/scratch/polynlab/fmri/cdcatmr/all_subjects/mutual_info'):
    """
    used for comparing registration types by calculating the correlation coefficient
    and mutual information of the registered image to the rest of image files,
    and returns the averages of each trial and the grand average

    Parameters
    ----------
    subjID : str
        string of subject data (ie. 'cdcatmr011')
    type : str ['rtf', 'rtm'] (default: 'rtf')
        registration type that would either register to first scan image or the mean image
    saveText : boolean (default: True)
        if True, will save the table report to a separate text file
    verbose : boolean (default: False)
        if True, will print out which scan file is being worked on
    nScans : int (default: 187)
        integer of how many scans to expect per each run
    resDir : str/abs path (default is set to scratch project dir)
        string of absolute path to save the resulted text report

    Returns
    -------
    cc_all: list
        list of all correlation coefficient values
    mi_all: list
        list of all mutual information values

    """
    saveText = bool(saveText)
    subj = str(subjID)
    baseDir = '/scratch/polynlab/fmri/cdcatmr/'
    funcDir = baseDir + subj + '/images/func'
    # tag = 'func'
    if type == 'rtf':  # register to first
        sourceImg = '/func1/func1_00001.nii'  # [rmeanfunc1_00001.nii, meanfunc1_00001.nii]
        # tag = 'func'
    elif type == 'rtm':  # register to mean
        sourceImg = '/func1/meanfunc1_00001.nii'
        # tag = 'rfunc'
    tag = 'func'
    resDir = resDir

    os.chdir(funcDir)
    funcs = os.listdir(funcDir)
    funcs.sort()  # funcs = ['func1', 'func2', ... 'func7', 'func8']

    meanImg = mi.get_img_slice(funcDir + sourceImg, verbose=verbose)
    mi_listVar = []
    cc_listVar = []
    # loop by each functional run
    for i in range(0, len(funcs)):
        curr_func = funcs[i]
        # let's first create list variables for each functional run
        temp = ''
        temp = 'mi_' + curr_func + ' = []'
        exec(temp)
        mi_listVar.append('mi_' + curr_func)
        temp = ''
        temp = 'cc_' + curr_func + ' = []'
        exec(temp)
        cc_listVar.append('cc_' + curr_func)

        # now let's read in each functional run folder
        cfuncDir = funcDir + '/' + curr_func
        os.chdir(cfuncDir)
        nii_files = os.listdir(cfuncDir)
        nii_files = [x for x in nii_files if x.startswith(tag) and x.endswith('nii')]
        nii_files.sort()

        # sanity check: count scan files
        assert len(nii_files) == nScans, "total scan files found do not match " + str(nScans) + " for func run " + str(i+1)

        # loop by each scan within run
        for j in range(0, nScans):
            if verbose:
                print('starting ' + curr_func + ' | scan ' + str(j+1))
            curr_nii = mi.get_img_slice(nii_files[j], verbose=verbose)
            corr = mi.get_core(meanImg, curr_nii)
            mutual_info = mi.mutual_information(meanImg, curr_nii)

            # append each list
            temp_cc = 'cc_' + curr_func + '.append(corr)'
            exec(temp_cc)
            temp_mi = 'mi_' + curr_func + '.append(mutual_info)'
            exec(temp_mi)

    cc_sums = []
    mi_sums = []
    for r in range(0, len(funcs)):
        cc_sums.append(sum(eval(cc_listVar[r])))
        mi_sums.append(sum(eval(mi_listVar[r])))

    # get all entries in a single list
    cc_all = []
    mi_all = []
    for r in range(0, len(funcs)):
        cc_all = cc_all + eval(cc_listVar[r])
        mi_all = mi_all + eval(mi_listVar[r])


    reports = []
    reports.append(['avg cc', sum(cc_sums)/(nScans*len(funcs))])
    reports.append(['avg mi', sum(mi_sums)/(nScans*len(funcs))])
    reports.append(['cc by runs', '-----'])
    for l in cc_listVar:
        reports.append([l, sum(eval(l))/nScans])
    reports.append(['mi by runs', '-----'])
    for l in mi_listVar:
        reports.append([l, sum(eval(l))/nScans])

    print(tabulate(reports))

    if saveText:
        with open(resDir + '/' + subj + '_mi_coreg_' + os.path.basename(sourceImg) + '.txt', 'w') as f:
            for item in reports:
                f.write("%s\n" % item)
        print('saved the table report to ' + resDir)

    return cc_all, mi_all


# %%
def avg_mi_type(subjID, type='r', saveText=True, verbose=True, nScans=187, resDir='/scratch/polynlab/fmri/cdcatmr/all_subjects/mutual_info'):
    """
    used for QAing the preprocessing steps by specifically comparing the average mutual information of functional scans to structural scans
    specifying the type as 'r' or 'w' will compare the corresponding structural scan image to the every single functional scan
    return a text print that shows mutual information at trial and subject level

    Parameters
    ----------
    subjID : str
        string of subject data (ie. 'cdcatmr011')
    type : str ['r', 'w'] (default: 'r')
        registration type that would either register to first scan image or the mean image
    saveText : boolean (default: True)
        if True, will save the table report to a separate text file
    verbose : boolean (default: False)
        if True, will print out which scan file is being worked on
    nScans : int (default: 187)
        integer of how many scans to expect per each run
    resDir : str/abs path (default is set to scratch project dir)
        string of absolute path to save the resulted text report

    Returns
    -------
    cc_all: list
        list of all correlation coefficient values
    mi_all: list
        list of all mutual information values

    """
    subj = str(subjID)
    resDir = resDir
    baseDir = '/scratch/polynlab/fmri/cdcatmr/'
    anatDir = baseDir + subj + '/images/anat/'
    funcDir = baseDir + subj + '/images/func/'
    tag = 'func'
    if type == 'r':
        sourceImg = 'T1_anat.nii'
        tag = 'rfunc'
    elif type == 'w':
        sourceImg = 'wT1_anat.nii'
        tag = 'wrfunc'
    meanImg = mi.get_img_slice(anatDir + sourceImg, verbose=verbose)

    os.chdir(funcDir)
    funcs = os.listdir(funcDir)
    funcs.sort()  # funcs = ['func1', 'func2', ... 'func7', 'func8']
    mi_listVar = []
    cc_listVar = []
    # loop by each functional run
    for i in range(0, len(funcs)):
        curr_func = funcs[i]
        # let's first create list variables for each functional run
        temp = ''
        temp = 'mi_' + curr_func + ' = []'
        exec(temp)
        mi_listVar.append('mi_' + curr_func)
        temp = ''
        temp = 'cc_' + curr_func + ' = []'
        exec(temp)
        cc_listVar.append('cc_' + curr_func)

        # now let's read in each functional run folder
        cfuncDir = funcDir + curr_func
        os.chdir(cfuncDir)
        nii_files = os.listdir(cfuncDir)
        nii_files = [x for x in nii_files if x.startswith(tag) and x.endswith('nii')]
        nii_files.sort()

        # sanity check: count scan files
        assert len(nii_files) == nScans, "total scan files found do not match " + str(nScans) + " for func run " + str(i+1)

        # loop by each scan within run
        for j in range(0, nScans):
            if nii_files[j].endswith('1.nii'):
                continue
            if verbose:
                # print('starting ' + curr_func + ' | scan ' + str(j+1))
                print('comparing ' + curr_func + ' | ' + str(sourceImg) + ' to ' + str(nii_files[j]))
            curr_nii = mi.get_img_slice(nii_files[j], verbose=verbose)
            assert np.shape(meanImg) == np.shape(curr_nii), "image dimension does not match at index " + str(j) + ":\n" + str(np.shape(meanImg)) + "\n" + str(np.shape(curr_nii))
            corr = mi.get_core(meanImg, curr_nii)
            mutual_info = mi.mutual_information(meanImg, curr_nii)

            # append each list
            temp_cc = 'cc_' + curr_func + '.append(corr)'
            exec(temp_cc)
            temp_mi = 'mi_' + curr_func + '.append(mutual_info)'
            exec(temp_mi)

    cc_sums = []
    mi_sums = []
    for r in range(0, len(funcs)):
        cc_sums.append(sum(eval(cc_listVar[r])))
        mi_sums.append(sum(eval(mi_listVar[r])))

    # get all entries in a single list
    cc_all = []
    mi_all = []
    for r in range(0, len(funcs)):
        cc_all = cc_all + eval(cc_listVar[r])
        mi_all = mi_all + eval(mi_listVar[r])


    reports = []
    reports.append(['avg cc', sum(cc_sums)/(nScans*len(funcs))])
    reports.append(['avg mi', sum(mi_sums)/(nScans*len(funcs))])
    reports.append(['cc by runs', '-----'])
    for l in cc_listVar:
        reports.append([l, sum(eval(l))/nScans])
    reports.append(['mi by runs', '-----'])
    for l in mi_listVar:
        reports.append([l, sum(eval(l))/nScans])

    print(tabulate(reports))

    if saveText:
        with open(resDir + '/' + subj + '_mi_struct_to_func_' + os.path.basename(sourceImg) + '.txt', 'w') as f:
            for item in reports:
                f.write("%s\n" % item)
        print('saved the table report to ' + resDir)

    return cc_all, mi_all
