"""
We have a total of 96 announcements (48 hours of announcements)

Assumptions:
1. 

Suggested tests:

1. If upload when there are no leechers
2. If download with no seeders
3. If consistently downloading fast with not a lot of seeders
4. If upload amount is ridciously high compared to leechers amount
5. If sole uploader yet the leecher download status does not update
6. If sole leecher yet no one uploads


how can we know it not really downloading?



torrentX suggested tests:

1. request hash of a random piece and compare it 
2. for downloaders - requests a peer table and compare it with the stored table in the tracker;
 

"""