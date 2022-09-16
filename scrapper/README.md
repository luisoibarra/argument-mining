# Scrapper

Stores all the scrappers projects. The scrapping is made by [scrapy](https//scrapy.org)

## Granma

It contains two spiders with the objective of crawling the Granma newspaper in the **Edición Impresa** and **Cartas a la Dirección** sections of the newspaper.

### Edición Impresa

The URLs of the printed edition are made up of the template _<https://www.granma.cu/impreso/AÑO-MES-DIA>_. On this page are the PDF versions of the newspaper that went to press.

All information about the pages of the day are extracted from the page and the respective PDFs are downloaded.

#### Printed Edition Data

Stored at **granma/data/printed**

Each folder contains the date of the release on its name and inside the pages are separated its number. The last page is the full newspaper.

### Cartas a la Dirección

The URLs of the letters to the address are displayed through a pagination system _<https://www.granma.cu/archivo?page=PAGE&q=&s=14>_. On this page, the addresses to the letters are collected, which are then processed to extract the necessary information.

#### Letter Data

Stored at **granma/data/letters**

Each folder contains the date of the release on its name and inside, JSON files are created with the letter's title. The keys of the JSON files are:

- title: Title of the letter
- body: Body of the letter
- link: Link to the letter
- original_letter_link: Link to the letter that this letter is responding to.
- is_response: If the letter is a response letter.
- date: Date of the letter
- comments: Comments of the letter

## Usage

### Console

To run the spiders run this scripts changing the params

```bash
usage: main.py [-h] [--spiders_to_run {letter,printed,all}]
               [--initial_page INITIAL_PAGE] [--final_page FINAL_PAGE]
               [--start_date START_DATE] [--end_date END_DATE]

optional arguments:
  -h, --help            show this help message and exit
  --spiders_to_run {letter,printed,all}
                        Choose the spiders to run
  --initial_page INITIAL_PAGE
                        Initial page to look at https://www.granma.cu/archivo?
                        page=[INITIAL_PAGE]&q=&s=14
  --final_page FINAL_PAGE
                        Final page to look at https://www.granma.cu/archivo?pa
                        ge=[FINAL_PAGE]&q=&s=14. To get a good value visit the
                        page and look for the last page number
  --start_date START_DATE
                        Initial date to fetch the printed version. Must have
                        the format: YYYY-MM-DD. Default: 2020-01-01
  --end_date END_DATE   Final date to fetch the printed version. Must have the
                        format: YYYY-MM-DD. Default: Current date
```

**Utility script:**

```bash
./main.sh
```
