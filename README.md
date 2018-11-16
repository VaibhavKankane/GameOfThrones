# GameOfThrones full dataset from fandom wiki.
Entity graph created by scraping GOTWiki- https://gameofthrones.fandom.com/wiki

Nodes-       ['Organization', 'Person', 'Event', 'Episode', 'Animal', 'Location',
             'HistoriesNLore', 'Weapon', 'House', 'PersonType', 'Religion',
             'Season']
       
Relationships- ['SeenOrMentioned', 'Membership', 'Religion', 'Center', 'Location',
       'Clergy', 'Allegiance', 'Leader', 'Founder', 'Predecessor',
       'Death', 'Culture', 'Conflict', 'Place', 'Outcome',
       'AssociatedLocation', 'Father', 'Mother', 'Spouse', 'Siblings',
       'Battles', 'Rulers', 'Narratedby', 'Lovers', 'Successor',
       'Children', 'Maker', 'Owner', 'Lord', 'Capital', 'Cities', 'Towns',
       'Castles', 'Species', 'Range', 'Ruler', 'Population', 'Heir',
       'Ancestralweapon', 'PlacesofNote', 'Formerly', 'Placesofnote',
       'Military', 'Institutions', 'Villages', 'Placeoforigin',
       'Formedfrom', 'Cadetbranches', 'Militarystrength', 'Premiere',
       'Finale']

I have written a introductory blog about web scraping - https://codefringo.wordpress.com/2018/10/22/the-journey-begins/

Important files-
1. spiders/GotTGraphSpider.py is the main spider used to scrape fandom wiki
2. DataProcessor/ScrapyOutputProcessing.ipynb is the jupyter notebook that processes the scrapedOutput and generates tabular data for entities and creates graph in neo4j instance.

Run the whole project-
1. Run command- "scrapy crawl GotGraphSpider -o Data/ScrapedData.json"
2. Execute the jupyter notebook - DataProcessor/ScrapyOutputProcessing.ipynb.