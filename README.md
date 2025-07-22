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
- [ ] 1. Songs – listing
    - [x] Alphabetical list
    - [ ] Filtering by: genre, country, language, year, album, performer, ratings
- [ ] 2. Songs – song detail
    - [ ] Title
    - [ ] Genres (n:m -> Genre)
    - [ ] Duration (in seconds)
    - [ ] Release year
    - [ ] Language
    - [ ] Lyrics
    - [ ] Summary / note
    - [ ] Performers: individuals or groups (from SongPerformance)
    - [ ] Performer roles (singer, composer, lyricist, etc.)
- [ ] 3. Songs – other
    - [ ] Album image (via Album relation)
    - [ ] Rating (user-based)
    - [ ] Audio sample / streaming link
- [ ] 4. Contributors (Artists) – listing and detail
    - [ ] Alphabetical list
    - [ ] Contributor detail (singer, composer...)
        - [ ] First name, last name, stage name
        - [ ] Date of birth and death
        - [ ] Country of origin
        - [ ] Biography
        - [ ] Previous names
        - [ ] Songs performed (from SongPerformance)
        - [ ] Groups they were members of (MusicGroupMembership)
        - [ ] Picture 
- [ ] 5. Music Groups – listing and detail
    - [ ] Alphabetical list
    - [ ] Group detail
        - [ ] Name, description
        - [ ] Founded / disbanded year
        - [ ] Members, roles, active periods
        - [ ] Songs they performed in
- [ ] 6. Albums – listing and detail
    - [ ] Alphabetical album list
    - [ ] Album detail
        - [ ] Title
        - [ ] Release year
        - [ ] Summary
        - [ ] List of songs (with performers, durations, etc.)
        - [ ] Total album duration (via get_duration())
        - [ ] Genres, languages, performers (derived from songs)
- [ ] 7. Countries – listing and detail
    - [ ] Alphabetical list
    - [ ] Detail (list of contributors from the given country)
- [ ] 8. Genres – listing and detail
    - [ ] Alphabetical list
    - [ ] Detail (list of songs of the given genre)
- [ ] 9. CRUD operations (via admin or views):
    - [ ] Create
        - [ ] Songs, Contributors, Albums, Countries, Genres
    - [ ] Update
        - [ ] Songs, Contributors, Albums, Countries, Genres
    - [ ] Delete
        - [ ] Songs, Contributors, Albums, Countries, Genres
- [ ] 10. Authentication and Users
    - [ ] Display of logged-in user
    - [ ] Access restrictions by user type (regular vs. admin)
    - [ ] Login / Logout / Password reset
    - [ ] Registration, user profile
- [ ] 11. Authorization
    - [ ] Permissions for CRUD operations
    - [ ] Protection of specific views (e.g. admin only)

#### Databáze
![ER diagram](./files/ER_diagram_v2.png)
- [x] Genre  
  - [x] name (String)
- [x] Country  
  - [x] name (String)
- [x] Language  
  - [x] name (String)
- [x] Contributor  
  - [x] first_name (String)  
  - [x] middle_name (String)  
  - [x] last_name (String)  
  - [x] stage_name (String)  
  - [x] date_of_birth (Date)  
  - [x] date_of_death (Date)  
  - [x] country (FK -> Country)  
  - [x] bio (Text)
- [x] ContributorPreviousName  
  - [x] contributor (FK -> Contributor)  
  - [x] first_name (String)  
  - [x] middle_name (String)  
  - [x] last_name (String)
- [x] ContributorRole  
  - [x] name (String)
- [x] MusicGroupRole  
  - [x] name (String)
- [x] MusicGroup  
  - [x] name (String)  
  - [x] bio (Text)  
  - [x] founded (Date)  
  - [x] disbanded (Date)
- [x] MusicGroupMembership  
  - [x] contributor (FK -> Contributor)  
  - [x] music_group (FK -> MusicGroup)  
  - [x] contributor_role (n:m -> ContributorRole)  
  - [x] from_date (Date)  
  - [x] to_date (Date)
- [x] Song  
  - [x] title (String)  
  - [x] genres (n:m -> Genre)  
  - [x] duration (Integer, in seconds)  
  - [x] released_year (Integer)  
  - [x] summary (Text)  
  - [x] lyrics (Text)  
  - [x] language (FK -> Language)
- [x] SongPerformance  
  - [x] song (FK -> Song)  
  - [x] contributor (FK -> Contributor)  
  - [x] contributor_role (FK -> ContributorRole)  
  - [x] music_group (FK -> MusicGroup) 
  - [x] music_group_role (FK -> MusicGroupRole)
- [x] Album  
  - [x] title (String)  
  - [x] songs (n:m -> Song)  
  - [x] released_year (Integer)  
  - [x] summary (Text)  






   
    
    
