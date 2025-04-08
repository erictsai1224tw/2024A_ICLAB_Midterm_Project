import os
import subprocess
import pandas as pd
import shutil 
import re
import sys

File_System_Path = "/RAID2/COURSE/iclab/iclabTA01/2024A_fileSYSTEM"
Lab_name = "Midterm_Project"
Design = "ISP"
Demo_File = "demofile.txt"
Default_Cycle_Time = 15
Default_Latency = 0
blue_color = "\033[94m"  # 蓝色
green_color = "\033[92m"  # 绿色
red_color = "\033[91m"  # 红色
yellow_color = "\033[93m"  # 黄色
reset_color = "\033[0m"  # 重置颜色为默认

# class args_class():
#     def __init__(self):
#         self.username = "iclab001"
#         self.demo_type = "1st_demo"
#         self.msg = True
# args = args_class()

# 解析命令行参数
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("username", type=str, default="gg", help="Username")
parser.add_argument("demo_type", type=str, choices=["1st_demo", "2nd_demo"], default="1st_demo", help="Demo type")
parser.add_argument("--no-show-msg", dest='msg', help="Do not show message", action='store_false')
parser.set_defaults(msg=True)
args = parser.parse_args()

DEMO_RESULT = pd.DataFrame(columns=["Account", "Pass", "Message", "Files", "01_RTL", "02_SYN", "03_GATE", "CT", "Latency", "Area"])

##############################################################################################################
# Function
##############################################################################################################

def demo_fail():
    DEMO_RESULT.loc[0, "Pass"] = "X"
    DEMO_RESULT.to_csv("DEMO_RESULT.csv", index=False)
    if (args.msg):
        print(f"{red_color}[FAIL] {args.username} demo fail{reset_color}")
        print(f"{red_color}{DEMO_RESULT}{reset_color}")
    sys.exit(0)

def extract_total_cell_area(design):
    try:
        with open(f"02_SYN/Report/{design}.area", "r") as file:
            lines = file.readlines()
        total_cell_area = None
        for line in lines:
            if "Total cell area:" in line:
                parts = line.split()
                if len(parts) >= 3:
                    total_cell_area = parts[3]
                    break
        if total_cell_area is not None:
            total_cell_area = float(total_cell_area)
            return total_cell_area
        else:
            return None 
    except Exception as e:
        print(f"Error: {e}")
        return None


def extract_memory_area(design):
    try:
        with open(f"02_SYN/Report/{design}.area", "r") as file:
            content = file.read()
        match = re.search(r"Macro/Black Box area:\s+(\d+\.\d+)", content)
        if match:
            memory_area_str = match.group(1)
            memory_area_str = re.sub(r'[^0-9.]', '', memory_area_str)
            memory_area = float(memory_area_str)
            return memory_area
        else:
            return None 
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_cycle_time(filename):
    parts = filename.split("_")
    if len(parts) >= 2:
        cycle_time = parts[0] 
        return cycle_time
    return Default_Cycle_Time

def extract_latency_from_log(log_file):
    try:
        with open(log_file, "r") as file:
            content = file.read()
        match = re.search(r'Your execution cycles = \s*(\d+)', content)
        if match:
            latency_cycles = float(match.group(1))
            return latency_cycles
        else:
            return Default_Latency  
    except Exception as e:
        print(f"Error: {e}")
        return None

# <<<<<<<<<<<<<<<<<<<<<
# Main Flow
# <<<<<<<<<<<<<<<<<<<<<
##############################################################################################################
# Step1: Account
##############################################################################################################
DEMO_RESULT.loc[0, "Account"] = args.username
##############################################################################################################
# Step2: File Check
##############################################################################################################
Demo_File_Folder_Path = f"{File_System_Path}/{Lab_name}/{args.demo_type}"

Lab_tar_file = f"{Demo_File_Folder_Path}/{Lab_name}_{args.username}.tar.gz"
Lab_folder = f"{Demo_File_Folder_Path}/{Lab_name}_{args.username}"


demo_files = []
stu_files = []
only_file_name = []

