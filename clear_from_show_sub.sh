#!/bin/bash

echo "----- Running show subscriber at $(date) -----"; echo
mapfile -t CLEAR_CMD < <(cli show subscribers apn whsia.telus.com idle-time greater-than 3600 | awk '{print "clear subscriber msid " $3}')

#printf "%s\n" "${CLEAR_CMD[@]}"

# Loop through and execute each command
for (( i=0; i<${#CLEAR_CMD[@]}; i++ )); do
  cmd="${CLEAR_CMD[$i]}"
  echo "Running command: $cmd"
  echo
  cli "$cmd"
  echo
  sleep 0.5
done