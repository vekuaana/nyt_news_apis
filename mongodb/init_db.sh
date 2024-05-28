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
EOF
mongoimport -d $MONGO_INITDB_DATABASE -c election --type csv --authenticationDatabase $MONGO_INITDB_DATABASE --username $USER1 --password $PASSWORD1 --file data/db/data/elections_americaines_from_1851.csv --headerline
