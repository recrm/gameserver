export REACT_APP_ENV="prod"

# build udebs
rm -R /var/www/udebs/
mkdir /var/www/udebs
cp -R backend /var/www/udebs/backend
cp app.wsgi /var/www/udebs/

# build react
sudo rm -R frontend/build
npm run build --prefix frontend
sudo rm -R /var/www/react/
sudo mkdir /var/www/react
sudo cp -R frontend/build/. /var/www/react

# restart apache2
service apache2 restart
