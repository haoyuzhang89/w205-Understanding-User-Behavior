# Project 3: Understanding User Behavior

(**Our pipeline demonstration and analysis are combined in the Project3_Report file for both notebook and MD version**)


## Abstract

As a data scientist at a game development company, our latest mobile game has events we're interested in tracking: buy a sword, buy a shield & join guild. Each has metadata characterstic of such events (i.e., rarity, guild name, etc)

Our project is intended to mimic a real world gaming system to include simple gaming ideas such as purchases, inventory, guild joining mechanics. We utilized the below tools to realize features like: 
    1. live time player status check
    2. Inventory tracking
    3. Purchase randomization in terms of weapon rarity
    4. Simple analysis using Hive and Presto utilizing the live data stream build using flask API and Kafka.
    
- Most of our examples shown in this report are ran our teammate's, **Haoyu Zhang's**, system, so you might observer certain system path call that is different from the owner in Github.

- The MD file and the jupyter notebook files serve as our main report for the project to demonstrate the pipeline workflow, simple analysis. In case the format of MD is not ideal due to plateform supporting and various code examples, please refer to ou jupyter file for your reference.

- **Our project focused more on API building and game event logics rather than the analysis part in Presto. The analysis for presto is intended to show idea demonstration the game owner can potentially perform rather than an actual full length data analysis with real world data.**

    
## Tool Used

- Docker Images: 
  - cloudera 
  - kafka                        
  - mids (terminal system image)
  - spark
  - zookeeper
  - presto
  (docker configuration file __docker-compose.yml__ is included)
  

- Google cloud virtual machine 

- Jupyter Notebook

- SQLite Database

- Kafka

- Hive

- Flask API

- Presto



## Project Outcome

- Realization of functional API and data pipeline
  
- Operation of analysis using Presto based on test data

-----    

## Link to the report

[Project Report](Project3_Report.ipynb)\
[Project Report md version](Project3_Report.md)\
[Database Set-Up](create_database.ipynb)\
[API Set-Up](game_api.py)\
[Guild Stream Set-Up](write_guild_stream.py)\
[Swords Stream Set-Up](write_swords_stream.py)\
[Shields Stream Set-Up](write_shields_stream.py)


    



