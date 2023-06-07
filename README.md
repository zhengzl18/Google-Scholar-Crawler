# Google-Scholar-Crawler
A crawler for crawling the basic information of papers from google scholar.

This repo is built on the basis of https://github.com/needleworm/google_scholar_crawler, which is now out of date.

## Requirements
```bash
pip install scholarly==1.7.11
```

## Usage
**THIS IS IMPORTANT**

[Google scholar](https://scholar.google.com/) itself is way too hard to crawl, so it is highly recommended that you change the **239th line** in `scholarly/_navigator.py` to 
```python
html = self._get_page('https://scholar.lanfanshu.cn/{0}'.format(url))
```
, which is a mirror site of google scholar.
