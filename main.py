from DataAnalysis import DataAnalysis
import os

files = ["C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\0gr_100.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\0gr_250.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\30gr_250.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\30gr_test.txt"]
work_dir = "C:\\Users\\gukov\\Desktop\\workParser\\"


def main():
    data_process = DataAnalysis()
    brief_filename = work_dir + "brief.txt"
    packets_filename = work_dir
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)
    with open(brief_filename, 'w'):
        pass
    for file in files:
        print(file + " is processed")
        data_process.file_analysis(file, 10000)
        data_process.write_brief(brief_filename)
        data_process.write_packets(work_dir + "mem_" + os.path.split(file)[1])


if __name__ == '__main__':
    main()
