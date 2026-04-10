#!/usr/bin/env bash
{
 l_output="" l_output2=""
 a_files=()
 for l_file in /etc/motd{,.d/*}; do
 if grep -Psqi -- "(\\\v|\\\r|\\\m|\\\s|\b$(grep ^ID= /etc/os-release | cut -d= -f2 | sed -e 's/"//g')\b)" "$l_file"; then
 l_output2="$l_output2\n - File: \"$l_file\" includes system information"
 else
 a_files+=("$l_file")
 fi
 done
 if [ "${#a_files[@]}" -gt 0 ]; then
 echo -e "\n- ** Please review the following files and verify their contents follow local site policy **\n"
 printf '%s\n' "${a_files[@]}"
 elif [ -z "$l_output2" ]; then
 echo -e "- ** No MOTD files with any size were found. Please verify this conforms to local site policy ** -"
 fi
 if [ -z "$l_output2" ]; then
 l_output=" - No MOTD files include system information"
 echo -e "\n- Audit Result:\n ** PASS **\n$l_output\n"
 else
 echo -e "\n- Audit Result:\n ** FAIL **\n - Reason(s) for audit failure:\n$l_output2\n"
 fi
}
