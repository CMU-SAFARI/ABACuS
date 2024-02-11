import os

os.system('make')

print("##############################################")
print("################## ABACuS ####################")
print("##############################################")


address_cam_configs = ['our_study/address-cam-rh1000-bank32.cfg', 'our_study/address-cam-rh125-bank32.cfg']
count_cam_configs = ['our_study/count-cam-rh1000-bank32.cfg', 'our_study/count-cam-rh125-bank32.cfg']
sav_configs = ['our_study/sibling-addr-vector-rh1000-bank32.cfg', 'our_study/sibling-addr-vector-rh125-bank32.cfg']

# Run cacti for each configuration
# e.g., for our_study/address-cam-rh1000-bank32.cfg, use `os.system(./cacti -infile address-cam-rh1000-bank32.cfg > cacti_results/address-cam-rh1000-bank32.txt)`
os.system('mkdir -p cacti_results')

for config in address_cam_configs:
    os.system('./cacti -infile ' + config + ' > cacti_results/' + config.split('/')[1].split('.')[0] + '.txt')
    
for config in count_cam_configs:
    os.system('./cacti -infile ' + config + ' > cacti_results/' + config.split('/')[1].split('.')[0] + '.txt')
    
for config in sav_configs:
    os.system('./cacti -infile ' + config + ' > cacti_results/' + config.split('/')[1].split('.')[0] + '.txt')

# clear .out files under our_study/
os.system('rm our_study/*.out')

# result file names arrays like the ones at the top of the file
address_cam_results = ['cacti_results/address-cam-rh1000-bank32.txt', 'cacti_results/address-cam-rh125-bank32.txt']
count_cam_results = ['cacti_results/count-cam-rh1000-bank32.txt', 'cacti_results/count-cam-rh125-bank32.txt']
sav_results = ['cacti_results/sibling-addr-vector-rh1000-bank32.txt', 'cacti_results/sibling-addr-vector-rh125-bank32.txt']

