# PTT Beauty Crawling

A Python Script to crawl and store the article data from PTT Beauty. (2018 support only)


### Prerequisites

1. Install Python3.6 (Anocnda is recommended for Windows User) 

### Installing

Run the following command to install the required package.

```
pip install -r requirements.txt
```

## Running the script

The script provides 4 features:

1. Crawl all articles published in 2018.

```
python 0516225.py crawl
```

2. Count and summarize each user's 推文數、噓文數, and find top 10 users with most 推文數 噓文數

```
python 0516225.py push start_date end_date
```

3. Find 爆文 and the image posted in that article.

```
python 0516225.py popular
```

4. Find all articles that match your input keyword. For example "結衣我婆"

```
python 0516225.py {keyword} start_date end_date
```
