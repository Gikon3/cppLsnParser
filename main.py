from DataAnalysis import DataAnalysis
import os

files = ["C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\0gr_100.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\0gr_250.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\30gr_250.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\30gr_test.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\60gr.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\60gr1.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\60gr2.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\60gr250.txt",
         "C:\\Users\\gukov\\Desktop\\logs_input\\0degree_move.txt",
         "C:\\Users\\gukov\\Desktop\\logs_input\\30degree_move.txt",
         "C:\\Users\\gukov\\Desktop\\logs_input\\30degree_nomove.txt",
         "C:\\Users\\gukov\\Desktop\\logs_input\\60degree_move.txt",
         "C:\\Users\\gukov\\Desktop\\logs_input\\60degree_nomove.txt",
         "C:\\Users\\gukov\\Desktop\\logs_input\\lowpower(0degree).txt"]
work_dir = "C:\\Users\\gukov\\Desktop\\workParser\\"


def main():
    data_process = DataAnalysis()
    brief_filename = work_dir + "brief.txt"
    packets_filename = work_dir + "mem_"
    coords_filename = work_dir + "mem_coords_"
    coords_filename_wolf = work_dir + "mem_coords_wolf_"
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)
    with open(brief_filename, 'w'):
        pass
    for file in files:
        print(file + " is processed")
        data_process.file_analysis(file, 10000)
        data_process.write_brief(brief_filename)
        filename = os.path.split(file)[1]
        data_process.write_packets(packets_filename + filename)
        data_process.write_coords(coords_filename + filename)
        data_process.write_coords_wolfram(coords_filename_wolf + filename)


if __name__ == '__main__':
    main()