for ac,cc,sav in zip(address_cam_results, count_cam_results, sav_results):
    # open file and read all lines
    acf = open(ac, 'r')
    ac_lines = acf.readlines()
    acf.close()
    ccf = open(cc, 'r')
    cc_lines = ccf.readlines()
    ccf.close()
    savf = open(sav, 'r')
    sav_lines = savf.readlines()
    savf.close()
    
    nrh = ac.split('-')[2].removeprefix('rh')

    ######################### AREA #########################

    # find the line that starts with "CAM array: Area (mm2):"
    for line in ac_lines:
        if line.strip().startswith('CAM array: Area (mm2):'):
            # split the line by space, get the last element, which is the area
            acf_area = line.split(' ')[-1][:-1]
            break
        
    # find the line that starts with "CAM array: Area (mm2):"
    for line in cc_lines:
        if line.strip().startswith('CAM array: Area (mm2):'):
            # split the line by space, get the last element, which is the area
            ccf_area = line.split(' ')[-1][:-1]
            break
    
    # find the line that starts with "Data array: Area (mm2):"
    for line in sav_lines:
        if line.strip().startswith('Data array: Area (mm2):'):
            # split the line by space, get the last element, which is the area
            sav_area = line.split(' ')[-1][:-1]
            break
        
    ######################### ENERGY #########################
        
    for line in ac_lines:
        if line.strip().startswith('Total dynamic associative search energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            acf_acc_en = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total dynamic write energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            acf_wr_en = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total dynamic read energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            acf_rd_en = line.split(' ')[-1][:-1]
            
    acf_en = str(float(acf_acc_en) + float(acf_wr_en) + float(acf_rd_en))
        
    for line in cc_lines:
        if line.strip().startswith('Total dynamic associative search energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            ccf_acc_en = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total dynamic write energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            ccf_wr_en = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total dynamic read energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            ccf_rd_en = line.split(' ')[-1][:-1]
    
    ccf_en = str(float(ccf_acc_en) + float(ccf_wr_en) + float(ccf_rd_en))        
    
    for line in sav_lines:
        if line.strip().startswith('Total dynamic write energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            sav_wr_en = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total dynamic read energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            sav_rd_en = line.split(' ')[-1][:-1]

    sav_en = str(float(sav_wr_en) + float(sav_rd_en))        
    
    ######################### POWER #########################
    
    for line in ac_lines:
        if line.strip().startswith('Total leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            acf_cell_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total gate leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            acf_gate_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Number of banks:'):
            # split the line by space, get the last element, which is the area
            ac_n_banks = line.split(' ')[-1][:-1]

    acf_power = str((float(acf_cell_leakage) + float(acf_gate_leakage))*float(ac_n_banks))
        
    for line in cc_lines:
        if line.strip().startswith('Total leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            ccf_cell_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total gate leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            ccf_gate_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Number of banks:'):
            # split the line by space, get the last element, which is the area
            cc_n_banks = line.split(' ')[-1][:-1]
    
    ccf_power = str((float(ccf_cell_leakage) + float(ccf_gate_leakage))*float(cc_n_banks))
    
    for line in sav_lines:
        if line.strip().startswith('Total leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            sav_cell_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total gate leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            sav_gate_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Number of banks:'):
            # split the line by space, get the last element, which is the area
            sav_n_banks = line.split(' ')[-1][:-1]

    sav_power = str((float(sav_cell_leakage) + float(sav_gate_leakage))*float(sav_n_banks))
        
    # print file names (ac, cc, sav)
    # print(ac + ' ' + cc + ' ' + sav)
    
    # display 2 decimal places
    print('nRH:' + nrh + ' Row ID Table Area: ' + str(round(float(acf_area), 2)) + ' RAC Table Area: ' + str(round(float(ccf_area), 2)) + ' SAV Area: ' + str(round(float(sav_area), 2)) + ' Total Area: ' + str(round(float(acf_area) + float(ccf_area) + float(sav_area), 2)) + ' mm2')
    print('nRH:' + nrh + ' Row ID Table Energy: ' + str(round(float(acf_en)*1000, 2)) + ' RAC Table Energy: ' + str(round(float(ccf_en)*1000, 2)) + ' SAV Energy: ' + str(round(float(sav_en)*1000, 2)) + ' Total Energy: ' + str(round((float(acf_en) + float(ccf_en) + float(sav_en))*1000, 2)) + ' pJ')
    print('nRH:' + nrh + ' Row ID Table Power: ' + str(round(float(acf_power), 2)) + ' RAC Table Power: ' + str(round(float(ccf_power), 2)) + ' SAV Power: ' + str(round(float(sav_power), 2)) + ' Total Power: ' + str(round(float(acf_power) + float(ccf_power) + float(sav_power), 2)) + ' mW')


print("##############################################")
print("################ Graphene ####################")
print("##############################################")

address_cam_configs = ['prior_works/graphene/address-cam-rh1000.cfg', 'prior_works/graphene/address-cam-rh125.cfg']
count_cam_configs = ['prior_works/graphene/count-cam-rh1000.cfg', 'prior_works/graphene/count-cam-rh125.cfg']

# Run cacti for each configuration
# e.g., for our_study/address-cam-rh1000-bank32.cfg, use `os.system(./cacti -infile address-cam-rh1000-bank32.cfg > cacti_results/address-cam-rh1000-bank32.txt)`
os.system('mkdir -p cacti_results')

for config in address_cam_configs:
    os.system('./cacti -infile ' + config + ' > cacti_results/' + config.split('/')[2].split('.')[0] + '.txt')
    
for config in count_cam_configs:
    os.system('./cacti -infile ' + config + ' > cacti_results/' + config.split('/')[2].split('.')[0] + '.txt')
    
# clear .out files under our_study/
os.system('rm prior_works/graphene/*.out')

# result file names arrays like the ones at the top of the file
address_cam_results = ['cacti_results/address-cam-rh1000.txt', 'cacti_results/address-cam-rh125.txt']
count_cam_results = ['cacti_results/count-cam-rh1000.txt', 'cacti_results/count-cam-rh125.txt']

for ac,cc in zip(address_cam_results, count_cam_results):
    # open file and read all lines
    acf = open(ac, 'r')
    ac_lines = acf.readlines()
    acf.close()
    ccf = open(cc, 'r')
    cc_lines = ccf.readlines()
    ccf.close()
    
    nrh = ac.split('-')[2].removeprefix('rh').split('.')[0]

    ######################### AREA #########################

    # find the line that starts with "CAM array: Area (mm2):"
    for line in ac_lines:
        if line.strip().startswith('CAM array: Area (mm2):'):
            # split the line by space, get the last element, which is the area
            acf_area = line.split(' ')[-1][:-1]
            break
        
    # find the line that starts with "CAM array: Area (mm2):"
    for line in cc_lines:
        if line.strip().startswith('CAM array: Area (mm2):'):
            # split the line by space, get the last element, which is the area
            ccf_area = line.split(' ')[-1][:-1]
            break
    
    ######################### ENERGY #########################
        
    for line in ac_lines:
        if line.strip().startswith('Total dynamic associative search energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            acf_acc_en = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total dynamic write energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            acf_wr_en = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total dynamic read energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            acf_rd_en = line.split(' ')[-1][:-1]
    
    acf_en = str(float(acf_acc_en) + float(acf_wr_en) + float(acf_rd_en))
    
    for line in cc_lines:
        if line.strip().startswith('Total dynamic associative search energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            ccf_acc_en = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total dynamic write energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            ccf_wr_en = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total dynamic read energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            ccf_rd_en = line.split(' ')[-1][:-1]
            
    ccf_en = str(float(ccf_acc_en) + float(ccf_wr_en) + float(ccf_rd_en))
    
    ######################### POWER #########################
    
    for line in ac_lines:
        if line.strip().startswith('Total leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            acf_cell_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total gate leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            acf_gate_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Number of banks:'):
            # split the line by space, get the last element, which is the area
            ac_n_banks = line.split(' ')[-1][:-1]

    acf_power = str((float(acf_cell_leakage) + float(acf_gate_leakage))*float(ac_n_banks))
        
    for line in cc_lines:
        if line.strip().startswith('Total leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            ccf_cell_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total gate leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            ccf_gate_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Number of banks:'):
            # split the line by space, get the last element, which is the area
            cc_n_banks = line.split(' ')[-1][:-1]
    
    ccf_power = str((float(ccf_cell_leakage) + float(ccf_gate_leakage))*float(cc_n_banks))
    
    # print file names (ac, cc, sav)
    # print(ac + ' ' + cc)
    
    # display 2 decimal places
    print('nRH:' + nrh + '(per bank) Address CAM Area: ' + str(round(float(acf_area), 2)) + '(per bank) Count CAM Area: ' + str(round(float(ccf_area), 2)) + ' Total Area: ' + str(round((float(acf_area) + float(ccf_area))*32, 2)) + ' mm2')
    print('nRH:' + nrh + '(per bank) Address CAM Energy: ' + str(round(float(acf_en)*1000, 2)) + '(per bank) Count CAM Energy: ' + str(round(float(ccf_en)*1000, 2)) + ' Total Energy: ' + str(round((float(acf_en) + float(ccf_en))*32*1000, 2)) + ' pJ')
    print('nRH:' + nrh + '(per bank) Address CAM Power: ' + str(round(float(acf_power), 2)) + '(per bank) Count CAM Power: ' + str(round(float(ccf_power), 2)) + ' Total Power: ' + str(round((float(acf_power) + float(ccf_power))*32, 2)) + ' mW')


print("##############################################")
print("################## Hydra #####################")
print("##############################################")


gct_configs = ['prior_works/hydra/gct-rh1000.cfg', 'prior_works/hydra/gct-rh125.cfg']
rcc_configs = ['prior_works/hydra/rcc-rh1000.cfg', 'prior_works/hydra/rcc-rh125.cfg']
rit_configs = ['prior_works/hydra/rit-rh1000.cfg', 'prior_works/hydra/rit-rh125.cfg']

# Run cacti for each configuration
# e.g., for our_study/address-cam-rh1000-bank32.cfg, use `os.system(./cacti -infile address-cam-rh1000-bank32.cfg > cacti_results/address-cam-rh1000-bank32.txt)`
os.system('mkdir -p cacti_results')

for config in gct_configs:
    os.system('./cacti -infile ' + config + ' > cacti_results/' + config.split('/')[2].split('.')[0] + '.txt')
    
for config in rcc_configs:
    os.system('./cacti -infile ' + config + ' > cacti_results/' + config.split('/')[2].split('.')[0] + '.txt')
    
for config in rit_configs:
    os.system('./cacti -infile ' + config + ' > cacti_results/' + config.split('/')[2].split('.')[0] + '.txt')

# clear .out files under our_study/
os.system('rm prior_works/hydra/*.out')

# result file names arrays like the ones at the top of the file
gct_results = ['cacti_results/gct-rh1000.txt', 'cacti_results/gct-rh125.txt']
rcc_results = ['cacti_results/rcc-rh1000.txt', 'cacti_results/rcc-rh125.txt']
rit_results = ['cacti_results/rit-rh1000.txt', 'cacti_results/rit-rh125.txt']

for ac,cc,rit in zip(gct_results, rcc_results,rit_results):
    # open file and read all lines
    acf = open(ac, 'r')
    ac_lines = acf.readlines()
    acf.close()
    ccf = open(cc, 'r')
    cc_lines = ccf.readlines()
    ccf.close()
    ritf = open(rit, 'r')
    rit_lines = ritf.readlines()
    ritf.close()
    
    nrh = ac.split('-')[1].removeprefix('rh').split('.')[0]

    ######################### AREA #########################

    # find the line that starts with "CAM array: Area (mm2):"
    for line in ac_lines:
        if line.strip().startswith('Data array: Area (mm2):'):
            # split the line by space, get the last element, which is the area
            acf_area = line.split(' ')[-1][:-1]
            break
        
    # find the line that starts with "CAM array: Area (mm2):"
    for line in cc_lines:
        if line.strip().startswith('Data array: Area (mm2):'):
            # split the line by space, get the last element, which is the area
            ccf_area_data = line.split(' ')[-1][:-1]
        if line.strip().startswith('Tag array: Area (mm2):'):
            # split the line by space, get the last element, which is the area
            ccf_area_tag = line.split(' ')[-1][:-1]
       
    ccf_area = str(float(ccf_area_data) + float(ccf_area_tag))
        
    for line in rit_lines:
        if line.strip().startswith('Data array: Area (mm2):'):
            # split the line by space, get the last element, which is the area
            rit_area = line.split(' ')[-1][:-1]
            break
        
    
    ######################### ENERGY #########################
        
    for line in ac_lines:
        if line.strip().startswith('Total dynamic write energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            acf_wr_en = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total dynamic read energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            acf_rd_en = line.split(' ')[-1][:-1]

    acf_en = str(float(acf_wr_en) + float(acf_rd_en))       
        
    
    for line in cc_lines:
        if line.strip().startswith('Total dynamic write energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            ccf_wr_en = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total dynamic read energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            ccf_rd_en = line.split(' ')[-1][:-1]

    ccf_en = str(float(ccf_wr_en) + float(ccf_rd_en))         
    
    for line in rit_lines:
        if line.strip().startswith('Total dynamic write energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            rit_wr_en = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total dynamic read energy per access (nJ):'):
            # split the line by space, get the last element, which is the area
            rit_rd_en = line.split(' ')[-1][:-1]

    rit_en = str(float(rit_wr_en) + float(rit_rd_en))   
    
    ######################### POWER #########################
    
    for line in ac_lines:
        if line.strip().startswith('Total leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            acf_cell_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total gate leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            acf_gate_leakage = line.split(' ')[-1][:-1]
        
    acf_power = str(float(acf_cell_leakage) + float(acf_gate_leakage))
        
    for line in cc_lines:
        if line.strip().startswith('Total leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            ccf_cell_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total gate leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            ccf_gate_leakage = line.split(' ')[-1][:-1]
            break
    
    ccf_power = str(float(ccf_cell_leakage) + float(ccf_gate_leakage))
    
    for line in rit_lines:
        if line.strip().startswith('Total leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            rit_cell_leakage = line.split(' ')[-1][:-1]
        if line.strip().startswith('Total gate leakage power of a bank (mW):'):
            # split the line by space, get the last element, which is the area
            rit_gate_leakage = line.split(' ')[-1][:-1]
    
    rit_power = str(float(rit_cell_leakage) + float(rit_gate_leakage))
    
    # print file names (ac, cc, sav)
    # print(ac + ' ' + cc)
    
    # display 2 decimal places
    print('nRH:' + nrh + ' GCT Area: ' + str(round(float(acf_area), 2)) + ' RCC Area: ' + str(round(float(ccf_area), 2)) + ' RIT Area: ' + str(round(float(rit_area), 2)) + ' Total Area: ' + str(round((float(acf_area) + float(ccf_area)), 2)) + ' mm2')
    print('nRH:' + nrh + ' GCT Energy: ' + str(round(float(acf_en)*1000, 2)) + ' RCC Energy: ' + str(round(float(ccf_en)*1000, 2)) + ' RIT Energy: ' + str(round(float(rit_en)*1000, 2)) + ' Total Energy: ' + str(round((float(acf_en) + float(ccf_en))*1000, 2)) + ' pJ')
    print('nRH:' + nrh + ' GCT Power: ' + str(round(float(acf_power), 2)*8) + ' RCC Power: ' + str(round(float(ccf_power), 2)) + ' RIT Power: ' + str(round(float(rit_power), 2)) + ' Total Power: ' + str(round((float(acf_power)*8 + float(ccf_power)+ float(rit_power)), 2)) + ' mW')