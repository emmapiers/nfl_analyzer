This project is a data pipeline that automates the scraping, cleaning and structuring of NFL player and team statistics for weekly matchup analysis. The pipeline collects data across multiple positions (QB, RB, WR/TE and TEAM) and compiles them into Excel spreadsheets. These spreadsheets are designed to assist in making data-driven decisions for fantasy football lineups, increasing the likelihood of weekly success. 

Compiling matchup-specific stats manually from multiple websites can be time-consuming and error-prone. This tool streamlines the process so that users can have ready to use data each week.

To ensure easy access for users without a technical background, a simple static website hosted on GitHub Pages has been created. This method was used so that users can easily download the latest weekly spreadsheets without needing to run any code or install additional tools locally.

Website link: https://emmapiers.github.io/nfl_analyzer/



Data Sources:
www.pro-football-reference.com
www.fantasypros.com

**Various webpages from each were used. Specific URLS can be found at nfl_analyzer/scrapers/urls.py
