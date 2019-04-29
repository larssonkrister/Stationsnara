# Stationssamhällen

Det här är en demonstrator utvecklad i projektet God ljudmiljö i stationssamhällen!

Demonstratorn kan köras i Windows 10 och kräver att Google Chrome finns installerad på datorn.

För att göra en distribution krävs två steg. Först görs en distribution av pytonprogrmmet. Därefter paketeras distributionen som en Windows installerare.

## Ladda ner projektet

Ladda ner projektet med git ```git clone https://github.com/larssonkrister/Stationsnara.git``` eller som .zip fil, det finns en knapp på huvudsidan *Clone or download*. Om du laddat ner som .zip fil packa upp den på lämpligt ställe. 

## Skapa python distribution

För att kunna skapa en python distribution så krävs att python>=3.6, flask>=1.0.2 och pyinstaller finnns installerad på datorn. Förslagsvis kan man installera Python distributionen [miniconda](https://docs.conda.io/en/latest/miniconda.html). Sedan installeras flask genom att köra följande kommand i PowerShell ```conda install flask``` och pyinstaller med ```conda install pyinstaller```

Gå in i projektets mapp Stationsnara.
Öppna ett PowerShell fönster (finns i file menyn längst uppe till vänster i filbrowsern).

Kör komandot: ```pyinstaller main.py```

All kod som behövs för att köra python programmet finns nu i mappen ```dist```. 

## Skapa en Windows installerare

För att kunna skapa en Windows installerare så krävs programmet [Inno Setup](http://www.jrsoftware.org/isdl.php). Installera det på datorn.

Starta Inno Setup Compiler, öppna filen ```rise_sns.iss``` och kör (run), det också tar en stund. När programmet är klart så finns en installerare i mappen ```output```
