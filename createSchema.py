file = open('TICKERS.txt', 'r')
file1 = open('textFile.txt', 'w')
for ticker in file:
    t = ticker[:-1]
    lines = [f'model {t} ', "{ \n", "date DateTime @id\n", "open      Float    @default(0)\n", "high      Float    @default(0)\n", "low       Float    @default(0)\n",
             "close     Float    @default(0)\n", "adj_close Float    @default(0)\n", "volume    Float      @default(0)\n", "dividends     Float    @default(0)\n", "stock Float    @default(0)\n", "splits    Float      @default(0)\n", "}\n"]
    file1.writelines(lines)
