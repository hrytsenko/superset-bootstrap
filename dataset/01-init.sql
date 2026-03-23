\connect imdb;

CREATE TABLE IF NOT EXISTS movies (
  rank integer not null,
  name text not null,
  year integer not null,
  rating numeric (3,2) not null,
  genre text not null,
  certificate text not null
);

TRUNCATE movies;

copy movies(
    rank,
    name,
    year,
    rating,
    genre,
    certificate)
  FROM '/docker-entrypoint-initdb.d/movies.csv'
  WITH (FORMAT csv, HEADER true);
