# Scrapping-List-of-scientific-journals
First project of web scrapping on Wikipedia's page ' List of scientific journals', as Wikepedia approuves of scrapping

## Prerequisite
### Libraries used
    requests  
    BeautifulSoup 
They are included in the Anaconda distribution. Else ypu have to install them

### Else
You need a python environnement 
As it is scrapping a web page you need to have a good internet connection

## TODO
### Download
Download the repository through Clone Repository or Download Zip
```
git clone https://github.com/Clair1234/Scrapping-List-of-scientific-journals.git
```
### Installation
After download, go to 'cmd' and navigate to the project folder directory
```
cd project
```
### Run 
If you are on VS Code run (Ctrl+Alt+N)

### Description
Once you run the project, it will try to go through the [Wikepedia page](https://en.wikipedia.org/wiki/List_of_scientific_journals) 
Two .json files will be as outputs:
* all_journals.json : which have the hierarchy of journals (here only one level)
* _all_journals_parsed.json : which have all the information gathered on the Wikipedia page

To evaluate the program, there is the variable STATISTICS.
Each page of the [List of Scientific journals](https://en.wikipedia.org/wiki/List_of_scientific_journals) is assumed to have the way of being built in HTML.
The HTML part used as an anchor of the diferent page is the infoxbox on the right of the page ([See example page](https://en.wikipedia.org/wiki/The_Astronomical_Journal))
