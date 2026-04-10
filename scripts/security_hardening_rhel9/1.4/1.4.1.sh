#!/usr/bin/env bash
{
 l_grub_password_file="$(find /boot -type f -name 'user.cfg' ! -empty)"
 if [ -f "$l_grub_password_file" ]; then
 awk -F. '/^\s*GRUB2_PASSWORD=\S+/ {print $1"."$2"."$3}' 
"$l_grub_password_file"
 fi
}
