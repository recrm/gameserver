#!/bin/bash

export REACT_APP_ENV="prod"

# build udebs
rm -R /var/www/udebs/
mkdir /var/www/udebs
cp -R backend /var/www/udebs/backend
cp app.wsgi /var/www/udebs/

# build react
rm -R frontend/build
npm run build --prefix frontend
rm -R /var/www/react/
mkdir /var/www/react
cp -R frontend/build/. /var/www/react

# restart apache2
service apache2 restart