with open (Demo_File, "r") as f:
    lines = f.readlines()
    for line in lines:
        # print(line.strip())
        filename = line.strip()
        demo_files.append(filename)

        filename = filename.split('/')[-1]
        name, ext = filename.split('.')
        new_filename = f"{name}_{args.username}.{ext}"
        stu_files.append(new_filename)
        only_file_name.append(name)
# print(demo_files, stu_files, only_file_name)

demo_files.append("./02_SYN/.synopsys_dc.setup")
stu_files.append(f".synopsys_dc_{args.username}.setup")
only_file_name.append(f".synopsys_dc.setup")

if not os.path.exists(Lab_tar_file):
    DEMO_RESULT.loc[0, "Files"] = "X"
    DEMO_RESULT.loc[0, "Message"] = "No tar File"
    demo_fail()
else:
    if(os.path.exists(Lab_folder)):
        shutil.rmtree(Lab_folder)
    subprocess.run(["sudo", "chown","iclabTA01:iclab", Lab_tar_file], cwd=Demo_File_Folder_Path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    subprocess.run(["tar", "-zxvf", Lab_tar_file], cwd=Demo_File_Folder_Path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["chmod","-R","700", Lab_folder], cwd=Demo_File_Folder_Path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["sudo", "chown",f"{args.username}:iclab", Lab_tar_file], cwd=Demo_File_Folder_Path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not (os.path.exists(Lab_folder)):
        DEMO_RESULT.loc[0, "Files"] = "X"
        DEMO_RESULT.loc[0, "Message"] = "No Files in folder"
        demo_fail()
    else:
        for stu_file in stu_files:
            if not (os.path.exists(f"{Lab_folder}/{stu_file}")):
                DEMO_RESULT.loc[0, "Files"] = "X"
                DEMO_RESULT.loc[0, "Message"] = "No Files in folder"
                demo_fail()
        DEMO_RESULT.loc[0, "Files"] = "O"

##############################################################################################################
# Step3: File Copy
##############################################################################################################
if DEMO_RESULT.loc[0, "Files"] == "O":
    # shutil.copy(File1, "./00_TESTBED/filelist.f")
    # shutil.copy(File2, "./01_RTL/BEV.sv")
    # shutil.copy(File2, "../STUDENT_FILES")
    
    # Copy student's submit files to demo env
    for idx, demo_file in enumerate (demo_files):
        shutil.copy(f"{Lab_folder}/{stu_files[idx]}", demo_file)
    
    # Create All student file folder
    if not os.path.exists(f"{File_System_Path}/{Lab_name}/2024_MP_STUDENT_FILES_ALL"):
        os.makedirs(f"{File_System_Path}/{Lab_name}/2024_MP_STUDENT_FILES_ALL")
    for idx, n in enumerate(only_file_name):
        f_name = f"{File_System_Path}/{Lab_name}/2024_MP_STUDENT_FILES_ALL/{n}"
        if not os.path.exists(f_name):
            os.makedirs(f_name)
        shutil.copy(f"{Lab_folder}/{stu_files[idx]}", f"{f_name}/{stu_files[idx]}")
    
    # 更新syn.tcl文件中的CYCLE值
    syn_tcl_file_design = "./02_SYN/syn.tcl"
    cycle_time_file = [filename for filename in os.listdir(Lab_folder) if filename.endswith(".txt")]
    # cycle_time = extract_cycle_time(cycle_time_file[0])
    cycle_time = float(cycle_time_file[0].split("_")[0])
    DEMO_RESULT.loc[0, "CT"] = cycle_time
    
    # DESIGN's DC tcl
    with open(syn_tcl_file_design, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if "set CYCLE" in line:
            lines[i] = "set CYCLE {}\n".format(DEMO_RESULT.loc[0, "CT"])
            break
    with open(syn_tcl_file_design, 'w') as f:
        f.writelines(lines)
        
    DEMO_RESULT.loc[0, "CT"] = DEMO_RESULT.loc[0, "CT"]
    
    # Copy Memory files to 04_MEM
    mem_folder = f"{Lab_folder}/04_MEM_{args.username}"
    for mem_file in os.listdir(mem_folder):
        shutil.copy(f"{mem_folder}/{mem_file}", f"04_MEM/{mem_file}")
    
    if (args.msg):
        print(f"{blue_color}[Info] {args.username} File Copy OK{reset_color}")


##############################################################################################################
# Step4: 01_RTL
##############################################################################################################

if DEMO_RESULT.loc[0, "Files"] == "O":
    
    # dram1.dat
    dat_name = "dram1.dat"
    
    os.chdir("01_RTL")
    if (args.msg):
        print(f"{blue_color}[Info] {args.username} 01_RTL {dat_name} start{reset_color}")
    subprocess.run(["make", "clean"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["make","vcs_rtl_1"], stdout=open("../01_RTL.log", "w"), stderr=subprocess.STDOUT)
    # print(f"{blue_color}[Info] {args.username} 01_RTL end{reset_color}")
    os.chdir("..")
    
    try:
    # 检查01_RTL.log
        with open("01_RTL.log", 'r') as f:
            rtl_log = f.read()
            if ("FAIL" in rtl_log) or ("Error" in rtl_log):
                DEMO_RESULT.loc[0, "01_RTL"] = "X"
                DEMO_RESULT.loc[0, "Message"] = f"01_RTL Pattern Fail {dat_name}"
                demo_fail()
            elif "Congratulations" in rtl_log:
                # DEMO_RESULT.loc[0, "01_RTL"] = "O"
                # latency = extract_latency_from_log("01_RTL.log")
                if (args.msg):
                    print(f"{green_color}[PASS] {args.username} 01_RTL {dat_name} {reset_color}")
    except:
        demo_fail()
    
    # dram2.dat
    dat_name = "dram2.dat"
    os.chdir("01_RTL")
    if (args.msg):
        print(f"{blue_color}[Info] {args.username} 01_RTL {dat_name} start{reset_color}")
    subprocess.run(["make", "clean"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["make","vcs_rtl_2"], stdout=open("../01_RTL.log", "w"), stderr=subprocess.STDOUT)
    # print(f"{blue_color}[Info] {args.username} 01_RTL end{reset_color}")
    os.chdir("..")
    
    try:
    # 检查01_RTL.log
        with open("01_RTL.log", 'r') as f:
            rtl_log = f.read()
            if ("FAIL" in rtl_log) or ("Error" in rtl_log):
                DEMO_RESULT.loc[0, "01_RTL"] = "X"
                DEMO_RESULT.loc[0, "Message"] = f"01_RTL Pattern Fail {dat_name}"
                demo_fail()
            elif "Congratulations" in rtl_log:
                # DEMO_RESULT.loc[0, "01_RTL"] = "O"
                # latency = extract_latency_from_log("01_RTL.log")
                if (args.msg):
                    print(f"{green_color}[PASS] {args.username} 01_RTL {dat_name} {reset_color}")
    except:
        demo_fail()
    
    # dram0.dat
    dat_name = "dram0.dat"
    os.chdir("01_RTL")
    if (args.msg):
        print(f"{blue_color}[Info] {args.username} 01_RTL {dat_name} start  {reset_color}")
    subprocess.run(["make", "clean"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["make","vcs_rtl_3"], stdout=open("../01_RTL.log", "w"), stderr=subprocess.STDOUT)
    # print(f"{blue_color}[Info] {args.username} 01_RTL end{reset_color}")
    os.chdir("..")
    
    try:
    # 检查01_RTL.log
        with open("01_RTL.log", 'r') as f:
            rtl_log = f.read()
            if ("FAIL" in rtl_log) or ("Error" in rtl_log):
                DEMO_RESULT.loc[0, "01_RTL"] = "X"
                DEMO_RESULT.loc[0, "Message"] = "01_RTL {dat_name} Pattern Fail"
                demo_fail()
            elif "Congratulations" in rtl_log:
                DEMO_RESULT.loc[0, "01_RTL"] = "O"
                latency = extract_latency_from_log("01_RTL.log")
                if (args.msg):
                    print(f"{green_color}[PASS] {args.username} 01_RTL{reset_color}")
    except:
        demo_fail()

# ##############################################################################################################
# # Step5: 02_SYN
# ##############################################################################################################
if DEMO_RESULT.loc[0, "01_RTL"] == "O":
    os.chdir("02_SYN")
    if (args.msg):
        print(f"{blue_color}[Info] {args.username} 02_SYN start{reset_color}")
    subprocess.run(["make", "clean"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["make", "syn"], stdout=open("../02_SYN.log", "w"), stderr=subprocess.STDOUT)

    # print(f"{blue_color}[Info] {args.username} 02_SYN end{reset_color}")
    os.chdir("..")

    # 检查02_SYN.log
    with open("02_SYN.log", 'r') as f:
        syn_log = f.read()
        if "Latch" in syn_log:
            DEMO_RESULT.loc[0, "02_SYN"] = "X"
            DEMO_RESULT.loc[0, "Message"] = f"02_SYN {Design} Latch"
            demo_fail()
        elif "mismatch" in syn_log:
            DEMO_RESULT.loc[0, "02_SYN"] = "X"
            DEMO_RESULT.loc[0, "Message"] = f"02_SYN {Design} Mismatch"
            demo_fail()
        elif "Error" in syn_log:
            DEMO_RESULT.loc[0, "02_SYN"] = "X"
            DEMO_RESULT.loc[0, "Message"] = f"02_SYN {Design} Error"
            demo_fail()
        elif os.path.exists(f"Report/{Design}.timing") and "violated" in open(f"Report/{Design}.timing").read():
            DEMO_RESULT.loc[0, "02_SYN"] = "X"
            DEMO_RESULT.loc[0, "Message"] = f"02_SYN {Design} Timing (violated)"
            demo_fail()

        # elif memory_area == "0":
        #     DEMO_RESULT.loc[0, "02_SYN"] = "X"
        #     DEMO_RESULT.loc[0, "Message"] = "02_SYN No use of memory"
        #     demo_fail()
        else:
            Area = extract_total_cell_area(f"{Design}")
            memory_area = extract_memory_area(f"{Design}")
            gate_count = (Area+memory_area) / 9.9792
            DEMO_RESULT.loc[0, "02_SYN"] = "O"
            if (args.msg):
                print(f"{green_color}[PASS] {args.username} 02_SYN {reset_color}")

##############################################################################################################
# Step6: 03_GATE
##############################################################################################################
if DEMO_RESULT.loc[0, "02_SYN"] == "O":
    os.chdir("03_GATE")
    if (args.msg):
        print(f"{blue_color}[Info] {args.username} 03_GATE start{reset_color}")
    subprocess.run(["make", "clean"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["make","vcs_gate", f"GATE_CYCLE_TIME={cycle_time}"], stdout=open("../03_GATE.log", "w"), stderr=subprocess.STDOUT)
    # print(f"{blue_color}[Info] {args.username} 03_GATE end{reset_color}")
    os.chdir("..")

    # 检查03_GATE.log
    with open("03_GATE.log", 'r') as f:
        gate_log = f.read()
    if ("FAIL" in gate_log) or ("Error" in gate_log):
        DEMO_RESULT.loc[0, "03_GATE"] = "X"
        DEMO_RESULT.loc[0, "Message"] = "03_GATE Pattern Fail"
        demo_fail()
    elif "Congratulations" in gate_log:
        DEMO_RESULT.loc[0, "03_GATE"] = "O"
        latency = extract_latency_from_log("03_GATE.log")
        if (args.msg):
            print(f"{green_color}[PASS] {args.username} 03_GATE{reset_color}")
    else:
        DEMO_RESULT.loc[0, "03_GATE"] = "X"
        DEMO_RESULT.loc[0, "Message"] = "03_GATE Run Error"
        demo_fail()
##############################################################################################################
# Step7: DEMO_RESULT.csv
##############################################################################################################
if DEMO_RESULT.loc[0, "03_GATE"] == "O":
    DEMO_RESULT.loc[0, "Pass"] = args.demo_type
    DEMO_RESULT.loc[0, "Area"] = Area
    DEMO_RESULT.loc[0, "Latency"] = latency
    
    
DEMO_RESULT.to_csv("DEMO_RESULT.csv", index=False)
if (args.msg):
    print(f"{green_color}{DEMO_RESULT}{reset_color}")
sys.exit(0)
