from DataAnalysis import DataAnalysis

files = ["C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\0gr_100.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\0gr_250.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\30gr_250.txt",
         "C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\30gr_test.txt"]


def main():
    data_process = DataAnalysis()
    for file in files:
        print(file + " is processed")
        data_process.file_analysis(file, 10000, "C:\\Users\\gukov\\Desktop\\workParser")


if __name__ == '__main__':
    main()
