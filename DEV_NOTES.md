<!-- 
This is a shared space for the development team to write down ideas, planned features,
technical notes, and open questions related to the project.

Use this file to:
- Keep track of feature proposals and their status
- Document implementation details or decisions
- Share TODOs or tasks not yet reflected in code
- Record useful links or references
- Communicate with teammates asynchronously

Feel free to update, edit, and expand this file as the project evolves.
-->

14.07.2025
#### TODO 
- added 'Language' model
- changed 'Artist' into 'Contributor' model
- changed 'Group' into 'MusicGroup' model
- added 'ContributorPreviousName' model
- added 'ContributorRole' model 
- added 'MusicGroupMembership' model 
- added 'Song' model 


#### DATABASE MODELS
#![ER diagram]
-[ ] Genre
  -[ ] name (String)
-[ ] Country
  -[ ] name (String)
-[ ] Contributor
  -[ ] first_name (String)
  -[ ] middle_name (String)
  -[ ] last_name (String)
  -[ ] stage_name (String)
  -[ ] date_of_birth (Date)
  -[ ] date_of_death (Date)
  -[ ] country (FK -> Country)
  -[ ] bio (Text)
-[ ] ContributorPreviousName
  -[ ] contributor (FK -> Contributor)
  -[ ] first_name (String)
  -[ ] middle_name (String)
  -[ ] last_name (String)
-[ ] ContributorRole
  -[ ] name (String)
-[ ] MusicGroup 
  -[ ] name (String)
  -[ ] bio (Text)
  -[ ] founded (Date)
  -[ ] disbanded (Date)
-[ ] MusicGroupMembership 
  -[ ] contributor (FK -> Contributor)
  -[ ] music_group (FK -> MusicGroup)
  -[ ] role (n:m -> ContributorRole)
  -[ ] from_date (Date)
  -[ ] to_date (Date)
-[ ] Song
  -[ ] title (String)
  -[ ] genres (n:m -> Genre)
  -[ ] duration (Integer -> length in seconds)
  -[ ] released_year (Integer -> year of issue)
  -[ ] summary (String)
  -[ ] lyrics (String)
  -[ ] language (FK -> language)
-[ ] SongPerformance 
  -[ ] song (FK -> Song)
  -[ ] contributor  (FK -> Contributor)
  -[ ] music_group  (FK -> MusicGroup)
  -[ ] role  (FK -> ContributorRole)
-[ ] Album 
  -[ ] title (String)
  -[ ] songs (n:m -> Song)
  -[ ] released_year (Integer)
  -[ ] summary (String)
  -[ ] cover_image (ImageField)
  -[ ] duration (Integer -> calculated Songs)
  -[ ] performers (list -> Song)
  -[ ] Genre (list -> Song)
-[ ] Language 
  -[ ] name (String)

The difference between the database and its relations is that relations represent
the current state of how tables are connected.
The main purpose of using them is to gain a clearer overview of the project's structure
and to prepare for future features such as data filtering based on these relationships.

#neaktuální, doplnit z DATABASE MODELS
# DATABASE RELATIONS 
- [x] Genre
  - [x] name (String)
  - ... genres (genres)
- [x] Country
  - [x] name (String)
  - ... artist 
- [x] Artist (Man = Singer, Composer)
  - [x] name (String)
  - [x] surname (String)
  - [x] stage_name (String)
  - [ ] best_known_for (role/role in group)
  - [x] date_of_birth (Date)
  - [x] date_of_death (Date)
  - [x] country (FK -> Country)
  - [x] biography (String)
  - ... group 
  - ... song (performers)
  - ... song (composers)
- [x] Group 
  - [x] name (String)
  - [x] description (String)
  - [x] date_of_establish (Date)
  - [x] termination (Date)
  - [x] artists (n:m -> Artist)
  - ... song
  - ... album
- [ ] Song
  - [ ] title (String)
  - [ ] genres (n:m -> Genre)
  - [ ] performers (n:m -> Artist)
  - [ ] groups (n:m -> Group)
  - [ ] composers (n:m -> Artist)
  - [ ] length (Integer -> length in seconds)
  - [ ] year (Integer -> year of issue)
  - [ ] description (String)
  - [ ] lyrics (String)
  - [ ] language (n:m -> Language)
  - ... album
- [ ] Album 
  - [ ] title (String)
  - [ ] ... songs (n:m -> Songs, ordered list)
  - [ ] released_year (Integer -> year of issue)
  - [ ] description (String)
  - [ ] cover (ImageField)
  - [ ] ... length (Integer -> length in seconds, calculated from songs)
  - [ ] ... performers (List of artists, iterated from songs)
  - [ ] ... groups (List of groups, iterated from songs)
  - [ ] ... Genres (List of genres, iterated from songs)
  - [ ] ... language (List of languages, iterated from songs)
- [ ] Language
  - [ ] name
  - ... song
  - ... album
- [ ] Role
  - [ ] name
- [ ] SongContribution
  - ... FK song -> song
  - ... FK artist -> artist
  - ... FK role -> role


chystaná úprava README
#### DATABASE MODELS
#![ER diagram]
-[x] Genre
  -[x] name (String)
-[x] Country
  -[x] name (String)
-[x] Artist (Man = Singer, Composer)
  -[x] name (String)
  -[x] surname (String)
  -[x] artistic_name (String)
  -[x] date_of_birth (Date)
  -[x] date_of_death (Date)
  -[x] country (FK -> Country)
  -[x] biography (String)
-[x] Group 
  -[x] name (String)
  -[x] description (String)
  -[x] date_of_establish (Date)
  -[x] termination (Date)
  -[x] artists (n:m -> Artist)
-[ ] Song
  -[ ] title (String)
  -[ ] genres (n:m -> Genre)
  -[ ] performers (n:m -> Artist)
  -[ ] groups (n:m -> Group)
  -[ ] composers (n:m -> Artist)
  -[ ] length (Integer -> length in seconds)
  -[ ] year (Integer -> year of issue)
  -[ ] description (String)
  -[ ] lyrics (String)
  -[ ] language ()
-[ ] Album 
  -[ ] title (String)
  -[ ] songs (n:m -> Song)
  -[ ] released_year (Integer -> year of issue)
  -[ ] description (String)
  -[ ] front_cover (ImageField)
  -[ ] length (Integer -> length in seconds)
  -[ ] Artist ()
  -[ ] Genre ()
  