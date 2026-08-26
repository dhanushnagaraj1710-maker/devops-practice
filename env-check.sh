local_version="1.0.0"
export APP_ENV="Production"
echo "$APP_ENV"
echo "$local_version"
echo "FIles with the name env"
ls -1 | grep env
bash -c 'echo  "$local_version" "$APP_ENV"'