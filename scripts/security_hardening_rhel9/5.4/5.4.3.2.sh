#!/usr/bin/env bash
{
 a_output=(); a_output2=(); l_tmout_set="900"
 f_tmout_read_chk()
 {
 a_out=(); a_out2=()
 l_tmout_readonly="$(grep -P -- '^\h*(typeset\h\-xr\hTMOUT=\d+|([^#\n\r]+)?\breadonly\h+TMOUT\b)' "$l_file")"
 l_tmout_export="$(grep -P -- '^\h*(typeset\h\-xr\hTMOUT=\d+|([^#\n\r]+)?\bexport\b([^#\n\r]+\b)?TMOUT\b)' "$l_file")"
 if [ -n "$l_tmout_readonly" ]; then
 a_out+=(" - Readonly is set as: \"$l_tmout_readonly\" in: \"$l_file\"")
 else
 a_out2+=(" - Readonly is not set in: \"$l_file\"")
 fi
 if [ -n "$l_tmout_export" ]; then
 a_out+=(" - Export is set as: \"$l_tmout_export\" in: \"$l_file\"")
 else
 a_out2+=(" - Export is not set in: \"$l_file\"")
 fi 
 }
 while IFS= read -r l_file; do
 l_tmout_value="$(grep -Po -- '^([^#\n\r]+)?\bTMOUT=\d+\b' "$l_file" | awk -F= '{print $2}')"
 f_tmout_read_chk
 if [ -n "$l_tmout_value" ]; then
 if [[ "$l_tmout_value" -le "$l_tmout_set" && "$l_tmout_value" -gt "0" ]]; then
 a_output+=(" - TMOUT is set to: \"$l_tmout_value\" in: \"$l_file\"")
 [ "${#a_out[@]}" -gt 0 ] && a_output+=("${a_out[@]}")
 [ "${#a_out2[@]}" -gt 0 ] && a_output2+=("${a_out[@]}")
 fi
 if [[ "$l_tmout_value" -gt "$l_tmout_set" || "$l_tmout_value" -le "0" ]]; then
 a_output2+=(" - TMOUT is incorrectly set to: \"$l_tmout_value\" in: \"$l_file\"")
 [ "${#a_out[@]}" -gt 0 ] && a_output2+=(" ** Incorrect TMOUT value **" 
"${a_out[@]}")
 [ "${#a_out2[@]}" -gt 0 ] && a_output2+=("${a_out2[@]}")
 fi
 else
 [ "${#a_out[@]}" -gt 0 ] && a_output2+=(" - TMOUT is not set" "${a_out[@]}")
 [ "${#a_out2[@]}" -gt 0 ] && a_output2+=(" - TMOUT is not set" "${a_out2[@]}")
 fi
 done < <(grep -Pls -- '^([^#\n\r]+)?\bTMOUT\b' /etc/*bashrc /etc/profile /etc/profile.d/*.sh)
 [[ "${#a_output[@]}" -le 0 && "${#a_output2[@]}" -le 0 ]] && a_output2+=(" - TMOUT is not configured")
 if [ "${#a_output2[@]}" -le 0 ]; then
 printf '%s\n' "" "- Audit Result:" " ** PASS **" "${a_output[@]}"
 else
 printf '%s\n' "" "- Audit Result:" " ** FAIL **" " * Reasons for audit failure *" "${a_output2[@]}" ""
 [ "${#a_output[@]}" -gt 0 ] && printf '%s\n' "- Correctly set:" "${a_output[@]}"
 fi
}
