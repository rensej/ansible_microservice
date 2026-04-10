#!/usr/bin/env bash
{
 l_output="" l_output2=""
 l_perm_mask="0177"
 if [ -e "/etc/audit/auditd.conf" ]; then
 l_audit_log_directory="$(dirname "$(awk -F= '/^\s*log_file\s*/{print $2}' /etc/audit/auditd.conf | xargs)")"
 if [ -d "$l_audit_log_directory" ]; then
 l_maxperm="$(printf '%o' $(( 0777 & ~$l_perm_mask )) )"
 while IFS= read -r -d $'\0' l_file; do
 l_output2="$l_output2\n - File: \"$l_file\" is mode: \"$(stat -Lc '%#a' "$l_file")\"\n (should be mode: \"$l_maxperm\" or more restrictive)\n" 
 done < <(find "$l_audit_log_directory" -maxdepth 1 -type f -perm /"$l_perm_mask" -print0)
 else
 l_output2="$l_output2\n - Log file directory not set in \"/etc/audit/auditd.conf\" please set log file directory"
 fi
 else
 l_output2="$l_output2\n - File: \"/etc/audit/auditd.conf\" not found.\n - ** Verify auditd is installed **"
 fi
 if [ -z "$l_output2" ]; then
 l_output="$l_output\n - All files in \"$l_audit_log_directory\" are mode: \"$l_maxperm\" or more restrictive"
 echo -e "\n- Audit Result:\n ** PASS **\n - * Correctly configured * 
:$l_output"
 else
 echo -e "\n- Audit Result:\n ** FAIL **\n - * Reasons for audit failure * :$l_output2\n"
 fi
}
