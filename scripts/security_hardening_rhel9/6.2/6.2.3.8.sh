#!/usr/bin/env bash
{ 
 l_output="" l_rotate_conf="" #check for logrotate.conf file
 if [ -f /etc/logrotate.conf ]; then
 l_rotate_conf="/etc/logrotate.conf"
 elif compgen -G "/etc/logrotate.d/*.conf" 2>/dev/null; then
 for file in /etc/logrotate.d/*.conf; do
 l_rotate_conf="$file" 
 done
 elif systemctl is-active --quiet systemd-journal-upload.service; then
 echo -e "- journald is in use on system\n - recommendation is NA"
 else 
 echo -e "- logrotate is not configured"
 l_output="$l_output\n- rsyslog is in use and logrotate is not 
configured"
 fi
 if [ -z "$l_output" ]; then # Provide output from checks
 echo -e "\n- Audit Result:\n ** REVIEW **\n - $l_rotate_conf and verify logs are rotated according to site policy."
 else
 echo -e "\n- Audit Result:\n ** FAIL **\n - Reason(s) for audit failure:\n$l_output"
 fi
}
