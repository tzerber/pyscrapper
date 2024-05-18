## System Summary

### Accept site cookies

**Endpoint**: `/system/accept_cookies`  
**Method**: GET  
**Request Body**: NONE
```bash
curl -X GET -H "Content-Type: application/json" http://127.0.0.1:5000/system/accept_cookies
```

### Clear up stalle browser processes 
**Endpoint**: `/system/reload`  
**Method**: GET  
**Request Body**: NONE
```bash
curl -X GET -H "Content-Type: application/json" http://127.0.0.1:5000/system/reload
```

## API Summary

### Update Player Names for Player statistics

**Endpoint**: `/players/update_playernames`  
**Method**: POST  
**Request Body**: JSON  
```bash
curl -X POST -H "Content-Type: application/json" -d '{"playernames": ["20113/deko", "20709/r3salt", "19236/kensi", "19882/norwi"]}' http://127.0.0.1:5000/players/update_playernames
```

### Scrape Player Statistics

**Endpoint**: `/players/scrape`  
**Method**: POST  
```bash
curl -X POST -H "Content-Type: application/json" http://127.0.0.1:5000/players/scrape
```

### Get Player Statistics

**Endpoint**: `/players/statistics`  
**Method**: GET  
```bash
curl http://127.0.0.1:5000/players/statistics
```

### Scrape Upcoming Matches

**Endpoint**: `/upcoming/uri`  
**Method**: POST  
**Request Body**: JSON  
```json
{
    "url": "<upcoming_matches_url>"
}
```
```bash
curl -X POST -H "Content-Type: application/json" -d '{"url": "<upcoming_matches_url>"}' http://127.0.0.1:5000/upcoming/uri
```

### Get Upcoming Matches

**Endpoint**: `/upcoming/rating`  
**Method**: GET  
```bash
curl http://127.0.0.1:5000/upcoming/rating
```

### Scrape Team Statistics

**Endpoint**: `/team/uri`  
**Method**: POST  
**Request Body**: JSON  
```json
{
    "url": "<team_url>"
}
```
```bash
curl -X POST -H "Content-Type: application/json" -d '{"url": "<team_url>"}' http://127.0.0.1:5000/team/uri
```

### Get Team Statistics

**Endpoint**: `/team/rating`  
**Method**: GET  
```bash
curl http://127.0.0.1:5000/team/rating
```

### Scrape Match Data

**Endpoint**: `/matches/uri`  
**Method**: POST  
**Request Body**: JSON  
```json
{
    "url": "<match_url>"
}
```
```bash
curl -X POST -H "Content-Type: application/json" -d '{"url": "<match_url>"}' http://127.0.0.1:5000/matches/uri
```

### Get Match Data

**Endpoint**: `/matches/rating`  
**Method**: GET  
```bash
curl http://127.0.0.1:5000/matches/rating
```
