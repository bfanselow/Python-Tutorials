#!/bin/sh

## Don't change the order of table building since there
## are foregin-keys that must be built in order.

backup=$1
mydate=`date +%F`
file="SARS_DB-${mydate}.sql"

if [ "X${backup}" = 'Xbackup' ]; then
  echo "Backing up all tables to file [$file]..."
  mysqldump -p sars > $file
fi

echo "Dropping all tables..."
mysql -p < dropall.mysql

echo "Creating table: sars_users..."
mysql -p < sars_users.mysql

echo "Creating table: sars_groups..."
mysql -p < sars_groups.mysql

echo "Creating table: sars_user_group_map..."
mysql -p < sars_user_group_map.mysql

echo "Creating table: sars_job_input_archive..."
mysql -p < sars_job_input_archive.mysql

echo "Creating table: sars_job_input..."
mysql -p < sars_job_input.mysql

echo "Creating table: sars_scheduled_jobs..."
mysql -p < sars_scheduled_jobs.mysql

echo "Creating table: sars_triggered_jobs..."
mysql -p < sars_triggered_jobs.mysql

