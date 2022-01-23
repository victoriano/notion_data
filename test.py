from NotionData import NotionToCSV, get_all_db_entries
from pprint import pprint

db = get_all_db_entries("d4a079211959486495bdef8b61b3e8bc")
pprint(db)

#df = NotionToCSV("4870a2649b6c4d3784fc8a24196ea690")
#Taxonomy Table: 2fbdd8aba1604e2385ed7be3a59d1984
#Concepts Table: 763f8356f41c45e3934950696f00fa21
#Movies 4870a2649b6c4d3784fc8a24196ea690
#Podcasts c1f6b77ce50a47b7b1e524c923079c17
#Podcasts Channels d4a079211959486495bdef8b61b3e8bc


#print(df)