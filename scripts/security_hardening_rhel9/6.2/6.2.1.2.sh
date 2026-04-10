#!/usr/bin/env bash
{
 l_output="" file_path=""
 # Check for the existence of an override file
 if [ -f /etc/tmpfiles.d/systemd.conf ]; then
 file_path="/etc/tmpfiles.d/systemd.conf"
 elif [ -f /usr/lib/tmpfiles.d/systemd.conf ]; then
 file_path="/usr/lib/tmpfiles.d/systemd.conf"
 fi 
 if [ -n "$file_path" ]; then # Ensure a file path is found
 higher_permissions_found=false # Initialize a flag to check if higher permissions are found
 # Read the file line by line and check for permissions higher than 0640
 while IFS= read -r line; do
 if echo "$line" | grep -Piq '^\s*[a-z]+\s+[^\s]+\s+0*([6-7][4-7][1-7]|7[0-7][0-7])\s+'; then
 higher_permissions_found=true
 break
 fi
 done < "$file_path"
 if $higher_permissions_found; then
 echo -e "\n - permissions other than 0640 found in $file_path"
l_output="$l_output\n - Inspect $file_path"
 else
 echo -e "All permissions inside $file_path are 0640 or more restrictive."
 fi
 fi
 if [ -z "$l_output" ]; then # Provide output from checks
 echo -e "\n- Audit Result:\n ** PASS **\n$file_path exists and has correct permissions set\n"
 else
 echo -e "\n- Audit Result:\n ** REVIEW **\n$l_output\n - Review permissions to ensure they are set IAW site policy"
 fi 
}