#!/bin/bash
source /data/db/.env
mongosh <<EOF
use $MONGO_INITDB_DATABASE
db.createUser(
        {
            user: '$USER1',
            pwd: '$PASSWORD1',
            roles: [
                {
                    role: "readWrite",
                    db: "nyt_news"
                }
            ]
        }
);
db.createCollection('election');
db.createCollection('usa_election_articles');
db.createCollection('book');
db.createCollection('polarity_dataset');
db.createCollection('users');
db.users.insertOne({'user' : '$USER1','password': '$HASH_PASSWORD'});
EOF
mongoimport -d $MONGO_INITDB_DATABASE -c election --authenticationDatabase $MONGO_INITDB_DATABASE --username $USER1 --password $PASSWORD1 --type json --file data/db/data/election.json --jsonArray
mongoimport -d $MONGO_INITDB_DATABASE -c polarity_dataset --type csv --authenticationDatabase $MONGO_INITDB_DATABASE --username $USER1 --password $PASSWORD1 --file data/db/data/merge_SEN.csv --headerline
#mongoimport -d $MONGO_INITDB_DATABASE -c book --authenticationDatabase $MONGO_INITDB_DATABASE --username $USER1 --password $PASSWORD1 --type json --file data/db/data/bestsellers_with_abstract_and_genre_3350.json --jsonArray
#mongoimport -d $MONGO_INITDB_DATABASE -c usa_election_articles --authenticationDatabase $MONGO_INITDB_DATABASE --username $USER1 --password $PASSWORD1 --type json --file data/db/data/nytimes_archives_elections_articles.json --jsonArray
