from DataAnalysis import DataAnalysis

files = ["C:\\Users\\gukov\\Desktop\\НИИ МА НАУКА\\0gr_100.txt"]


def main():
    for file in files:
        with open(file, 'r') as f:
            text = f.readlines()
        data_process = DataAnalysis()
        data_process.analysis(text)


if __name__ == '__main__':
    main()
