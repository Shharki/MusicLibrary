# MusicLibrary 
Final_project_SDA_2025 

- A complete full-stack application in Django for managing your personal music archive. 
- Users can catalog songs, albums, artists, and genres; upload album artwork; 
  and conveniently manage the library through a user-friendly web interface with login 
  and permissions.

Backend             Django 5, Python 3.13 
Database            SQLite 3 (development)
Frontend            Django Templates, Bootstrap 5, HTMX
Authentication      Django auth + accounts 
Development & CI    Git, GitHub Actions (lint + tests), PyCharm

## PROJECT Functionality 
-[] 1 songs 
    -[] list (alphabetical)  
-[] 2 songs - details 
    -[] original name
    -[] cz name
    -[] genre
    -[] country
    -[] singer/group
    -[] composer
    -[] length
    -[] year
    -[] description
-[] 3 songs - other
    -[] evaluation
    -[] awards
    -[] picture - album cover
    -[] song_text
    -[] streaming
    -[] song sample
-[] 4 songs - filter 
    -[] by genre
    -[] by country 
    -[] by year 
    -[] by album 
    -[] by artist
    -[] by evaluation
    -[] by awards
-[] 5 artist - list (alphabetical)
-[] 6 artist - details (singer/composer/group)
    -[] name
    -[] surname
    -[] artist name
    -[] country
    -[] date of birth
    -[] date of death
    -[] songs, which are interpreted by singer/group 
    -[] songs, personally composed by composer 
    -[] albums, created by composer
    -[] biography
-[] 7 artist - other 
    -[] evaluation
    -[] awards
    -[] pictures
-[] 8 album 
    -[] 8.1 list (alphabetical)
    -[] 8.2 details
        -[] original name
        -[] cz name
        -[] genre
        -[] country
        -[] singer
        -[] composer
        -[] length
        -[] year of establishment
        -[] description
-[] 9 country
    -[] 9.1 list (alphabetical)
    -[] 9.2 details
-[] 10 genre
    -[] 10.1 list (abecedně)
    -[] 10.2 details
-[] 11 creating records (C)
    -[] 11.1 song
    -[] 11.2 artist
    -[] 11.3 album
    -[] 11.4 country
    -[] 11.5 genre
-[] 12 updating records (U)
    -[] 12.1 song
    -[] 12.2 artist
    -[] 12.3 album
    -[] 12.4 country
    -[] 12.5 genre
-[] 13 deleting records (D)
    -[] 13.1 song
    -[] 13.2 artis
    -[] 13.3 album
    -[] 13.4 country
    -[] 13.5 genre
-[] 14 autenthication 
    -[] 14.1 display the logged in user
    -[] 14.2 user display limitation
    -[] 14.3 superuser display limitation
    -[] 14.4 login
    -[] 14.5 logout-password change - reset
    -[] 14.6 registration - profile
-[] 15 authorization
    -[] 15.1 song
    -[] 15.2 artis
    -[] 15.3 album
    -[] 15.4 country
    -[] 15.5 genre

### Day 2
- Further setting of the MusicLibrary skeleton 
- Database creation 
- sqlite3 -> added to .gitignore + connected to PyCharm 
- Project structure 

#### Databáze
#![ER diagram]
- [x] Genre
  - [x] name (String)
- [] Country
  - [] name (String)
- [] Artist (Man = Singer, Composer)
  - [] name (String)
  - [] surname (String)
  - [] artistic_name (String)
  - [] date_of_birth (Date)
  - [] date_of_death (Date)
  - [] country (FK -> Country)
  - [] biography (String)
- [] Group 
  - [] name (String)
  - [] description (String) 
  - [] date_of_establish (Date)
  - [] termination (Date)
  - [] artists (n:m -> Artist)
- [] Song
  - [] title (String)
  - [] genres (n:m -> Genre)
  - [] performers (n:m -> Artist)
  - [] groups (n:m -> Group)
  - [] composers (n:m -> Artist)
  - [] length (Integer -> length in seconds)
  - [] year (Integer -> year of issue)
  - [] description (String)
  - [] lyrics (String)
- [] Album 
  - [] title (String)
  - [] songs (n:m -> Song)
  - [] released_year (Integer -> year of issue)
  - [] description (String)
  - [] front_cover (ImageField) 
  - [] back_cover (ImageField) 
  






   
    
    
