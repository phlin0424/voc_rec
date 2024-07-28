WITH 
korean_cards as (
    SELECT * 
    FROM cards 
    WHERE cards.did = '{deck_id}'
), 
korean_nid as (
    SELECT nid from korean_cards
) 
SELECT flds
FROM Notes
INNER JOIN korean_nid ON Notes.id = korean_nid.nid